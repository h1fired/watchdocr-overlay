#version 440

layout(location = 0) in vec2 qt_TexCoord0;
layout(location = 0) out vec4 fragColor;

layout(std140, binding = 0) uniform buf {
    mat4 qt_Matrix;
    float qt_Opacity;
};

layout(binding = 1) uniform sampler2D background;
layout(binding = 2) uniform sampler2D textMask;

void main() {
    vec4 bgSample = texture(background, qt_TexCoord0);
    vec3 bgColor = bgSample.a > 0.001 ? bgSample.rgb / bgSample.a : bgSample.rgb;

    float luminance = dot(bgColor, vec3(0.299, 0.587, 0.114));

    // invert around 0.5, then push outward so extremes reach pure black/white
    float inverted = 1.0 - luminance;
    float textValue = clamp((inverted - 0.5) * 15.2 + 0.5, 0.0, 1.0);

    float textAlpha = texture(textMask, qt_TexCoord0).a;
    fragColor = vec4(vec3(textValue) * textAlpha, textAlpha) * qt_Opacity;
}
