"""Câmera livre controlada pelo teclado (movimento proporcional ao tempo decorrido)."""
import math
import numpy as np
import pygame
from .math3d import look_at

UP = np.array([0, 1, 0], np.float32)


class Camera:
    SPEED, TURN = 5.0, 1.4          # unidades/s e rad/s

    def __init__(self, pos, yaw, pitch):
        self.pos = np.array(pos, np.float32)
        self.yaw, self.pitch = yaw, pitch

    def forward(self):
        cp = math.cos(self.pitch)
        return np.array([math.sin(self.yaw) * cp, math.sin(self.pitch), -math.cos(self.yaw) * cp], np.float32)

    def update(self, keys, dt):
        f = self.forward(); r = np.cross(f, UP); r /= np.linalg.norm(r)
        step = self.SPEED * dt
        if keys[pygame.K_w]: self.pos += f * step          # frente
        if keys[pygame.K_s]: self.pos -= f * step          # trás
        if keys[pygame.K_d]: self.pos += r * step          # direita
        if keys[pygame.K_a]: self.pos -= r * step          # esquerda
        if keys[pygame.K_e]: self.pos += UP * step         # sobe
        if keys[pygame.K_q]: self.pos -= UP * step         # desce
        if keys[pygame.K_RIGHT]: self.yaw += self.TURN * dt
        if keys[pygame.K_LEFT]:  self.yaw -= self.TURN * dt
        if keys[pygame.K_UP]:    self.pitch = min(1.5, self.pitch + self.TURN * dt)
        if keys[pygame.K_DOWN]:  self.pitch = max(-1.5, self.pitch - self.TURN * dt)

    def view(self):
        return look_at(self.pos, self.pos + self.forward(), UP)
