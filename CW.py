import time


class CW:
    """
    Clase base de los agentes Capitán Willard
    """

    def __init__(self, entorno, type="user", delay=0, usos_arma=1) -> None:
        # Usos que tiene el arma del agente
        self.usos_arma = usos_arma
        # Entorno con el que interactúa el agente
        self.entorno = entorno
        self.percept_indexes = self.entorno.percept_indexes
        # Posicion inicial que tiene como referencia el agente
        # (es siempre (1,1) para él, aunque la posición real puede ser distinta)
        self.position = [1, 1]
        self.direcciones = {
            "w": "up",
            "s": "down",
            "a": "left",
            "d": "right",
            "salir": "x",
        }

        # Si interactua con usuario o recibe una lista con los pasos
        self.type = type
        self.moves_lista = []
        self.lista_index = 0

        # Tiempo entre cada paso al sacarlos de la lista moves_lista
        self.delay = delay

    def reset(self) -> None:
        self.moves_lista = []
        self.lista_index = 0
        self.position = [1, 1]

    def get_position(self):
        return tuple(self.position)

    def usar_arma(self, direccion) -> None:
        if self.usos_arma > 0:
            if direccion is not None:
                self.entorno.usar_arma(direccion)
            else:
                self.entorno.usar_arma()
            self.usos_arma -= 1

    def salir(self) -> bool:
        return self.entorno.salir()

    def get_percepts(self, position) -> list:
        """
        Consigue la lista de perceptos dada una posición
        """
        return self.entorno.get_entorno(position)

    def moverse(self, direccion) -> None:
        """
        Se mueve el personaje si se lo permite el palacio
        """
        # managed_to_move es falso si no se ha podido mover por alguna pared
        managed_to_move, survived = self.entorno.mover(direccion)
        if managed_to_move:
            if direccion == "up":
                self.position[0] -= 1
            elif direccion == "down":
                self.position[0] += 1
            elif direccion == "left":
                self.position[1] -= 1
            elif direccion == "right":
                self.position[1] += 1
        return survived

    def actuar(self, accion) -> tuple:
        """
        Actúa dada una acción
        """
        if accion.startswith(" ") or accion == "usar arma":
            # Hay dirección si empieza por " " y tiene algo más detrás
            direccion = (
                None if len(accion) == 1 or accion == "usar arma" else accion[1:]
            )
            direccion = self.direcciones.get(direccion, direccion)
            self.usar_arma(direccion)
            return True, True
        elif accion == "x" or accion == "salir":
            has_escapado = self.salir()
            return not has_escapado, has_escapado
        else:
            return self.moverse(accion), False

    def get_next_move(self) -> str:
        """
        Consigue la próxima acción a partir de input del usuario o de la lista de acciones
        """
        if self.type == "user":
            # get input from user
            accion = input("DIRECCION (WASD):").lower()
            return self.direcciones.get(accion, accion)
        elif self.type == "lista":
            i = self.lista_index
            self.lista_index += 1

            # delay
            time.sleep(self.delay)
            return self.moves_lista[i]

    def display_posible_moves(self, posible_moves) -> None:
        """
        Imprime por pantalla las posibles acciones
        """
        if posible_moves:
            print("Posible moves:", ", ".join(list(zip(*posible_moves))[0]))
        else:
            print("No possible moves")

    def get_adyacent_positions(self, position=None) -> tuple:
        """
        Devuelve las posiciones adyacentes a una posición
        """
        if position is None:
            position = self.position

        up = (position[0] - 1, position[1])
        down = (position[0] + 1, position[1])
        left = (position[0], position[1] - 1)
        right = (position[0], position[1] + 1)
        return up, down, left, right

    def set_moves_lista(self, lista) -> None:
        self.moves_lista = lista
        self.lista_index = 0

    def set_type(self, value) -> None:
        self.type = value
