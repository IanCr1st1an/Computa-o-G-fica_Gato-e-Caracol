"""Recursos de GPU: Program (shaders + uniforms), Texture (imagem) e ShadowMap (FBO de profundidade)."""
import numpy as np
import pygame
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader


class Program:
    """Compila um par vertex/fragment shader a partir de arquivos .vert/.frag."""
    def __init__(self, vert_path, frag_path):
        read = lambda p: open(p, encoding="utf-8").read()
        self.id = compileProgram(compileShader(read(vert_path), GL_VERTEX_SHADER),
                                 compileShader(read(frag_path), GL_FRAGMENT_SHADER), validate=False)
        self._loc = {}

    def use(self):
        glUseProgram(self.id)

    def set(self, name, v):
        """Envia um uniform; o tipo do GLSL é deduzido do valor Python."""
        if name not in self._loc:
            self._loc[name] = glGetUniformLocation(self.id, name)
        loc = self._loc[name]
        if isinstance(v, np.ndarray) and v.shape == (4, 4):
            glUniformMatrix4fv(loc, 1, GL_TRUE, v)          # GL_TRUE: nossas matrizes são linha-maior
        elif isinstance(v, (tuple, list, np.ndarray)):
            glUniform3f(loc, *v)
        elif isinstance(v, int):
            glUniform1i(loc, v)
        else:
            glUniform1f(loc, float(v))


class Texture:
    """Textura 2D carregada de um arquivo de imagem (.jpg/.png) com pygame.image.load."""
    def __init__(self, path):
        surf = pygame.image.load(path)
        w, h = surf.get_size()
        tobytes = getattr(pygame.image, "tobytes", None) or pygame.image.tostring
        pixels = tobytes(surf, "RGB", True)                  # True: inverte linhas (origem OpenGL)
        self.id = glGenTextures(1); glBindTexture(GL_TEXTURE_2D, self.id)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, w, h, 0, GL_RGB, GL_UNSIGNED_BYTE, pixels)
        glGenerateMipmap(GL_TEXTURE_2D)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    def bind(self, unit=0):
        glActiveTexture(GL_TEXTURE0 + unit)
        glBindTexture(GL_TEXTURE_2D, self.id)


class ShadowMap:
    """Framebuffer só com textura de profundidade: guarda a cena vista pela luz (seção 6.9)."""
    def __init__(self, size=2048):
        self.size = size
        self.tex = glGenTextures(1); glBindTexture(GL_TEXTURE_2D, self.tex)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT24, size, size, 0,
                     GL_DEPTH_COMPONENT, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, np.array([1, 1, 1, 1], np.float32))
        self.fbo = glGenFramebuffers(1); glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, self.tex, 0)
        glDrawBuffer(GL_NONE); glReadBuffer(GL_NONE)         # sem buffer de cor
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def begin(self):
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
        glViewport(0, 0, self.size, self.size)
        glClear(GL_DEPTH_BUFFER_BIT)

    def end(self, w, h):
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glViewport(0, 0, w, h)
