#version 440

layout(location = 0) in vec2 qt_TexCoord0;
layout(location = 0) out vec4 fragColor;

layout(std140, binding = 0) uniform buf {
    mat4 qt_Matrix;
    float qt_Opacity;
    vec2 pixelSize;   // 1.0 / texture resolution (pass from QML)
} ubuf;

layout(binding = 1) uniform sampler2D source;

const int RING_SAMPLES = 16;
const float RADIUS = 12.0; // in pixels, tune to text size

void main() {
    vec4 samples[RING_SAMPLES];

    for (int i = 0; i < RING_SAMPLES; i++) {
        float angle = (float(i) / float(RING_SAMPLES)) * 6.2831853;
        vec2 offset = vec2(cos(angle), sin(angle)) * RADIUS * ubuf.pixelSize;
        vec2 uv = clamp(qt_TexCoord0 + offset, vec2(0.01), vec2(0.99));
        samples[i] = texture(source, uv);
    }

    // Trimmed mean: drop the brightest and darkest outliers (likely text),
    // average the rest.
    float lum[RING_SAMPLES];
    for (int i = 0; i < RING_SAMPLES; i++) {
        lum[i] = dot(samples[i].rgb, vec3(0.299, 0.587, 0.114));
    }

    // simple bubble sort by luminance (RING_SAMPLES is small, fine on GPU)
    vec4 sorted[RING_SAMPLES];
    for (int i = 0; i < RING_SAMPLES; i++) sorted[i] = samples[i];
    for (int i = 0; i < RING_SAMPLES - 1; i++) {
        for (int j = 0; j < RING_SAMPLES - 1 - i; j++) {
            float l1 = dot(sorted[j].rgb, vec3(0.299, 0.587, 0.114));
            float l2 = dot(sorted[j+1].rgb, vec3(0.299, 0.587, 0.114));
            if (l1 > l2) {
                vec4 tmp = sorted[j];
                sorted[j] = sorted[j+1];
                sorted[j+1] = tmp;
            }
        }
    }

    // trim top/bottom 25% (outliers), average the middle 50%
    int trim = RING_SAMPLES / 4;
    vec4 sum = vec4(0.0);
    int count = 0;
    for (int i = trim; i < RING_SAMPLES - trim; i++) {
        sum += sorted[i];
        count++;
    }

    fragColor = (sum / float(count)) * ubuf.qt_Opacity;
}