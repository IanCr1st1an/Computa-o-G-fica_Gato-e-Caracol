"""Modelos hierárquicos: Gato de brinquedo e Caracol robótico (frente = +z local).
Cada parte é um Node filho de outro Node; mexer na cabeça move orelhas, olhos e nariz juntos."""
import math
from engine.node import Node
from engine.math3d import turn, wrap


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


class Cat:
    ARENA = 5.0

    def __init__(self, sh):
        o = (.95, .6, .2)
        self.root = Node()
        self.root.add(Node(sh.box, o, (0, .62, 0), scl=(.5, .4, .9)))                    # corpo

        self.legs = []                                                                   # 4 patas (pivô no quadril)
        for sx in (-1, 1):
            for sz in (-1, 1):
                hip = Node(None, pos=(sx * .17, .42, sz * .3))
                hip.add(Node(sh.cyl, (.85, .5, .15), (0, -.42, 0), scl=(.07, .42, .07)))
                self.root.add(hip); self.legs.append((hip, sx * sz))

        self.head = Node(None, pos=(0, .88, .5)); self.root.add(self.head)               # cabeça (pivô)
        self.head.add(Node(sh.sph, o, scl=(.28, .24, .24)))
        for sx in (-1, 1):
            self.head.add(Node(sh.cone, o, (sx * .14, .18, 0), rot=(0, 0, -sx * .25), scl=(.09, .2, .09)))  # orelhas
            self.head.add(Node(sh.sph, (.05, .05, .05), (sx * .1, .05, .21), scl=(.045, .045, .045)))        # olhos
        self.head.add(Node(sh.sph, (.9, .4, .5), (0, -.03, .24), scl=(.035, .03, .03)))                      # nariz

        self.tail = Node(None, pos=(0, .7, -.45), rot=(-.8, 0, 0)); self.root.add(self.tail)
        self.tail.add(Node(sh.cyl, o, scl=(.05, .5, .05)))

        self.key = Node(None, pos=(0, .84, -.1)); self.root.add(self.key)                # chave de dar corda
        self.key.add(Node(sh.box, (.7, .7, .75), (0, .1, 0), scl=(.22, .03, .06)))
        self.key.add(Node(sh.cyl, (.7, .7, .75), scl=(.025, .1, .025)))

        self.t = 0.; self.walk = 0.; self.head_angle = 0.

    @property
    def pos(self):
        return self.root.pos

    def step(self, dt, v, bearing, turn_rate, sniff):
        """v = velocidade (negativa = recuar), bearing = ângulo (no mundo) até o caracol."""
        r = self.root; self.t += dt
        r.rot[1] = turn(r.rot[1], bearing, turn_rate * dt)                 # corpo vira
        y = r.rot[1]
        r.pos[0] = clamp(r.pos[0] + math.sin(y) * v * dt, -self.ARENA, self.ARENA)
        r.pos[2] = clamp(r.pos[2] + math.cos(y) * v * dt, -self.ARENA, self.ARENA)
        self.walk += v * dt * 6
        for hip, k in self.legs:                                           # marcha em diagonal
            hip.rot[0] = .5 * math.sin(self.walk) * k * (1 if v else 0)
        self.tail.rot[1] = .5 * math.sin(self.t * 3)
        self.key.rot[1] += abs(v) * dt * 6
        want = clamp(wrap(bearing - y), -1.1, 1.1)                         # cabeça olha para o caracol (±63°)
        self.head_angle += (want - self.head_angle) * min(1, dt * 6)
        self.head.rot[1] = self.head_angle
        self.head.rot[0] = .18 * math.sin(self.t * 7) if sniff else 0.     # farejar


