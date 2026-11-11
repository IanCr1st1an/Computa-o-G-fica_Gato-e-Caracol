# Gato de brinquedo + Caracol robótico (Python + Pygame + PyOpenGL)

**Ambiente e situação:** um jardim. O gato de brinquedo (curiosidade) se aproxima do caracol robótico
(percurso de reconhecimento); o caracol reage parando e recolhendo as antenas; depois muda de direção e o gato recua.

## Executar
```
pip install -r requirements.txt
python main.py
```
Controles: `W/S` frente/trás · `A/D` esquerda/direita · `Q/E` desce/sobe · setas giram a câmera ·
`ESPAÇO` pausa/retoma a animação (a câmera continua livre) · `ESC` sai.

## Arquitetura
```
main.py        janela, laço principal (dt real), entrada do teclado, pausa
renderer.py    2 passos de desenho: shadow map (luz) -> cena final (câmera)
scene.py       ambiente (chão, árvores de Natal, presentes), luz direcional, texturas, junta tudo
models.py      Cat e Snail: modelos hierárquicos + animação de cada parte
sequence.py    Encounter: máquina de estados que COORDENA os dois (a interação)
engine/        mini-framework: math3d (T,S,R, perspectiva, ortho, look_at), geometry (esfera, cubo,
               cilindro/cone + Mesh), node (grafo de cena), camera, gfx (Program, Texture, ShadowMap)
shaders/       scene.vert/.frag (cena final) · depth.vert/.frag (passo do shadow map)
assets/        grama.png, casco.png e arvore.png: imagens de textura (ver "Texturas")
```

## Requisitos × onde estão
| # | Requisito | Onde |
|---|-----------|------|
| 1 | Modelos 3D reconhecíveis em ambiente próprio | `models.py`, `scene.py` (só primitivas: esfera, cubo, cilindro, cone) |
| 2 | Animação + interação, independente do FPS | `sequence.py` (estados RECONHECER → PAUSA → DESVIO), `dt` em `main.py` |
| 3 | Translação, rotação, escala, hierarquia | `engine/node.py` (`local()` = T·R·S; `world()` = pai·filho); ex.: cabeça→orelhas/olhos/nariz |
| 4 | Perspectiva, câmera por teclado, pausa | `engine/camera.py`, `persp()`, `ESPAÇO` (pausa = animação com `dt=0`) |
| 5 | Textura de imagem | `Texture` carrega a imagem de `assets/`; UVs vêm da `Mesh`; chão (`tile=6`) e casco |
| 6 | Luz direcional, materiais, normais | `scene.frag` (Blinn-Phong), `Node.color/spec/shin`, normais na `Mesh` |
| 7 | Sombra projetada por shadow mapping (6.9) | `ShadowMap`, `depth.*`, `shadow()` em `scene.frag`; refeita a cada quadro |

**Árvores e colisão:** as árvores de Natal (`Tree` em `models.py`: tronco + 3 cones + estrela, ~2,2 de altura)
são obstáculos circulares no chão. Em `Snail._avoid_obstacles()`, se o corpo entra no círculo, o caracol é empurrado
para fora e passa a contornar a árvore pela direção tangente (não é simulação física, só um teste de distância).

## Texturas
O programa carrega três imagens de `assets/` (`.jpg` ou `.png`): `grama` (repete 6x no chão; ideal que seja
*tileable*/sem emenda), `casco` (mapeada no casco do caracol) e `arvore` (enrola nos cones das árvores
de Natal; formato largo 4:1 e sem emenda na horizontal). O programa não inicia sem elas.
O projeto vem com `casco.png` (listras em espiral), `grama.png` (xadrez de grama) e `arvore.png` (folhagem com bolas, guirlanda e luzes) como imagens provisórias;
para usar outra imagem, basta salvá-la em `assets/` com o mesmo nome (`.jpg` tem prioridade sobre `.png`).

## Shaders, atributos e uniforms efetivamente usados
**Atributos de vértice** (VBO intercalado, 32 bytes/vértice, definidos em `Mesh`):
`location 0 aP` posição (vec3) · `location 1 aN` normal (vec3) · `location 2 aU` coordenada de textura (vec2).

**scene.vert** — `uM` (modelo, do grafo de cena) leva a posição ao mundo; `uV` (visão) e `uP` (perspectiva)
levam à tela; `uLS` calcula `vL`, a posição do vértice vista pela luz. A normal é transformada por
`transpose(inverse(mat3(uM)))`, que a mantém perpendicular à superfície mesmo com escala não uniforme.

**scene.frag** — uniforms: `uC` cor do material · `uSpec`, `uShin` brilho especular · `uHasT`, `uTile`, `uT`
textura (unidade 0) · `uShadow` mapa de profundidade (unidade 1) · `uLdir` direção da luz · `uE` posição da câmera.

**depth.vert / depth.frag** — só `uM` e `uLS` (câmera ortográfica da luz); o fragment shader é vazio, pois só a profundidade importa.

**Pipeline por quadro:** (1) com o framebuffer do `ShadowMap`, desenha-se todo objeto que projeta sombra a partir
da luz → textura de profundidade; (2) desenha-se a cena pela câmera; para cada pixel, `shadow()` leva `vL` para
[0,1], compara a profundidade do pixel com a gravada no mapa (com bias e PCF 3×3) e escurece se houver algo mais perto da luz.

## Sombreamento × sombra projetada
- **Sombreamento (shading)** é a cor da *própria* superfície conforme o ângulo entre sua normal e a luz
  (ambiente + difusa + especular). É local: não sabe se existem outros objetos.
- **Sombra projetada** é a ausência de luz num ponto porque *outro* objeto bloqueia o caminho até a luz.
  Exige informação global da cena, por isso o passo extra do shadow map. Aqui o fator `sh` do shader
  multiplica difusa e especular, mantendo só a luz ambiente nas áreas sombreadas.

## Fontes
- Framework e shadow mapping: adaptados dos exemplos do livro — **[preencher: título/autor, capítulos e seção 6.9]**.
- Código-base: `gato_caracol.py` da dupla (a sombra planar foi substituída por shadow mapping).
- Texturas `grama.png`, `casco.png` e `arvore.png` incluídas: imagens provisórias geradas por script (sem fonte externa). Se trocar por outras imagens: **[preencher: nome, autor, site/URL e licença de cada uma]**.
