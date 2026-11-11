"""Sequência coordenada entre os dois personagens (máquina de estados).

  RECONHECER : gato se aproxima olhando para o caracol; caracol segue o percurso.
  PAUSA      : (gato a < 2.0 do caracol) caracol PARA e recolhe as antenas; gato fareja.
  DESVIO     : caracol MUDA DE DIREÇÃO; gato recua até ficar a >= 3.4 e volta a RECONHECER.
O que cada um faz depende do estado e da posição do outro -> há interação, não só dois movimentos soltos.
"""
import math


class Encounter:
    NEAR, FAR = 2.0, 3.4

    def __init__(self, cat, snail):
        self.cat, self.snail = cat, snail
        self.phase, self.t = "reconhecer", 0.
        cat.pos[:] = [2.5, 0, 3.0]; cat.root.rot[1] = math.pi
        snail.pos[:] = [-3.5, 0, -1.0]

    def _goto(self, phase):
        self.phase, self.t = phase, 0.

    def update(self, dt):
        self.t += dt
        dx = self.snail.pos[0] - self.cat.pos[0]
        dz = self.snail.pos[2] - self.cat.pos[2]
        dist, bearing = math.hypot(dx, dz), math.atan2(dx, dz)
        v, turn_rate, sniff = 0., 3., False
        gliding, antenna = True, 1.

        if self.phase == "reconhecer":
            if dist > self.NEAR: v = 1.1
            else: self._goto("pausa")
        elif self.phase == "pausa":
            gliding, antenna, sniff = False, .15, True
            if self.t > 3.:
                self.snail.change_direction(); self._goto("desvio")
        else:  # desvio
            turn_rate = 2.
            if dist < self.FAR: v = -1.0
            if (dist >= self.FAR and self.t > 1.5) or self.t > 6.: self._goto("reconhecer")

        self.cat.step(dt, v, bearing, turn_rate, sniff)
        self.snail.step(dt, gliding, antenna)
        return f"fase: {self.phase} | distancia gato-caracol: {dist:.2f}"
