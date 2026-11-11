"""Primitivas geométricas (posição, normal, UV, índices) e a classe Mesh (VAO/VBO)."""
import math
import ctypes
import numpy as np
from OpenGL.GL import *


def sphere(n=24):
    P, N, U, I = [], [], [], []
    for i in range(n + 1):
        th = math.pi * i / n
        for j in range(n + 1):
            ph = 2 * math.pi * j / n
            v = (math.sin(th) * math.cos(ph), math.cos(th), math.sin(th) * math.sin(ph))
            P.append(v); N.append(v); U.append((j / n, i / n))   # numa esfera unitária, normal = posição
    for i in range(n):
        for j in range(n):
            a = i * (n + 1) + j; b = a + n + 1
            I += [a, b, a + 1, a + 1, b, b + 1]
    return P, N, U, I


def box():
    """Cubo de lado 1 centrado na origem; cada face tem 4 vértices próprios (normal própria)."""
    P, N, U, I = [], [], [], []
    faces = [((1, 0, 0), (0, 0, -1), (0, 1, 0)), ((-1, 0, 0), (0, 0, 1), (0, 1, 0)),
             ((0, 1, 0), (1, 0, 0), (0, 0, -1)), ((0, -1, 0), (1, 0, 0), (0, 0, 1)),
             ((0, 0, 1), (1, 0, 0), (0, 1, 0)), ((0, 0, -1), (-1, 0, 0), (0, 1, 0))]
    for n, u, v in faces:
        b = len(P)
        for a, c in [(-1, -1), (1, -1), (1, 1), (-1, 1)]:
            P.append(tuple(.5 * (n[k] + a * u[k] + c * v[k]) for k in range(3)))
            N.append(n); U.append(((a + 1) / 2, (c + 1) / 2))
        I += [b, b + 1, b + 2, b, b + 2, b + 3]
    return P, N, U, I


def cyl(r0=1., r1=1., n=24):
    """Cilindro/cone: base em y=0 (raio r0), topo em y=1 (raio r1; r1=0 -> cone)."""
    P, N, U, I = [], [], [], []
    for i in range(n + 1):
        a = 2 * math.pi * i / n; c, s = math.cos(a), math.sin(a)
        P += [(r0 * c, 0, r0 * s), (r1 * c, 1, r1 * s)]
        N += [(c, 0, s)] * 2; U += [(i / n, 0), (i / n, 1)]
    for i in range(n):
        k = 2 * i; I += [k, k + 1, k + 2, k + 2, k + 1, k + 3]
    for y, r, ny in ((0, r0, -1), (1, r1, 1)):          # tampas
        b = len(P); P.append((0, y, 0)); N.append((0, ny, 0)); U.append((.5, .5))
        for i in range(n + 1):
            a = 2 * math.pi * i / n
            P.append((r * math.cos(a), y, r * math.sin(a))); N.append((0, ny, 0)); U.append((.5, .5))
        for i in range(n):
            I += [b, b + 1 + i, b + 2 + i]
    return P, N, U, I


class Mesh:
    """Envia a geometria para a GPU. Layout de cada vértice (32 bytes):
       location 0 = posição (vec3) | location 1 = normal (vec3) | location 2 = UV (vec2)."""
    def __init__(self, geom):
        P, N, U, I = geom
        data = np.hstack([np.array(P), np.array(N), np.array(U)]).astype(np.float32)
        idx = np.array(I, np.uint32)
        self.count = len(I)
        self.vao = glGenVertexArrays(1); glBindVertexArray(self.vao)
        vbo = glGenBuffers(1); glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)
        ibo = glGenBuffers(1); glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ibo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, idx.nbytes, idx, GL_STATIC_DRAW)
        for loc, (size, offset) in enumerate([(3, 0), (3, 12), (2, 24)]):
            glEnableVertexAttribArray(loc)
            glVertexAttribPointer(loc, size, GL_FLOAT, False, 32, ctypes.c_void_p(offset))

    def draw(self):
        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, self.count, GL_UNSIGNED_INT, None)
