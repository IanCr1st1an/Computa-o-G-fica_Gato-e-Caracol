"""Gato de brinquedo + Caracol robótico  (Python + Pygame + PyOpenGL)
Instalar: pip install pygame PyOpenGL numpy        Executar: python main.py

Controles:  W/S frente/trás | A/D esquerda/direita | Q/E desce/sobe | setas = girar a câmera
            ESPAÇO = pausar/retomar a animação (a câmera continua livre) | ESC = sair
"""
import pygame
from engine.camera import Camera
from renderer import Renderer
from scene import Scene

W, H = 1000, 700


def main():
    pygame.init()
    for attr, val in [(pygame.GL_CONTEXT_MAJOR_VERSION, 3), (pygame.GL_CONTEXT_MINOR_VERSION, 3),
                      (pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE),
                      (pygame.GL_DEPTH_SIZE, 24)]:
        pygame.display.gl_set_attribute(attr, val)
    pygame.display.set_mode((W, H), pygame.DOUBLEBUF | pygame.OPENGL)

    renderer, scene = Renderer(W, H), Scene()
    camera = Camera(pos=(6, 4.5, 8), yaw=-0.6435, pitch=-0.4228)   # olhando para o centro do jardim
    clock, paused, running = pygame.time.Clock(), False, True

    while running:
        dt = min(clock.tick(60) / 1000, .05)          # tempo real decorrido (s): velocidades não dependem do FPS
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                running = False
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                paused = not paused

        camera.update(pygame.key.get_pressed(), dt)   # câmera sempre ativa, mesmo pausado
        status = scene.update(0. if paused else dt)   # pausa = animação recebe dt = 0
        renderer.draw(scene, camera)
        pygame.display.set_caption(status + ("  [PAUSADO]" if paused else ""))
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()
