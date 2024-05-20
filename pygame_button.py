import pygame
from threading import Thread


class Button:
    def __init__(self, x, y, width, height, name, font=None) -> None:
        self.rect = pygame.Rect(x, y, width, height)

        self.font = font if font else pygame.font.Font(None, 28)
        self.colors = {
            "BLACK": (0, 0, 0),
            "WHITE": (255, 255, 255),
            "GRAY": (200, 200, 200),
            "LIGHT_GRAY": (220, 220, 220),
        }
        self.color_to_draw = "GRAY"
        self.name = name

    def draw(self, screen):
        # Draw the main dropdown button
        pygame.draw.rect(screen, self.colors[self.color_to_draw], self.rect)
        pygame.draw.rect(screen, self.colors["BLACK"], self.rect, 2)

        text = self.font.render(self.name, True, self.colors["BLACK"])
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)

    def handle_event(self, event):
        """
        Funcionalidad de cuando se pulsa la búsqueda. Comprueba que estén bien los filtros y busca en el árbol en base a estos
        """
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.color_to_draw = "LIGHT_GRAY"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.to_execute()
        else:
            self.color_to_draw = "GRAY"

        return None

    def to_execute(self):
        pass


class AgentButton(Button):
    def __init__(self, x, y, width, height, CW, jugador, name, font=None) -> None:
        Button.__init__(self, x, y, width, height, name, font=font)
        self.CW = CW
        self.jugador = jugador

    def to_execute(self):
        self.jugador.set_CW(self.CW, self.name)


class ShuffleButton(Button):
    def __init__(self, x, y, width, height, jugador, name, font=None) -> None:
        Button.__init__(self, x, y, width, height, name, font=font)
        self.jugador = jugador

    def to_execute(self):
        self.jugador.shuffle()


class FindSolutionButton(Button):
    def __init__(self, x, y, width, height, jugador, name, font=None) -> None:
        Button.__init__(self, x, y, width, height, name, font=font)
        self.jugador = jugador

    def to_execute(self):
        self.jugador.set_find(True)


class ResetButton(Button):
    def __init__(self, x, y, width, height, jugador, name, font=None) -> None:
        Button.__init__(self, x, y, width, height, name, font=font)
        self.jugador = jugador

    def to_execute(self):
        self.jugador.reset()
