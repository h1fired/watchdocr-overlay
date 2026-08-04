#version 440

layout(location = 0) in vec2 qt_TexCoord0;
layout(location = 0) out vec4 fragColor;

layout(std140, binding = 0) uniform buf {
    mat4 qt_Matrix;
    float qt_Opacity;
};

layout(binding = 1) uniform sampler2D background; // full-res box area texture, NOT 1x1
layout(binding = 2) uniform sampler2D textMask;    // rendered text label (alpha = glyph coverage)

const int GRID = 8;      // GRID x GRID samples = 64 total samples
const int LEVELS = 4;    // quantize each channel to 4 levels -> 64 buckets
const int NUM_BUCKETS = LEVELS * LEVELS * LEVELS;

int bucketIndex(vec3 c) {
    ivec3 q = ivec3(clamp(c, 0.0, 0.999) * float(LEVELS));
    return q.x + q.y * LEVELS + q.z * LEVELS * LEVELS;
}

vec3 bucketColor(int idx) {
    int r = idx % LEVELS;
    int g = (idx / LEVELS) % LEVELS;
    int b = idx / (LEVELS * LEVELS);
    return (vec3(r, g, b) + 0.5) / float(LEVELS);
}

vec3 dominantColor() {
    int counts[NUM_BUCKETS];
    for (int i = 0; i < NUM_BUCKETS; i++) counts[i] = 0;

    for (int y = 0; y < GRID; y++) {
        for (int x = 0; x < GRID; x++) {
            vec2 uv = (vec2(x, y) + 0.5) / float(GRID);
            vec4 s = texture(background, uv);
            vec3 c = s.a > 0.001 ? s.rgb / s.a : s.rgb;
            counts[bucketIndex(c)] += 1;
        }
    }

    int bestIdx = 0;
    int bestCount = 0;
    for (int i = 0; i < NUM_BUCKETS; i++) {
        if (counts[i] > bestCount) {
            bestCount = counts[i];
            bestIdx = i;
        }
    }

    return bucketColor(bestIdx);
}

// WCAG relative luminance (approx, assumes linearized-enough input)
float luminance(vec3 c) {
    return dot(c, vec3(0.2126, 0.7152, 0.0722));
}

void main() {
    vec3 bg = dominantColor();

    // pick black or white text, whichever contrasts more with bg
    float lum = luminance(bg);
    vec3 textColor = lum > 0.5 ? vec3(0.0) : vec3(1.0);

    float textAlpha = texture(textMask, qt_TexCoord0).a;

    // only draw the glyphs; everywhere else stays transparent
    fragColor = vec4(textColor * textAlpha, textAlpha) * qt_Opacity;
}