"""Renderização em dois passos: (1) shadow map visto pela luz, (2) cena final com iluminação e sombra."""
import os
import math
import numpy as np
from OpenGL.GL import *
from engine.gfx import Program, ShadowMap
from engine.math3d import persp, ortho, look_at

SHADERS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shaders")
UP = np.array([0, 1, 0], np.float32)


class Renderer:
    def __init__(self, w, h):
        self.w, self.h = w, h
        sp = lambda f: os.path.join(SHADERS, f)
        self.main = Program(sp("scene.vert"), sp("scene.frag"))
        self.depth = Program(sp("depth.vert"), sp("depth.frag"))
        self.shadow = ShadowMap(2048)
        self.proj = persp(math.radians(55), w / h, .1, 80)
        glEnable(GL_DEPTH_TEST); glDepthFunc(GL_LEQUAL)
        glClearColor(.55, .75, .92, 1)

    @staticmethod
    def light_matrix(L):
        """'Câmera da luz': ortográfica (luz direcional = raios paralelos), olhando para o centro da cena."""
        eye = (-L * 20).astype(np.float32)
        return ortho(-10, 10, -10, 10, 1, 45) @ look_at(eye, np.zeros(3, np.float32), UP)

    def draw(self, scene, cam):
        items = [(n, n.world()) for n in scene.root.walk() if n.mesh]
        LS = self.light_matrix(scene.light)

        # Passo 1: profundidade vista pela luz (refeita a cada quadro -> sombra acompanha o movimento)
        self.shadow.begin(); self.depth.use(); self.depth.set("uLS", LS)
        for n, w in items:
            if n.casts_shadow:
                self.depth.set("uM", w); n.mesh.draw()
        self.shadow.end(self.w, self.h)

        # Passo 2: cena vista pela câmera
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        p = self.main; p.use()
        p.set("uV", cam.view()); p.set("uP", self.proj); p.set("uLS", LS)
        p.set("uLdir", scene.light); p.set("uE", cam.pos)
        p.set("uT", 0); p.set("uShadow", 1)
        glActiveTexture(GL_TEXTURE1); glBindTexture(GL_TEXTURE_2D, self.shadow.tex)
        for n, w in items:
            p.set("uM", w); p.set("uC", n.color)
            p.set("uSpec", float(n.spec)); p.set("uShin", float(n.shin))
            p.set("uHasT", 1 if n.tex else 0); p.set("uTile", float(n.tile))
            if n.tex: n.tex.bind(0)
            n.mesh.draw()
