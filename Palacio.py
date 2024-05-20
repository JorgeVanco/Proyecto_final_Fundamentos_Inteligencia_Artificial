import random
import pygame
from auxiliary_functions import is_adyacent


class Palacio:
    """
    Clase de Palacio del Agente KB
    """

    def __init__(self, n: int = 6, n_precipicios=3) -> None:
        self.n = n
        self.posibles_perceptos = [
            "brisa",
            "fetido_olor",
            "resplandor",
            "pared_arriba",
            "pared_abajo",
            "pared_izquierda",
            "pared_derecha",
            "grito",
            "CK_con_CW",
        ]
        self.N_precipicios = n_precipicios

        # Se inicializa aleatoriamente las posiciones de los objetos en el palacio.
        self.shuffle()
        self.percept_indexes = {
            percept: i for i, percept in enumerate(self.posibles_perceptos)
        }

        self.acaba_de_detonar = False

    def reset(self) -> None:
        """
        Resetea los valores de las posiciones para volver a empezar
        """
        self.CW = self.CW_start.copy()
        self.CK = self.CK_start.copy()
        self.monstruo = self.monstruo_start
        self.acaba_de_detonar = False

    def random_coords(self) -> tuple[int, int]:
        """
        Inicialiaza coordenadas aleatorias dentro del palacio
        """
        return (random.randint(1, self.n), random.randint(1, self.n))

    def shuffle(self) -> None:
        """
        Genera las posiciones aleatorias de los elementos del palacio
        """
        self.CW_start = list(self.random_coords())
        self.CW = self.CW_start.copy()

        self.salida = None
        while self.salida is None or self.salida == tuple(self.CW):
            self.salida = self.random_coords()

        self.precipicios = []
        while len(self.precipicios) != self.N_precipicios:
            coord = self.random_coords()
            if (
                coord != tuple(self.CW)
                and coord != self.salida
                and coord not in self.precipicios
            ):
                self.precipicios.append(coord)

        self.monstruo = None
        while (
            self.monstruo is None
            or coord == tuple(self.CW)
            or coord == self.salida
            or self.monstruo in self.precipicios
        ):
            self.monstruo = self.random_coords()
        self.monstruo_start = self.monstruo

        self.CK = None
        while (
            self.CK is None
            or (self.CK) == list(self.CW)
            or self.CK == self.monstruo
            or self.CK in self.precipicios
        ):
            self.CK = self.random_coords()

        self.CK = list(self.CK)
        self.CK_start = self.CK.copy()

        self.acaba_de_detonar = False

    def get_entorno(self, position=None) -> list:
        """
        Genera la lista de los perceptos para determinada posición
        """
        if position is None:
            position = self.CW
        else:
            # Se traslada la posición dada por el agente a la del mapa
            position = (
                position[0] - 1 + self.CW_start[0],
                position[1] - 1 + self.CW_start[1],
            )

        brisa = (
            any(is_adyacent(position, p) for p in self.precipicios)
            or tuple(position) in self.precipicios
        )
        fetido_olor = (
            is_adyacent(position, self.monstruo) or tuple(position) == self.monstruo
        )
        resplandor = is_adyacent(position, self.salida)
        pared_arriba = position[0] == 1
        pared_abajo = position[0] == self.n
        pared_izquierda = position[1] == 1
        pared_derecha = position[1] == self.n
        grito = self.acaba_de_detonar and self.monstruo == (-100, -100)
        CK_con_CW = tuple(self.CK) == tuple(position)
        self.acaba_de_detonar = False

        return (
            brisa,
            fetido_olor,
            resplandor,
            pared_arriba,
            pared_abajo,
            pared_izquierda,
            pared_derecha,
            grito,
            CK_con_CW,
        )

    def mover(self, direccion):
        """
        Mueve al capitán Willard y a Kurtz(si se encuentra con Willard)
        """
        mover_CK = self.CW == self.CK

        CW = self.CW
        CK = self.CK
        managed_to_move = False
        if direccion == "up" and not CW[0] == 1:
            CW[0] -= 1
            managed_to_move = True
        elif direccion == "down" and not CW[0] == self.n:
            CW[0] += 1
            managed_to_move = True
        elif direccion == "left" and not CW[1] == 1:
            CW[1] -= 1
            managed_to_move = True
        elif direccion == "right" and not CW[1] == self.n:
            CW[1] += 1
            managed_to_move = True

        if mover_CK:
            self.CK = CW

        return managed_to_move, self.check_state()

    def salir(self) -> bool:
        if self.CW == self.CK and tuple(self.CW) == self.salida:
            return True
        else:
            return False

    def check_state(self) -> bool:
        position = tuple(self.CW)
        if position in self.precipicios or position == self.monstruo:
            return False

        return True

    def usar_arma(self) -> None:
        self.acaba_de_detonar = True
        if is_adyacent(self.CW, self.monstruo):
            self.monstruo = (-100, -100)

    def dibujar(self, states, CW=None, CK=None) -> None:
        """
        Dibuja el palacio en la terminal
        """
        if CW is None:
            CW = self.CW
        else:
            CW = (
                CW[0] - 1 + self.CW_start[0],
                CW[1] - 1 + self.CW_start[1],
            )

        if CK is None:
            CK = self.CK
        else:
            # Trasladar las coordenadas dadas por el agente a las realess
            CK = (
                CK[0] - 1 + self.CW_start[0],
                CK[1] - 1 + self.CW_start[1],
            )
        dibujo = ""
        traps = {"P", "M", "S"}
        i_start, j_start = self.CW_start
        for i in range(1, self.n + 1):
            for j in range(1, self.n + 1):
                # trasladar la posicion real a la del agente
                position = (i + 1 - i_start, j + 1 - j_start)

                # obtener la información que tiene el agente de la sala a dibujar
                state = states.get(position, {})

                if len(state) == 0:
                    # Si no sabe nada de la sala
                    dibujo += "| xx |"
                elif len(state) < 3 and not 1 in state.values():
                    # Si sabe algo de la sala
                    doubt = list(traps - set(list(state.keys())))
                    print(doubt, states.get(position))
                    if len(doubt) == 1:
                        dibujo += f"| {doubt[0]}? |"
                    else:
                        dibujo += f"|{doubt[0]}?{doubt[1]}?|"

                else:
                    # Si sabe todo de la sala
                    if [i, j] == list(CK):
                        if self.CK == CW:
                            dibujo += "|CWCK|"
                        else:
                            dibujo += "|    |"
                    elif [i, j] == list(CW):
                        dibujo += "| CW |"
                    elif (i, j) in self.precipicios:
                        dibujo += "| P  |"
                    elif (i, j) == self.monstruo:
                        dibujo += "| M  |"
                    elif (i, j) == self.salida:
                        dibujo += "| S  |"
                    else:
                        dibujo += "|    |"
            dibujo += "\n"
        print(dibujo)


