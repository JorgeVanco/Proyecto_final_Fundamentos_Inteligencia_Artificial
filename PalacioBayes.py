import random
import numpy as np
import pygame
from auxiliary_functions import is_adyacent, render_text_cell, change_pos


class PalacioBayes:
    """
    Clase del Palacio para el agente Bayesiano
    """

    def __init__(self, n: int = 6) -> None:
        self.n = n
        self.posibles_perceptos = [
            "estimulo_fuego",
            "estimulo_pinchos",
            "estimulo_dardos",
            "estimulo_monstruo",
            "estimulo_salida",
            "pared_arriba",
            "pared_abajo",
            "pared_izquierda",
            "pared_derecha",
            "grito",
            "CK_con_CW",
        ]

        self.indices_trampas = {"fuego": 0, "pinchos": 1, "dardos": 2}
        self.percept_indexes = {
            percept: i for i, percept in enumerate(self.posibles_perceptos)
        }
        self.shuffle()
        self.acaba_de_detonar = False

    def reset(self) -> None:
        self.CW = self.CW_start.copy()
        self.CK = self.CK_start.copy()
        self.monstruo = self.monstruo_start
        self.acaba_de_detonar = False

    def random_coords(self) -> tuple[int, int]:
        return (random.randint(1, self.n), random.randint(1, self.n))

    def shuffle(self) -> None:
        """
        Genera las posiciones aleatorias de los elementos del palacio
        """
        self.CW_start = [1, 1]
        self.CW = self.CW_start.copy()
        self.salida = None
        while self.salida is None or self.salida == tuple(self.CW):
            self.salida = self.random_coords()

        self.precipicios = [None] * len(self.indices_trampas)
        for i in range(len(self.indices_trampas)):
            while (
                self.precipicios[i] is None
                or self.precipicios[i] == tuple(self.CW)
                or self.precipicios[i] == self.salida
            ):
                self.precipicios[i] = self.random_coords()

        self.monstruo = None
        while (
            self.monstruo is None
            or self.monstruo == tuple(self.CW)
            or self.monstruo in self.precipicios
        ):
            self.monstruo = self.random_coords()
        self.monstruo_start = self.monstruo
        self.CK = None
        while (
            self.CK is None
            or self.CK == tuple(self.CW)
            or self.CK in self.precipicios
            or self.CK == self.salida
        ):
            self.CK = self.random_coords()
        self.CK = list(self.CK)
        self.CK_start = self.CK.copy()
        self.acaba_de_detonar = False

    def get_entorno(self, position=None) -> list:
        """
        Genera la lista de los perceptos para determinada posición
        percept(s) = [eF?, eP?, eD?, eM?, eS?, Pared↑?, Pared↓?, Pared←?, Pared→?, Grito?]
        """
        if position is None:
            position = tuple(self.CW)
        else:
            # Se traslada la posición dada por el agente a la del mapa
            position = (position[0] + self.CW_start[0], position[1] + self.CW_start[1])

        indice_fuego = self.indices_trampas["fuego"]
        indice_pinchos = self.indices_trampas["pinchos"]
        indice_dardos = self.indices_trampas["dardos"]
        eF = (
            is_adyacent(position, self.precipicios[indice_fuego])
            or position == self.precipicios[indice_fuego]
        )
        eP = (
            is_adyacent(position, self.precipicios[indice_pinchos])
            or position == self.precipicios[indice_pinchos]
        )
        eD = (
            is_adyacent(position, self.precipicios[indice_dardos])
            or position == self.precipicios[indice_dardos]
        )
        eM = is_adyacent(position, self.monstruo) or position == self.monstruo
        eS = is_adyacent(position, self.salida) or position == self.salida
        pared_arriba = position[0] == 1
        pared_abajo = position[0] == self.n
        pared_izquierda = position[1] == 1
        pared_derecha = position[1] == self.n
        grito = self.acaba_de_detonar and self.monstruo == (-100, -100)
        CK_con_CW = tuple(self.CK) == tuple(position)
        self.acaba_de_detonar = False

        return (
            eF,
            eP,
            eD,
            eM,
            eS,
            pared_arriba,
            pared_abajo,
            pared_izquierda,
            pared_derecha,
            grito,
            CK_con_CW,
        )

    def mover(self, direccion) -> tuple[bool, bool]:
        """
        Mueve al capitán Willard y a Kurtz(si se encuentra con Willard)
        """
        mover_CK = tuple(self.CW) == tuple(self.CK)

        managed_to_move = False
        if direccion == "up" and not self.CW[0] == 1:
            self.CW[0] -= 1
            managed_to_move = True
        elif direccion == "down" and not self.CW[0] == self.n:
            self.CW[0] += 1
            managed_to_move = True
        elif direccion == "left" and not self.CW[1] == 1:
            self.CW[1] -= 1
            managed_to_move = True
        elif direccion == "right" and not self.CW[1] == self.n:
            self.CW[1] += 1
            managed_to_move = True
        if mover_CK:
            self.CK = self.CW

        return managed_to_move, self.check_state(tuple(self.CW))

    def salir(self) -> bool:
        if self.CW == self.CK and tuple(self.CW) == self.salida:
            return True
        else:
            return False

    def check_state(self, position) -> bool:
        if position in self.precipicios or position == self.monstruo:
            return False

        return True

    def usar_arma(self, direccion) -> None:
        """
        Se usa el arma
        """
        self.acaba_de_detonar = True

        if direccion is None:
            if is_adyacent(self.CW, self.monstruo):
                self.monstruo = (-100, -100)
        else:
            CW = self.CW.copy()
            if direccion == "up":
                CW[0] -= 1
            elif direccion == "down":
                CW[0] += 1
            elif direccion == "left":
                CW[1] -= 1
            elif direccion == "right":
                CW[1] += 1

            if self.monstruo == tuple(CW):
                self.monstruo = (-100, -100)

    def dibujar(self, mapas, position=None) -> None:
        """
        Dibuja el palacio en la terminal
        """
        if position is None:
            position = self.CW
            start = self.CW_start
            p1, p2 = position
            position = (p1 - start[0], p2 - start[1])

        suma = np.sum(mapas, axis=0)
        i, j = position

        dibujo = ""
        for k in range(self.n):
            for l in range(self.n):
                if (k, l) == (i, j):
                    if self.CW == self.CK:
                        dibujo += "|CW  CK|"
                    else:
                        dibujo += "|  CW  |"
                elif (k, l) == (self.salida[0] - 1, self.salida[1] - 1):
                    dibujo += f"|S {suma[k, l]:0.02f}|"
                else:
                    dibujo += f"| {suma[k, l]:0.02f} |"
            dibujo += "\n"
        print(dibujo)


