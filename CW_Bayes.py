from CW import CW
import numpy as np

from PalacioBayes import PalacioBayes


class CW_Bayes(CW):
    """
    Clase del Agente Bayesiano
    """

    def __init__(self, entorno, type="user", delay=0, umbral=0.2) -> None:
        CW.__init__(self, entorno, type, delay=delay)
        self.N = self.entorno.n

        # Tamaño del mapa
        self.MAPA_SHAPE = (self.N, self.N)

        # Número de estímulos
        self.estimulos = 5
        self.position = [0, 0]
        self.umbral = umbral
        self.has_just_shot = False

        # El prior uniforme
        self.prior_uniforme = 1 / (self.N - 1)

        self.lista_mapas = [
            "trampa_fuego",
            "trampa_pinchos",
            "trampa_dardos",
            "monstruo",
            "salida",
        ]

        # Índices de los mapas
        self.mapas_indexes = {m: i for i, m in enumerate(self.lista_mapas)}

        # Inicializamos los mapas con el prior
        self.mapas = [
            np.full((self.N, self.N), self.prior_uniforme)
            for _ in range(self.estimulos)
        ]

        self.salida_position = None

    def reset(self) -> None:
        """
        Resetea los mapas a sus valores iniciales
        """
        self.mapas = [
            np.full((self.N, self.N), self.prior_uniforme)
            for _ in range(self.estimulos)
        ]

        self.salida_position = None
        super().reset()
        self.position = [0, 0]
        self.has_just_shot = False

    def verosimilitud(self, position):
        """
        Se crea la función verosimilitud para cierta posición
        """
        # Posiciones adyacentes
        adyacent = self.get_adyacent_positions(position)

        valid_positions = set(adyacent) | {position}

        # Función verosimilitud
        f = lambda pos: 1 if pos in valid_positions else 0
        return f

    def create_mapa_verosimilitud(
        self, position, percept, p_verosimilitud=None
    ) -> np.array:
        """
        Se crea el mapa de verosimilitud para una posición y percepto
        """
        if p_verosimilitud is None:
            p_verosimilitud = self.verosimilitud(position)

        mapa_verosimilitud = np.zeros(self.MAPA_SHAPE)

        # Se recorre todo el mapa
        for k in range(self.N):
            for l in range(self.N):
                # Se calcula la verosimilitud de la posición
                ver = p_verosimilitud((k, l))

                # Si el percepto es Falso, se hace 1 - la probabilidad
                if not percept:
                    ver = 1 - ver

                # Se escribe el valor de la verosimilitud
                mapa_verosimilitud[k, l] = ver
        return mapa_verosimilitud

    def Bayes(self, mapa_verosimilitud, mapa_prior) -> np.array:
        """
        Aplica Bayes
        """
        # Calcula numerador
        numerador = mapa_verosimilitud * mapa_prior

        # El denominador es la integral (suma) del numerador
        denominador = np.sum(numerador)

        # Para no dividir por cero
        if denominador == 0:
            return numerador

        # Se devuelve la fracción
        return numerador / denominador

    def actualizar_mapa(
        self, index, percept, mapas, position, p_verosimilitud=None
    ) -> None:
        """
        Se actualizan las probabilidades de un mapa a partir de la posición y el percepto
        """
        mapa_verosimilitud = self.create_mapa_verosimilitud(
            position, percept, p_verosimilitud
        )
        mapa_prior = mapas[index]
        mapas[index] = self.Bayes(mapa_verosimilitud, mapa_prior)

    def actualizar_mapas(self, percepts, mapas, position) -> None:
        """
        Se actualizan todos los mapas del agente dados los perceptos para una posición
        """
        # Se recorren los perceptos y se actualizan los mapas asociados a cada uno
        for i, percept in enumerate(percepts[: self.estimulos]):
            self.actualizar_mapa(i, percept, mapas, position)

        # Si se oye un grito, se se pone a 0 la probabilidad de monstruo en todas las casillas
        if percepts[self.percept_indexes["grito"]]:
            mapas[self.mapas_indexes["monstruo"]] = np.zeros(self.MAPA_SHAPE)

    def handle_percepts(self, percepts, position=None, mapas=None) -> None:
        """
        Usa los perceptos para actualizar los mapas
        """
        if position is None:
            position = self.get_position()

        if mapas is None:
            mapas = self.mapas

        # Actualiza los mapas
        self.actualizar_mapas(percepts, mapas, position)

        # Si se sabe con certeza la localización de la salida, se guarda la posición
        if np.count_nonzero(mapas[self.mapas_indexes["salida"]] == 1) == 1:
            i, j = np.where(mapas[self.mapas_indexes["salida"]] == 1)
            self.salida_position = (i[0], j[0])

    def perceive_and_act(self) -> tuple:
        """
        Bucle principal del agente
        """
        ok = True
        while ok:
            # Conseguir perceptos y manejarlos
            percepts = self.get_percepts(self.get_position())
            self.handle_percepts(percepts)

            # Dibuja entorno
            self.dibujar()

            # Obtener los posibles movimientos
            posible_moves = self.get_posible_moves(
                percepts, self.get_position(), self.mapas, self.umbral
            )

            # Mostralos
            self.display_posible_moves(posible_moves)

            # Obtener la siguiente acción
            accion = self.get_next_move()

            # Obtener resultado de dicha acción
            ok, victory = self.actuar(accion)

        if victory:
            print("ENHORABUENA!!! Has conseguido salir")
        else:
            print("Has perdido")
        return ok, victory

    def get_posible_moves(
        self, percepts, position, mapas, umbral, CK_con_CW=False
    ) -> list:
        """
        Consigue la lista de posibles movimientos
        """
        positions = {5: "up", 6: "down", 7: "left", 8: "right"}

        # Lista de posibles acciones
        actions = []

        # Mira si se puede salir
        if (percepts[self.percept_indexes["CK_con_CW"]] or CK_con_CW) and mapas[
            self.mapas_indexes["salida"]
        ][position[0], position[1]] == 1:
            actions.append(("salir", (None, None)))

        # Recorre las adyacentes y comprueba que no sean paredes y sean seguras
        for i, adyacent_position in enumerate(self.get_adyacent_positions(position), 5):
            if not percepts[i] and self.is_safe(adyacent_position, mapas, umbral):
                actions.append((positions[i], adyacent_position))

        return actions

    def is_safe(self, adyacent_position, mapas, umbral) -> bool:
        """
        Establece si una posición es segura a partir del umbral
        """
        p_morir = self.get_probabilidad_de_morir(adyacent_position, mapas)
        return p_morir < umbral

    def get_probabilidad_de_morir(self, position, mapas) -> float:
        """
        Calcula la probabilidad de morir en una posición a partir de la suma de todos los mapas de probabilidad de las trampas y monstruo
        """
        i, j = position
        probabilidad_de_morir = np.sum(mapas[: self.mapas_indexes["salida"]], axis=0)[
            i, j
        ]
        return probabilidad_de_morir

    def dibujar(self) -> None:
        """
        Dibuja entorno
        """
        self.entorno.dibujar(self.mapas)

    def usar_arma(self, direccion) -> None:
        """
        Usa el arma dirigida y actualiza el mapa del monstruo según los nuevos perceptos
        """
        super().usar_arma(direccion)
        position = self.get_position()
        percepts = self.get_percepts(position)
        olor = percepts[self.percept_indexes["estimulo_monstruo"]]
        if olor:
            adyacent = self.get_adyacent_positions(position)
            direcciones = {"up": 0, "down": 1, "left": 2, "right": 3}
            casilla_disparada = adyacent[direcciones[direccion]]

            funcion_verosimilitud = lambda pos: 0 if pos == casilla_disparada else 1
            self.actualizar_mapa(
                self.mapas_indexes["monstruo"],
                olor,
                self.mapas,
                position,
                funcion_verosimilitud,
            )
        else:
            self.actualizar_mapa(
                self.mapas_indexes["monstruo"],
                olor,
                self.mapas,
                position,
            )


if __name__ == "__main__":
    p = PalacioBayes()
    p.shuffle()
    c = CW_Bayes(p)
    c.perceive_and_act()
