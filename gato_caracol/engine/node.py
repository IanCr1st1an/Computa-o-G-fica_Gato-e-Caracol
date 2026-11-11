"""Grafo de cena: cada Node tem transformação local relativa ao pai e um material."""
import numpy as np
from .math3d import T, S, RX, RY, RZ


class Node:
    def __init__(self, mesh=None, color=(1, 1, 1), pos=(0, 0, 0), rot=(0, 0, 0), scl=(1, 1, 1),
                 tex=None, tile=1, spec=.35, shin=32., casts_shadow=True):
        self.mesh, self.tex, self.tile = mesh, tex, tile
        self.color, self.spec, self.shin = color, spec, shin      # material (cor difusa, brilho especular)
        self.casts_shadow = casts_shadow
        self.pos, self.rot, self.scl = list(pos), list(rot), list(scl)
        self.kids, self.parent = [], None

    def add(self, *nodes):
        for n in nodes:
            n.parent = self; self.kids.append(n)
        return self

    def local(self):
        """Ordem: escala -> rotação -> translação (lida da direita para a esquerda)."""
        return T(*self.pos) @ RY(self.rot[1]) @ RX(self.rot[0]) @ RZ(self.rot[2]) @ S(*self.scl)

    def world(self):
        """Matriz de modelo: acumula as transformações de todos os ancestrais."""
        parent = self.parent.world() if self.parent else np.eye(4, dtype=np.float32)
        return parent @ self.local()

    def walk(self):
        yield self
        for k in self.kids:
            yield from k.walk()
