#version 330 core
// Atributos de vértice (vêm do VBO da Mesh)
layout(location = 0) in vec3 aP;   // posição no espaço do objeto
layout(location = 1) in vec3 aN;   // normal
layout(location = 2) in vec2 aU;   // coordenada de textura

uniform mat4 uM;    // modelo: objeto -> mundo (acumulada pelo grafo de cena)
uniform mat4 uV;    // visão: mundo -> câmera
uniform mat4 uP;    // projeção em perspectiva
uniform mat4 uLS;   // luz: mundo -> espaço da luz (projeção ortográfica * visão da luz)

out vec3 vP;        // posição no mundo
out vec3 vN;        // normal no mundo
out vec2 vU;
out vec4 vL;        // posição do vértice no espaço da luz (para o shadow mapping)

void main() {
    vec4 w = uM * vec4(aP, 1.0);
    vP = w.xyz;
    vN = transpose(inverse(mat3(uM))) * aN;   // normal correta mesmo com escala não uniforme
    vU = aU;
    vL = uLS * w;
    gl_Position = uP * uV * w;
}
