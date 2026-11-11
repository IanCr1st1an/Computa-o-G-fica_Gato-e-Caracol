#version 330 core
in vec3 vP;
in vec3 vN;
in vec2 vU;
in vec4 vL;
out vec4 F;

uniform vec3  uC;        // cor do material
uniform float uSpec;     // intensidade do brilho especular
uniform float uShin;     // expoente especular (quanto maior, mais concentrado)
uniform int   uHasT;     // 1 = usa textura
uniform float uTile;     // repetição da textura
uniform sampler2D uT;        // textura de imagem (unidade 0)
uniform sampler2D uShadow;   // mapa de profundidade da luz (unidade 1)
uniform vec3  uLdir;     // direção da luz direcional (para onde ela aponta)
uniform vec3  uE;        // posição da câmera

// Fração do pixel que está em sombra (0 = iluminado, 1 = sombra), com PCF 3x3.
float shadow(vec3 n, vec3 l) {
    vec3 p = vL.xyz / vL.w * 0.5 + 0.5;               // [-1,1] -> [0,1]: UV no mapa e profundidade
    if (p.z > 1.0) return 0.0;
    float bias = max(0.006 * (1.0 - dot(n, l)), 0.0008);   // evita "acne" de sombra
    vec2 texel = 1.0 / vec2(textureSize(uShadow, 0));
    float s = 0.0;
    for (int x = -1; x <= 1; x++)
        for (int y = -1; y <= 1; y++)
            s += (p.z - bias > texture(uShadow, p.xy + vec2(x, y) * texel).r) ? 1.0 : 0.0;
    return s / 9.0;
}

void main() {
    vec3 c = uC;
    if (uHasT == 1) c *= texture(uT, vU * uTile).rgb;

    // Sombreamento (Phong/Blinn): depende da normal da superfície e da direção da luz
    vec3 n = normalize(vN), l = normalize(-uLdir), v = normalize(uE - vP), h = normalize(l + v);
    float d  = max(dot(n, l), 0.0);
    float sp = pow(max(dot(n, h), 0.0), uShin) * uSpec * step(0.001, d);

    // Sombra projetada: depende de haver outro objeto entre a luz e este ponto
    float sh = 1.0 - shadow(n, l);

    F = vec4(c * (0.30 + 0.75 * d * sh) + vec3(sp * sh), 1.0);
}
