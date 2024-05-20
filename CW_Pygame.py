from CW_Bayes import CW_Bayes
from CW_BayesSearch import CW_BayesSearch
from CW_KB import CW_KB
from CW_KB_Search import CW_KB_Search
import pygame


class CW_KB_Pygame(CW_KB):
    def __init__(
        self,
        entorno,
        screen,
        delay=0,
    ) -> None:
        CW_KB.__init__(self, entorno, delay=delay)
        self.screen = screen
        self.set_clear(self.get_position(), self.KB, self.room_states)
        self.un_movimiento()

    def un_movimiento(self) -> None:
        position = self.get_position()
        percepts = self.get_percepts(position)

        self.handle_percepts(percepts, position, self.KB, self.room_states)
        posible_moves = self.get_posible_moves(percepts, position)
        self.display_posible_moves(posible_moves)

    def display_posible_moves(self, posible_moves) -> None:
        if posible_moves:
            text = "Posible moves: " + ", ".join(list(zip(*posible_moves))[0])

        else:
            text = "No possible moves"

        text_to_display = pygame.font.Font(None, 60).render(text, True, (255, 255, 255))
        text_rect = text_to_display.get_rect(center=(self.screen.get_width() // 2, 150))
        rect = pygame.Rect(self.screen.get_width() // 2 - 425, 115, 850, 70)
        pygame.draw.rect(self.screen, (0, 0, 0), rect)
        self.screen.blit(text_to_display, text_rect)

    def hacer_siguiente_movimiento(self, accion) -> tuple:
        ok, victory = self.actuar(accion)
        self.un_movimiento()
        return ok, victory

    def dibujar(self) -> None:
        self.entorno.dibujar(self.room_states)


class CW_Bayes_Pygame(CW_Bayes):
    def __init__(self, entorno, screen, delay=0, umbral=0.2) -> None:
        CW_Bayes.__init__(self, entorno, delay=delay, umbral=umbral)
        self.screen = screen
        self.un_movimiento()

    def un_movimiento(self) -> None:
        percepts = self.get_percepts(self.get_position())
        self.handle_percepts(percepts)

        posible_moves = self.get_posible_moves(
            percepts, self.get_position(), self.mapas, self.umbral
        )

        self.display_posible_moves(posible_moves)

    def hacer_siguiente_movimiento(self, accion):
        ok, victory = self.actuar(accion)
        self.un_movimiento()
        return ok, victory

    def dibujar(self) -> None:
        self.entorno.dibujar(self.mapas, umbral=self.umbral)

    def display_posible_moves(self, posible_moves) -> None:
        if posible_moves:
            text = "Posible moves: " + ", ".join(list(zip(*posible_moves))[0])

        else:
            text = "No possible moves"

        text_to_display = pygame.font.Font(None, 60).render(text, True, (255, 255, 255))
        text_rect = text_to_display.get_rect(center=(self.screen.get_width() // 2, 150))
        rect = pygame.Rect(self.screen.get_width() // 2 - 425, 115, 850, 70)
        pygame.draw.rect(self.screen, (0, 0, 0), rect)
        self.screen.blit(text_to_display, text_rect)


class CW_BayesSearch_Pygame(CW_Bayes_Pygame, CW_BayesSearch):
    def __init__(self, entorno, screen, delay=0.2, umbral=0.2) -> None:
        CW_BayesSearch.__init__(self, entorno, delay)
        CW_Bayes_Pygame.__init__(self, entorno, screen, delay, umbral=umbral)


class CW_KB_Search_Pygame(CW_KB_Pygame, CW_KB_Search):
    def __init__(self, entorno, screen, delay=0.2) -> None:
        CW_KB_Search.__init__(self, entorno, delay=0)
        CW_KB_Pygame.__init__(self, entorno, screen, delay)
