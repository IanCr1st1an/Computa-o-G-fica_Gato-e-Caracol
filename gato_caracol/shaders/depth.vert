#version 330 core
// Passo 1 do shadow mapping: a cena vista pela luz (só a profundidade é gravada).
layout(location = 0) in vec3 aP;
uniform mat4 uM;    // modelo
uniform mat4 uLS;   // projeção ortográfica * visão da luz
void main() { gl_Position = uLS * uM * vec4(aP, 1.0); }
