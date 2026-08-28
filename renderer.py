"""Small GLU-free OpenGL renderer for Pygame surfaces.

Create the ``pygame.OPENGL | pygame.DOUBLEBUF`` display before constructing a
Renderer. Coordinates use Pygame's convention: (0, 0) is the top-left.
"""

import pygame

from OpenGL.GL import (
    GL_BLEND, GL_COLOR_BUFFER_BIT, GL_LINE_LOOP, GL_LINEAR, GL_MODELVIEW,
    GL_ONE_MINUS_SRC_ALPHA, GL_PROJECTION, GL_QUADS, GL_RGBA, GL_SRC_ALPHA,
    GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_TEXTURE_MIN_FILTER,
    GL_UNSIGNED_BYTE, glBegin, glBindTexture, glBlendFunc, glClear,
    glClearColor, glColor4f, glDeleteTextures, glDisable, glEnable, glEnd,
    glGenTextures, glLineWidth, glLoadIdentity, glMatrixMode, glOrtho,
    glTexCoord2f, glTexImage2D, glTexParameteri, glVertex2f, glViewport,
)


class Renderer:
    """Render Pygame surfaces through the current OpenGL context.

    Surfaces are uploaded once and cached by object identity. Call
    :meth:`invalidate_surface` after changing a cached surface's pixels.
    """

    def __init__(self, width, height, clear_color=(135, 206, 235, 255)):
        self.width = width
        self.height = height
        self.clear_color = clear_color
        # Keep the source surface alongside its texture. This prevents Python
        # from reusing a destroyed surface's id for a different texture.
        self._textures = {}
        self._texture_enabled = False

        self.resize(width, height)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def resize(self, width, height):
        """Use a top-left-origin pixel coordinate system."""
        self.width = width
        self.height = height
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, height, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def begin_frame(self, clear_color=None):
        """Clear the back buffer before issuing draw calls."""
        color = clear_color or self.clear_color
        red, green, blue, opacity = pygame.Color(color)
        glClearColor(red / 255, green / 255, blue / 255, opacity / 255)
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()

    def texture_for(self, surface):
        """Return the OpenGL texture ID for a Pygame surface."""
        key = id(surface)
        if key in self._textures:
            return self._textures[key][1]

        texture = self._upload_surface(surface)
        self._textures[key] = (surface, texture)
        return texture

    @staticmethod
    def _upload_surface(surface):
        """Upload a Pygame surface and return its OpenGL texture ID."""

        width, height = surface.get_size()
        pixels = pygame.image.tostring(surface, "RGBA", True)
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,
            GL_RGBA, GL_UNSIGNED_BYTE, pixels,
        )
        return texture

    def invalidate_surface(self, surface):
        """Discard a surface's cached texture after its pixels change."""
        cached = self._textures.pop(id(surface), None)
        if cached is not None:
            glDeleteTextures([cached[1]])

    def draw_surface(self, surface, dest, *, cache=True):
        """Draw ``surface`` at a ``pygame.Rect`` or (x, y) destination."""
        if isinstance(dest, pygame.Rect):
            x, y, width, height = dest
        else:
            x, y = dest
            width, height = surface.get_size()

        texture = self.texture_for(surface) if cache else self._upload_surface(surface)
        if not self._texture_enabled:
            glEnable(GL_TEXTURE_2D)
            self._texture_enabled = True
        glBindTexture(GL_TEXTURE_2D, texture)
        glColor4f(1, 1, 1, 1)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1)
        glVertex2f(x, y)
        glTexCoord2f(1, 1)
        glVertex2f(x + width, y)
        glTexCoord2f(1, 0)
        glVertex2f(x + width, y + height)
        glTexCoord2f(0, 0)
        glVertex2f(x, y + height)
        glEnd()
        if not cache:
            glDeleteTextures([texture])

    def draw_rect(self, rect, color, width=1, skeleton=False):
        """Draw an unfilled debug rectangle using Pygame-style coordinates."""
        if self._texture_enabled:
            glDisable(GL_TEXTURE_2D)
            self._texture_enabled = False
        red, green, blue, opacity = pygame.Color(color)
        glColor4f(red / 255, green / 255, blue / 255, opacity / 255)
        glLineWidth(width)
        if skeleton: glBegin(GL_LINE_LOOP)
        else: glBegin(GL_QUADS)
        glVertex2f(rect.left, rect.top)
        glVertex2f(rect.right, rect.top)
        glVertex2f(rect.right, rect.bottom)
        glVertex2f(rect.left, rect.bottom)
        glEnd()

    def present(self):
        """Swap the OpenGL back buffer onto the display."""
        pygame.display.flip()

    def close(self):
        """Release OpenGL textures before Pygame destroys the GL context."""
        if self._textures:
            glDeleteTextures([texture for _, texture in self._textures.values()])
            self._textures.clear()