class PalacioBayesPygame(PalacioBayes):
    """
    Clase Palacio para el agente bayesiano en Pygame
    """

    def __init__(self, screen, n=6, font=None) -> None:
        self.screen = screen
        self.font = font if font else pygame.font.Font(None, 28)
        PalacioBayes.__init__(self, n)

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

    def dibujar(self, mapas, position=None, umbral=None) -> None:
        """
        Dibuja el palacio en Pygame
        """
        if position is None:
            position = self.CW
            start = self.CW_start
            p1, p2 = position
            position = (p1 - start[0], p2 - start[1])

        if umbral == None:
            umbral = 0.2

        margin_top = 200
        margin_bottom = 100
        margin_side = 200

        width = int(self.screen.get_width() - margin_side)
        height = int(self.screen.get_height() - margin_top - margin_bottom)

        x_start = margin_side // 2
        y_start = margin_top
        block_width = width // (self.n)
        block_height = height // (self.n)

        displacement_x = (block_width // 2) * 0.6
        displacement_y = (block_height // 2) * 0.7

        color = self.colors["WHITE"]

        suma = np.sum(mapas, axis=0)
        i, j = position

        y = y_start
        for k in range(self.n):
            x = x_start
            for l in range(self.n):
                text = ""
                texts_to_draw = []

                rect = pygame.Rect(x, y, block_width, block_height)
                color = (
                    self.colors["WHITE"]
                    if suma[k, l] == 0
                    else self.colors["YELLOW"]
                    if suma[k, l] < umbral
                    else self.colors["RED"]
                    if suma[k, l] == 1
                    else self.colors["ORANGE"]
                )
                if (k, l) == (i, j):
                    if self.CW == self.CK:
                        text = "CW CK"
                        color = self.colors["GREEN"]
                    else:
                        text = "CW"
                        color = self.colors["BLUE"]
                    texts_to_draw.append((text, rect.center))

                else:
                    if mapas[3][k, l] > 0:
                        pos = change_pos(rect.center, -displacement_x, -displacement_y)
                        texts_to_draw.append((f"M:{mapas[3][k, l]:0.02f}", pos))
                    if mapas[0][k, l] > 0:
                        pos = change_pos(rect.center, displacement_x, -displacement_y)
                        texts_to_draw.append((f"F:{mapas[0][k, l]:0.02f}", pos))

                    if mapas[1][k, l] > 0:
                        pos = change_pos(rect.center, -displacement_x, displacement_y)
                        texts_to_draw.append((f"P:{mapas[1][k, l]:0.02f}", pos))

                    if mapas[2][k, l] > 0:
                        pos = change_pos(rect.center, displacement_x, displacement_y)
                        texts_to_draw.append((f"D:{mapas[2][k, l]:0.02f}", pos))

                    if mapas[4][k, l] > 0:
                        texts_to_draw.append((f"S:{mapas[4][k, l]:0.02f}", rect.center))
                        if (
                            mapas[4][k, l] >= 0.3
                            and not np.sum(mapas[:-1], axis=0)[k, l] >= umbral
                        ):
                            color = self.colors["GREEN"]

                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, self.colors["GRAY"], rect, 2)

                for t, p in texts_to_draw:
                    render_text_cell(t, p, self.screen, self.font)

                x += block_width
            y += block_height
        pygame.display.update()
