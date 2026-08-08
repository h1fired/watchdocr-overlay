#version 440

layout(location = 0) in vec2 qt_TexCoord0;
layout(location = 0) out vec4 fragColor;

layout(std140, binding = 0) uniform buf {
    mat4  qt_Matrix;
    float qt_Opacity;
    vec2  q0;         // frame UV of box-local (0,0) — TL
    vec2  q1;         // local (1,0)                 — TR
    vec2  q2;         // local (1,1)                 — BR
    vec2  q3;         // local (0,1)                 — BL
    float tolerance;  // luminance residual above which a sample is rejected
    float seam;       // blend-to-original band at the box edge, local units
    float gradient;   // 0 = force flat fill, 1 = full linear gradient
} ubuf;

layout(binding = 1) uniform sampler2D source;   // frameCapture — FULL frame

const int   EDGE_SAMPLES = 8;   // per edge, per ring
const int   RINGS        = 2;
const int   MIN_SAMPLES  = 8;
const vec3  LUMA = vec3(0.299, 0.587, 0.114);

// Projective map: unit square -> quad. Extrapolates correctly outside [0,1],
// which is how the border taps reach past the box edges.
vec2 mapQuad(vec2 p)
{
    vec2 d1 = ubuf.q1 - ubuf.q2;
    vec2 d2 = ubuf.q3 - ubuf.q2;
    vec2 d3 = ubuf.q0 - ubuf.q1 + ubuf.q2 - ubuf.q3;

    float den = d1.x * d2.y - d2.x * d1.y;

    float g = 0.0;
    float h = 0.0;
    if (abs(den) > 1e-9) {
        g = (d3.x * d2.y - d2.x * d3.y) / den;
        h = (d1.x * d3.y - d3.x * d1.y) / den;
    }

    vec2 A = ubuf.q1 - ubuf.q0 + g * ubuf.q1;
    vec2 B = ubuf.q3 - ubuf.q0 + h * ubuf.q3;
    vec2 C = ubuf.q0;

    float w = g * p.x + h * p.y + 1.0;
    if (abs(w) < 1e-6) w = 1e-6;

    return (A * p.x + B * p.y + C) / w;
}

vec4 fetch(vec2 local)
{
    return texture(source, clamp(mapQuad(local), vec2(0.0), vec2(1.0)));
}

// Border ring position: ring 1..RINGS, edge 0..3, index 0..EDGE_SAMPLES-1.
vec2 ringPoint(int ring, int e, int i)
{
    vec2  off = vec2(0, 0);
    float f   = (float(i) + 0.5) / float(EDGE_SAMPLES);

    if (e == 0) return vec2(mix(-off.x, 1.0 + off.x, f), -off.y);
    if (e == 1) return vec2(mix(-off.x, 1.0 + off.x, f), 1.0 + off.y);
    if (e == 2) return vec2(-off.x,      mix(-off.y, 1.0 + off.y, f));
    return             vec2(1.0 + off.x, mix(-off.y, 1.0 + off.y, f));
}

// Solve the 3x3 symmetric normal equations for  color = a + b*u + c*v.
// Written out by cofactors rather than inverse(), which GLSL ES 100 / 120 lack.
bool solvePlane(float n, float Su, float Sv, float Suu, float Suv, float Svv,
                vec4 Sc, vec4 Suc, vec4 Svc,
                out vec4 a, out vec4 b, out vec4 c)
{
    float k00 = Suu * Svv - Suv * Suv;
    float k01 = Sv  * Suv - Su  * Svv;
    float k02 = Su  * Suv - Sv  * Suu;

    float det = n * k00 + Su * k01 + Sv * k02;

    a = vec4(0.0);
    b = vec4(0.0);
    c = vec4(0.0);

    if (abs(det) < 1e-12) return false;

    float inv = 1.0 / det;

    float i00 = k00 * inv;
    float i01 = k01 * inv;
    float i02 = k02 * inv;
    float i11 = (n * Svv - Sv * Sv) * inv;
    float i12 = (Su * Sv - n * Suv) * inv;
    float i22 = (n * Suu - Su * Su) * inv;

    a = i00 * Sc + i01 * Suc + i02 * Svc;
    b = i01 * Sc + i11 * Suc + i12 * Svc;
    c = i02 * Sc + i12 * Suc + i22 * Svc;

    return true;
}