class PalacioPygame(Palacio):
    """
    Clase Palacio para el agente KB en Pygame
    """

    def __init__(self, screen, n=6, font=None):
        self.screen = screen

        self.font = font if font else pygame.font.Font(None, 28)
        Palacio.__init__(self, n)

        self.colors = {
            "WHITE": (255, 255, 255),
            "BLACK": (0, 0, 0),
            "GRAY": (169, 169, 169),
            "RED": (255, 0, 0),
            "BLUE": (0, 0, 255),
            "GREEN": (0, 255, 0),
            "YELLOW": (255, 255, 0),
            "ORANGE": (255, 140, 0),
        }

    def dibujar(self, states, CW=None, CK=None) -> None:
        """
        Dibuja el palacio en Pygame
        """
        if CW is None:
            CW = self.CW
        else:
            CW = (
                CW[0] - 1 + self.CW_start[0],
                CW[1] - 1 + self.CW_start[1],
            )

        if CK is None:
            CK = self.CK
        else:
            CK = (
                CK[0] - 1 + self.CW_start[0],
                CK[1] - 1 + self.CW_start[1],
            )

        traps = {"P", "M", "S"}
        i_start, j_start = self.CW_start
        margin_top = 200
        margin_bottom = 100
        margin_side = 200

        # Se calcula todo en cada iteración por si se redimensiona la pantalla
        width = int(self.screen.get_width() - margin_side)
        height = int(self.screen.get_height() - margin_top - margin_bottom)
        x_start = margin_side // 2
        y_start = margin_top
        block_width = width // (self.n)
        block_height = height // (self.n)

        color = self.colors["WHITE"]

        y = y_start
        for i in range(1, self.n + 1):
            x = x_start
            for j in range(1, self.n + 1):
                text = ""

                position = (i + 1 - i_start, j + 1 - j_start)
                state = states.get(position, {})

                if len(state) == 0:
                    color = self.colors["BLACK"]
                    text = "xx"

                elif len(state) < 3:
                    doubt = list(traps - set(list(state.keys())))
                    if len(doubt) == 1:
                        text = f"{doubt[0]}?"
                    else:
                        text = f"{doubt[0]}?{doubt[1]}?"
                    color = self.colors["GRAY"]

                else:
                    if [i, j] == list(CK):
                        if self.CK == CW:
                            text = "CW CK"
                            color = self.colors["GREEN"]
                        else:
                            color = self.colors["WHITE"]
                    elif [i, j] == list(CW):
                        text = "CW"
                        color = self.colors["BLUE"]
                    elif (i, j) in self.precipicios:
                        text = "P"
                        color = self.colors["RED"]
                    elif (i, j) == self.monstruo:
                        text = "M"
                        color = self.colors["RED"]

                    elif (i, j) == self.salida:
                        text = "S"
                        color = self.colors["GREEN"]

                    else:
                        text = ""
                        color = self.colors["WHITE"]

                rect = pygame.Rect(x, y, block_width, block_height)
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, self.colors["GRAY"], rect, 2)
                text_to_display = self.font.render(text, True, self.colors["BLACK"])
                text_rect = text_to_display.get_rect(center=rect.center)
                self.screen.blit(text_to_display, text_rect)
                x += block_width
            y += block_height
        pygame.display.update()
