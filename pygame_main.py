import sys
import pygame
from CW_Pygame import CW_BayesSearch_Pygame, CW_KB_Search_Pygame
from Palacio import PalacioPygame
from PalacioBayes import PalacioBayesPygame
from pygame_button import AgentButton, FindSolutionButton, ResetButton, ShuffleButton
from auxiliary_functions import imprimir_mensaje

# Constants
WIDTH, HEIGHT = 800, 800
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (169, 169, 169)
FONT_SIZE = 36
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50


class MensajeError:
    """
    Clase del mensaje de error
    """

    def __init__(self) -> None:
        self.msg: str = ""
        self.colors = {
            "WHITE": (255, 255, 255),
            "BLACK": (0, 0, 0),
            "GRAY": (169, 169, 169),
            "RED": (255, 0, 0),
            "BLUE": (0, 0, 255),
            "GREEN": (0, 255, 0),
        }
        self.color = self.colors["RED"]

    def set_msg(self, msg="", color="RED") -> None:
        self.msg = msg
        self.color = self.colors[color]

    def mostrar(self, screen, font) -> None:
        """
        Muestra el mensaje de error en el medio de la pantalla
        """

        imprimir_mensaje(screen, self.msg, font, self.color)


class Jugador:
    def __init__(self, screen, UMBRAL):
        self.CW_class = None
        self.palace = None
        self.CW = None
        self.agent_name = None
        self.set_umbral = False
        self.palace_dict = {
            "Agente KB": PalacioPygame,
            "Agente Bayesiano": PalacioBayesPygame,
        }
        self.screen = screen
        self.find = False

        self.UMBRAL = UMBRAL

    def set_CW(self, CW, agent_name) -> None:
        self.CW_class = CW
        self.agent_name = agent_name
        self.set_umbral = True if agent_name == "Agente Bayesiano" else False
        self.set_palace(self.palace_dict[self.agent_name])
        if self.set_umbral:
            self.CW = self.CW_class(
                self.palace, self.screen, delay=0.2, umbral=self.UMBRAL
            )
        else:
            self.CW = self.CW_class(self.palace, self.screen, delay=0.2)

    def set_palace(self, palace) -> None:
        self.palace = palace(self.screen)

    def initialize(self) -> None:
        if self.CW_class is not None:
            if self.set_umbral:
                self.CW = self.CW_class(
                    self.palace, self.screen, delay=0.2, umbral=self.UMBRAL
                )
            else:
                self.CW = self.CW_class(self.palace, self.screen, delay=0.2)

    def set_find(self, value):
        self.find = value
        if value == True and self.CW is None:
            self.find = False

    def shuffle(self):
        self.palace.shuffle()
        self.CW = self.CW_class(self.palace, self.screen)

    def add_solution(self, sol) -> None:
        self.CW.reset()
        self.CW.set_moves_lista(sol)
        self.CW.set_type("lista")
        return self.CW.perceive_and_act()

    def reset(self):
        self.palace.reset()
        self.initialize()