void main()
{
    vec2 p = qt_TexCoord0;          // box-local, 0..1
    vec2 puv = p - vec2(0.5);       // centred, better conditioned for the fit

    vec4 a = vec4(0.0);
    vec4 b = vec4(0.0);
    vec4 c = vec4(0.0);

    vec4  flatSum = vec4(0.0);
    float flatN   = 0.0;

    vec4 lo = vec4(1.0);
    vec4 hi = vec4(0.0);

    bool haveFit = false;

    // Pass 0 fits every border sample. Pass 1 refits, discarding samples whose
    // luminance disagrees with pass 0 by more than `tolerance` — that is the
    // leftover glyph halo, and dropping it is what keeps text out of the fill.
    for (int pass = 0; pass < 2; ++pass) {

        float n   = 0.0;
        float Su  = 0.0;
        float Sv  = 0.0;
        float Suu = 0.0;
        float Suv = 0.0;
        float Svv = 0.0;

        vec4 Sc  = vec4(0.0);
        vec4 Suc = vec4(0.0);
        vec4 Svc = vec4(0.0);

        vec4 passLo = vec4(1.0);
        vec4 passHi = vec4(0.0);

        vec4  passFlatSum = vec4(0.0);
        float passFlatN   = 0.0;

        for (int ring = 1; ring <= RINGS; ++ring) {
            for (int e = 0; e < 4; ++e) {
                for (int i = 0; i < EDGE_SAMPLES; ++i) {

                    vec2 local = ringPoint(ring, e, i);
                    vec4 s     = fetch(local);

                    vec2 uv = local - vec2(0.5);

                    if (pass == 1 && haveFit) {
                        vec4  pred = a + b * uv.x + c * uv.y;
                        float d    = abs(dot(s.rgb, LUMA) - dot(pred.rgb, LUMA));
                        if (d > ubuf.tolerance) continue;
                    }

                    n   += 1.0;
                    Su  += uv.x;
                    Sv  += uv.y;
                    Suu += uv.x * uv.x;
                    Suv += uv.x * uv.y;
                    Svv += uv.y * uv.y;

                    Sc  += s;
                    Suc += s * uv.x;
                    Svc += s * uv.y;

                    passLo = min(passLo, s);
                    passHi = max(passHi, s);

                    passFlatSum += s;
                    passFlatN   += 1.0;
                }
            }
        }

        // Too few survivors means the rejection ate everything — keep pass 0.
        if (pass == 1 && n < float(MIN_SAMPLES)) break;

        vec4 na, nb, nc;
        if (solvePlane(n, Su, Sv, Suu, Suv, Svv, Sc, Suc, Svc, na, nb, nc)) {
            a = na;
            b = nb;
            c = nc;
            haveFit = true;
        }

        lo      = passLo;
        hi      = passHi;
        flatSum = passFlatSum;
        flatN   = passFlatN;
    }

    vec4 flatFill = flatN > 0.0 ? flatSum / flatN : fetch(p);

    vec4 filled;
    if (haveFit) {
        // `gradient` dials the linear terms down toward a flat fill.
        filled = a + (b * puv.x + c * puv.y) * ubuf.gradient;
        // A plane can extrapolate past anything actually observed on the
        // border; clamping to the sampled range keeps it physically plausible.
        filled = clamp(filled, lo, hi);
    } else {
        filled = flatFill;
    }

    // Fade to the real image in a thin band at the box edge so there is no
    // step where the fill meets the untouched surroundings.
    float edge = min(min(p.x, 1.0 - p.x), min(p.y, 1.0 - p.y));
    float k    = smoothstep(0.0, max(ubuf.seam, 1e-4), edge);

    vec4 result = mix(fetch(p), filled, k);

    fragColor = clamp(result, vec4(0.0), vec4(1.0)) * ubuf.qt_Opacity;
}