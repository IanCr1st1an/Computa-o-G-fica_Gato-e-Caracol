"""Matrizes 4x4 (linha-maior, enviadas ao OpenGL com transpose=GL_TRUE) e helpers de ângulo."""
import math
import numpy as np


def T(x, y, z):
    """Translação."""
    m = np.eye(4, dtype=np.float32)
    m[:3, 3] = (x, y, z)
    return m


def S(x, y, z):
    """Escala."""
    return np.diag([x, y, z, 1]).astype(np.float32)


def RX(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1]], np.float32)


def RY(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1]], np.float32)


def RZ(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32)


def persp(fov, aspect, near, far):
    """Projeção em perspectiva (câmera)."""
    t = 1 / math.tan(fov / 2)
    return np.array([[t / aspect, 0, 0, 0],
                     [0, t, 0, 0],
                     [0, 0, (far + near) / (near - far), 2 * far * near / (near - far)],
                     [0, 0, -1, 0]], np.float32)


def ortho(l, r, b, t, n, f):
    """Projeção ortográfica (usada pela luz direcional no shadow mapping)."""
    return np.array([[2 / (r - l), 0, 0, -(r + l) / (r - l)],
                     [0, 2 / (t - b), 0, -(t + b) / (t - b)],
                     [0, 0, -2 / (f - n), -(f + n) / (f - n)],
                     [0, 0, 0, 1]], np.float32)


def look_at(eye, center, up):
    """Matriz de visão: posiciona/orienta a câmera (ou a 'câmera da luz')."""
    f = center - eye
    f = f / np.linalg.norm(f)
    r = np.cross(f, up)
    r = r / np.linalg.norm(r)
    u = np.cross(r, f)
    m = np.eye(4, dtype=np.float32)
    m[0, :3], m[1, :3], m[2, :3] = r, u, -f
    m[:3, 3] = [-r @ eye, -u @ eye, f @ eye]
    return m


def wrap(a):
    """Ângulo normalizado para [-pi, pi)."""
    return (a + math.pi) % (2 * math.pi) - math.pi


def turn(cur, target, max_step):
    """Gira 'cur' em direção a 'target' pelo caminho mais curto, no máximo 'max_step'."""
    d = wrap(target - cur)
    return cur + max(-max_step, min(max_step, d))
