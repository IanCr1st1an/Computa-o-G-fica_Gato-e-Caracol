"""Cena: ambiente (jardim), os dois personagens, a luz direcional e a sequência de animação."""
import os
from types import SimpleNamespace
import numpy as np
from engine.geometry import Mesh, sphere, box, cyl
from engine.gfx import Texture
from engine.node import Node
from models import Cat, Snail, Tree, Gift
from sequence import Encounter

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def load_texture(name):
    """Carrega assets/<name>.jpg (ou .jpeg/.png). As imagens são fornecidas pela dupla (ver README)."""
    for ext in (".jpg", ".jpeg", ".png"):
        path = os.path.join(ASSETS, name + ext)
        if os.path.exists(path):
            return Texture(path)
    raise FileNotFoundError(f"Imagem de textura não encontrada: coloque assets/{name}.jpg (ou .png). Veja o README.")


class Scene:
    def __init__(self):
        sh = SimpleNamespace(sph=Mesh(sphere()), box=Mesh(box()), cyl=Mesh(cyl(1, 1)), cone=Mesh(cyl(1, 0)))
        tex_floor = load_texture("grama")      # textura de imagem do chão
        tex_shell = load_texture("casco")      # textura de imagem do casco do caracol
        tex_tree = load_texture("arvore")      # textura das árvores de Natal

        self.root = Node()
        # chão (recebe sombra, não projeta); topo em y = 0
        self.root.add(Node(sh.box, (1, 1, 1), (0, -.05, 0), scl=(12, .1, 12),
                           tex=tex_floor, tile=6, spec=.05, casts_shadow=False))
        for x, z, size, body, ribbon, ry in [(-3.5, -3, .8, (.8, .1, .12), (.95, .8, .3), .4),     # presentes
                                             (3.8, -2, .6, (.15, .3, .8), (.85, .85, .9), -.3),
                                             (-4, 3, .5, (.1, .55, .25), (.85, .12, .12), .8)]:
            self.root.add(Gift(sh, x, z, size, body, ribbon, ry).root)
        self.trees = [Tree(sh, tex_tree, x, z) for x, z in [(2.8, -3.6), (-1.2, -4.0), (4.0, 3.0), (-2.2, 3.8)]]
        for t in self.trees:                                                                  # árvores de Natal
            self.root.add(t.root)

        self.cat, self.snail = Cat(sh), Snail(sh, tex_shell)
        self.root.add(self.cat.root, self.snail.root)
        self.snail.obstacles = [(t.root.pos[0], t.root.pos[2], t.radius) for t in self.trees]
        self.encounter = Encounter(self.cat, self.snail)

        self.light = np.array([-.4, -1., -.3], np.float32)       # luz direcional (direção de propagação)
        self.light /= np.linalg.norm(self.light)

    def update(self, dt):
        return self.encounter.update(dt)