class Snail:
    LIMIT = 4.3
    RADIUS = .35          # raio do corpo (usado na colisão com obstáculos)

    def __init__(self, sh, shell_tex):
        m = (.55, .6, .7)
        self.root = Node()
        self.root.add(Node(sh.sph, m, (0, .1, 0), scl=(.28, .1, .8)))                    # corpo
        self.root.add(Node(sh.sph, m, (0, .24, .7), scl=(.17, .17, .17)))                # cabeça
        self.root.add(Node(sh.sph, (1, 1, 1), (0, .52, -.1), scl=(.4, .4, .4),       # casco (texturizado)
                           tex=shell_tex, tile=1, spec=.8, shin=64.))
        self.ants = []
        for sx in (-1, 1):
            pivot = Node(None, pos=(sx * .09, .36, .76))
            shaft = Node(sh.cyl, (.7, .72, .78), scl=(.02, .4, .02))
            tip = Node(sh.sph, (1, .15, .1), (0, .4, 0), scl=(.045, .045, .045))
            pivot.add(shaft, tip); self.root.add(pivot); self.ants.append((pivot, shaft, tip, sx))
        self.heading = self.target = 1.2; self.side = 1
        self.obstacles = []                                   # círculos (x, z, raio) que o caracol não atravessa
        self.t = 0.; self.ant = 1.

    @property
    def pos(self):
        return self.root.pos

    def change_direction(self):
        """Desvia 90° (alternando o lado a cada vez)."""
        self.target = self.heading + self.side * math.pi / 2
        self.side *= -1

    def _avoid_obstacles(self):
        """Se o corpo entrar num obstáculo circular: empurra para fora e passa a contorná-lo (direção tangente)."""
        r = self.root
        for ox, oz, rad in self.obstacles:
            dx, dz = r.pos[0] - ox, r.pos[2] - oz
            d = math.hypot(dx, dz)
            lim = rad + self.RADIUS
            if d >= lim:
                continue
            nx, nz = (dx / d, dz / d) if d > 1e-6 else (1., 0.)          # normal: do obstáculo para o caracol
            r.pos[0], r.pos[2] = ox + nx * lim, oz + nz * lim
            fx, fz = math.sin(self.heading), math.cos(self.heading)
            if fx * nx + fz * nz < 0:                                       # estava indo contra o obstáculo
                tx, tz = (-nz, nx) if (-nz * fx + nx * fz) >= 0 else (nz, -nx)
                self.target = math.atan2(tx, tz)                            # tangente mais próxima da direção atual

    def step(self, dt, gliding, antenna):
        """gliding = está deslizando?  antenna = 1 (estendida) ... 0.15 (recolhida)."""
        r = self.root; self.t += dt
        if abs(r.pos[0]) > self.LIMIT or abs(r.pos[2]) > self.LIMIT:      # volta para a arena
            self.target = math.atan2(-r.pos[0], -r.pos[2])
        self.heading = turn(self.heading, self.target, 1.2 * dt)
        if gliding:
            v = .5 if abs(wrap(self.target - self.heading)) < .3 else .15
            r.pos[0] += math.sin(self.heading) * v * dt
            r.pos[2] += math.cos(self.heading) * v * dt
        self._avoid_obstacles()
        r.rot[1] = self.heading
        self.ant += (antenna - self.ant) * min(1, dt * 6)
        for i, (pivot, shaft, tip, sx) in enumerate(self.ants):
            pivot.rot[2] = -sx * (.35 + .15 * math.sin(self.t * 3 + i))
            pivot.rot[0] = .15 * math.sin(self.t * 2 + i * 2)
            shaft.scl[1] = .4 * self.ant
            tip.pos[1] = .4 * self.ant


class Tree:
    """Árvore de Natal: tronco + 3 cones empilhados com textura + estrela. Base de raio 1*scale no chão."""
    def __init__(self, sh, tex, x, z, scale=.8):
        self.root = Node(pos=(x, 0, z), scl=(scale, scale, scale))
        self.radius = 1.0 * scale                                           # raio de colisão (círculo no chão)
        self.root.add(Node(sh.cyl, (.4, .25, .12), scl=(.16, .45, .16), spec=.05))              # tronco
        for y, r, h in [(.35, 1.0, 1.2), (1.05, .76, 1.1), (1.75, .52, 1.0)]:                   # 3 andares
            self.root.add(Node(sh.cone, (1, 1, 1), (0, y, 0), scl=(r, h, r), tex=tex, tile=1, spec=.15, shin=16.))
        self.root.add(Node(sh.sph, (1, .85, .2), (0, 2.82, 0), scl=(.13, .13, .13), spec=.9, shin=64.))  # estrela


class Gift:
    """Caixa de presente: corpo (cubo) + 2 fitas cruzadas + laço. Modelada num cubo unitário e escalada por 'size'."""
    def __init__(self, sh, x, z, size, body, ribbon, rot_y=0.):
        self.root = Node(pos=(x, 0, z), rot=(0, rot_y, 0), scl=(size, size, size))
        self.root.add(Node(sh.box, body, (0, .5, 0), spec=.4, shin=24.))                         # corpo
        self.root.add(Node(sh.box, ribbon, (0, .5, 0), scl=(1.02, 1.02, .16), spec=.6, shin=32.))  # fita em z
        self.root.add(Node(sh.box, ribbon, (0, .5, 0), scl=(.16, 1.02, 1.02), spec=.6, shin=32.))  # fita em x
        for sx in (-1, 1):                                                                       # laço (2 "orelhas")
            self.root.add(Node(sh.sph, ribbon, (sx * .13, 1.07, 0), rot=(0, 0, -sx * .6),
                               scl=(.2, .1, .1), spec=.6, shin=32.))
        self.root.add(Node(sh.sph, ribbon, (0, 1.05, 0), scl=(.07, .07, .07), spec=.6, shin=32.))  # nó