def main(UMBRAL) -> None:
    pygame.init()

    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    # screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Kurtz")
    font = pygame.font.Font(None, 60)
    imp = pygame.image.load("fondo.jpg").convert()

    CLOCK = pygame.time.Clock()

    button_width: int = 275
    button_height: int = 50
    button_y: int = 50
    button_x = (screen.get_width() - 5 * button_width) // 6

    jugador = Jugador(screen, UMBRAL)

    button_KB = AgentButton(
        button_x,
        button_y,
        button_width,
        button_height,
        CW_KB_Search_Pygame,
        jugador,
        "Agente KB",
    )
    button_Bayes = AgentButton(
        button_width + 2 * button_x,
        button_y,
        button_width,
        button_height,
        CW_BayesSearch_Pygame,
        jugador,
        "Agente Bayesiano",
    )

    button_find_solution = FindSolutionButton(
        2 * button_width + 3 * button_x,
        button_y,
        button_width,
        button_height,
        jugador,
        "Encontrar Solución",
    )
    button_shuffle = ShuffleButton(
        3 * button_width + 4 * button_x,
        button_y,
        button_width,
        button_height,
        jugador,
        "Cambiar Palacio",
    )

    button_reset = ResetButton(
        4 * button_width + 5 * button_x,
        button_y,
        button_width,
        button_height,
        jugador,
        "Reiniciar Palacio",
    )

    buttons = [
        button_KB,
        button_Bayes,
        button_find_solution,
        button_shuffle,
        button_reset,
    ]

    mensaje_error = MensajeError()

    # )
    running = True
    ok = True
    screen.blit(imp, (0, 0))
    getting_direction = False
    while running:
        CLOCK.tick(FPS)

        for button in buttons:
            button.draw(screen)
        if jugador.CW:
            jugador.CW.dibujar()
            if jugador.find:
                solution = jugador.CW.search()
                if solution:
                    jugador.set_find(False)
                    ok, victory = jugador.add_solution(solution)
                else:
                    mensaje_error.set_msg("No se encontró una solución")
                    mensaje_error.mostrar(screen, font)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if jugador.CW:
                        ok, victory = jugador.CW.hacer_siguiente_movimiento("x")
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    if jugador.CW:
                        if not getting_direction:
                            ok, victory = jugador.CW.hacer_siguiente_movimiento("right")
                        else:
                            getting_direction = False
                            ok, victory = jugador.CW.hacer_siguiente_movimiento(
                                " right"
                            )
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    if jugador.CW:
                        if not getting_direction:
                            ok, victory = jugador.CW.hacer_siguiente_movimiento("left")
                        else:
                            getting_direction = False
                            ok, victory = jugador.CW.hacer_siguiente_movimiento(" left")
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    if jugador.CW:
                        if not getting_direction:
                            ok, victory = jugador.CW.hacer_siguiente_movimiento("down")
                        else:
                            getting_direction = False
                            ok, victory = jugador.CW.hacer_siguiente_movimiento(" down")
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    if jugador.CW:
                        if not getting_direction:
                            ok, victory = jugador.CW.hacer_siguiente_movimiento("up")
                        else:
                            getting_direction = False
                            ok, victory = jugador.CW.hacer_siguiente_movimiento(" up")
                elif event.key == pygame.K_ESCAPE:
                    return
                if event.key == pygame.K_SPACE:
                    if jugador.CW:
                        if jugador.CW.usos_arma > 0:
                            if isinstance(jugador.CW, CW_BayesSearch_Pygame):
                                text = "Elija una dirección para disparar"
                                text_to_display = pygame.font.Font(None, 60).render(
                                    text, True, (255, 255, 255)
                                )
                                text_rect = text_to_display.get_rect(
                                    center=(screen.get_width() // 2, 150)
                                )
                                rect = pygame.Rect(
                                    screen.get_width() // 2 - 425, 115, 850, 70
                                )
                                pygame.draw.rect(screen, (0, 0, 0), rect)
                                screen.blit(text_to_display, text_rect)
                                pygame.display.update()
                                getting_direction = True
                            else:
                                ok, victory = jugador.CW.hacer_siguiente_movimiento(" ")
                        else:
                            text = "Ya no le quedan usos del arma"
                            text_to_display = pygame.font.Font(None, 60).render(
                                text, True, (255, 255, 255)
                            )
                            text_rect = text_to_display.get_rect(
                                center=(screen.get_width() // 2, 150)
                            )
                            rect = pygame.Rect(
                                screen.get_width() // 2 - 425, 115, 850, 70
                            )
                            pygame.draw.rect(screen, (0, 0, 0), rect)
                            screen.blit(text_to_display, text_rect)
                            pygame.display.update()

        for button in buttons:
            button.handle_event(event)

        if not ok:
            jugador.CW.dibujar()
            jugador.CW = None

            if victory:
                mensaje_error.set_msg("ENHORABUENA, GANASTE!!!", "GREEN")
            else:
                mensaje_error.set_msg("PERDISTE :(")
            mensaje_error.mostrar(screen, font)
            ok = True

        pygame.display.update()
