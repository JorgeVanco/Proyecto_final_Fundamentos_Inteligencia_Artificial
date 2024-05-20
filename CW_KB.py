import re
import copy

from CW import CW

# B -> Brisa
# O -> Olor
# R -> Resplandor
# P -> Precipicio
# M -> Monstruo
# S -> Salida
# [B, O, R, P, M, S, PU, PD, PL, PR, MU, MD, MR, ML, SU, SD, SL, SR]
# [-1, -1, -1, -1, -1, -1]
# [0, 0, 1]
# [0, 0, 0]


class CW_KB(CW):
    def __init__(self, entorno, delay=0) -> None:
        CW.__init__(self, entorno, delay=delay)
        self.KB = dict()
        self.KB_format = [
            "B",
            "O",
            "R",
            "P",
            "M",
            "S",
            "PU",
            "PD",
            "PL",
            "PR",
            "MU",
            "MD",
            "ML",
            "MR",
            "SU",
            "SD",
            "SL",
            "SR",
        ]
        # Indices de cada opción del KB
        self.indexes = {self.KB_format[i]: i for i in range(len(self.KB_format))}

        # Clausulas base
        self.base_clauses = set()
        self.set_base_clauses()

        # Estados de las celdas
        self.room_states = dict()

        # Posiciones de objetos
        self.monster_position = None
        self.salida_position = None

    def reset(self) -> None:
        self.base_clauses = set()
        self.room_states = dict()
        self.monster_position = None
        self.salida_position = None
        super().reset()

    def get_KB_copy(
        self,
    ) -> dict:
        return copy.deepcopy(self.KB)

    def get_room_states_copy(self) -> dict:
        return copy.deepcopy(self.room_states)

    def handle_percepts(self, percepts, position, KB, room_states) -> tuple:
        # Manejar las paredes poniendo su información a 0
        self.set_wall_info(position, percepts, KB)

        # Añadir información al KB
        self.add_knowledge_from_percepts(percepts, KB, position)

        # Realizar inferencia
        self.ask_everything(position, KB, room_states)

        return KB, room_states

    def perceive_and_act(self) -> tuple:
        """
        Bucle principal del agente
        """
        # Poner como segura la celda inicial
        self.set_clear(self.get_position(), self.KB, self.room_states)
        ok = True
        while ok:
            position = self.get_position()
            # Conseguir perceptos
            percepts = self.get_percepts(position)

            # Actualizar todo con los perceptos
            self.handle_percepts(percepts, position, self.KB, self.room_states)

            # Dibujar entorno
            self.dibujar()

            # Obtener los posibles movimientos
            posible_moves = self.get_posible_moves(percepts, position)
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

    def set_base_clauses(self) -> None:
        """
        Implementa las cláusulas base que cada celda debe tener
        """
        for a, b in [("B", "P"), ("O", "M"), ("R", "S")]:
            # B -> (PU V PD V PL V PR) and so on...
            self.base_clauses.add(
                self.parse_proposition(f"¬{a} V {b}U V {b}D V {b}L V {b}R")
            )

            # (PU V PD V PL V PR) -> B
            for k in ["U", "D", "L", "R"]:
                self.base_clauses.add(self.parse_proposition(f"{a} V ¬{b}{k}"))

    def parse_proposition(self, proposition: str) -> tuple:
        """
        Convierte una proposición de texto al formato de cada cláusula
        """
        # Regex para dividir la proposición
        pattern = r"\s(?![^(]*\))"
        splitted = re.split(pattern, proposition)

        # Creo el vector de -1
        parsed = [-1 for _ in range(len(self.indexes))]

        # Recorremos los literales
        for p in splitted:
            if p.startswith("-") or p.startswith("¬") or p.startswith("~"):
                parsed[self.indexes[p[1:]]] = 0
            elif p in self.indexes:
                parsed[self.indexes[p]] = 1
        return tuple(parsed)

    def add_to_KB(self, room, knowledge=None, KB=None) -> None:
        """
        Añade conocimiento a una celda
        """
        if KB is None:
            KB = self.KB
        if room not in KB:
            # Si la celda no existe, se añaden as cláusulas base al KB
            KB[room] = set(self.base_clauses)

        if knowledge is not None:
            # Si knowledge es una string, se convierte en el vector
            if isinstance(knowledge, str):
                knowledge = self.parse_proposition(knowledge)
            KB[room].add(knowledge)

    def remove_from_KB(self, room, knowledge, KB) -> None:
        """
        Quita conocimiento de una celda
        """
        if KB is None:
            KB = self.KB
        if room in KB:
            if isinstance(knowledge, str):
                # Si knowledge es una string, se convierte en el vector
                knowledge = self.parse_proposition(knowledge)
            KB[room] -= {knowledge}

    def not_clause(self, clause) -> str:
        """
        Nega una cláusula
        """
        if clause.startswith("-") or clause.startswith("¬") or clause.startswith("~"):
            clause = clause[1:]
        else:
            clause = "¬" + clause

        return clause

    def convert_to_clause(self, c) -> str:
        """
        Convierte un vector en un string de una cláusula para que se pueda leer
        """
        clause = ""
        for i, v in enumerate(c):
            if v == 0:
                clause += "¬" + self.KB_format[i] + " V "
            elif v == 1:
                clause += self.KB_format[i] + " V "
        return clause[:-3]

    def ask(self, room, alpha, KB) -> bool:
        """
        Applies resolution and answers if KB entails alpha
        """
        if KB is None:
            KB = self.KB
        if room not in KB:
            self.add_to_KB(room, KB)
        clauses = set(KB[room])

        # Añade el alpha negado
        clauses.add(self.parse_proposition(self.not_clause(alpha)))

        # Algoritmo de resolución
        new = set()
        while True:
            clause_list = list(clauses)

            for i, ci in enumerate(clause_list):
                for cj in clause_list[i + 1 :]:
                    resolvents = self.PL_resolve(ci, cj)
                    if -len(self.indexes) in [sum(r) for r in resolvents]:
                        return True
                    new = new | resolvents

            if new <= clauses:
                return False
            clauses = clauses | new

    def PL_resolve(self, qi, qj) -> set:
        """
        Calcula los resolvents dadas dos cláusulas
        """
        resolvents = set()
        for i, q in enumerate(qi):
            if q != -1 and qj[i] != -1 and q == (not qj[i]):
                resolvent = [
                    self.get_bit_value_pl_resolve(qi, qj, k, i) for k in range(len(qi))
                ]
                if None not in resolvent:
                    resolvents.add(tuple(resolvent))

        return resolvents

    def get_bit_value_pl_resolve(self, qi, qj, k, i) -> int:
        """
        Calcula el valor de una posición del resolvente
        """
        if k == i:
            return -1
        elif qi[k] == -1:
            return qj[k]
        elif qj[k] == -1:
            return qi[k]
        elif qj[k] != qi[k]:
            return None
        else:
            return qi[k] or qj[k]

    def percepts_to_knowledge(self, percepts) -> list:
        """
        Dados los perceptos, crea las cláusulas asociadas a esos perceptos
        Devuelve una lista porque es una conjunción de cláusulas
        """
        # conocimientos de perceptos de brisa, olor, resplandor
        return [
            tuple([-1 if k != i else percepts[i] for k in range(len(self.KB_format))])
            for i in range(3)
        ]

    def add_knowledge_from_percepts(self, percepts, KB, position=None) -> None:
        """
        Añade conocimiento al KB a partir de los perceptos
        """
        # Si se ha percibido un grito, se elimina al monstruo
        grito = percepts[self.percept_indexes["grito"]]
        if grito:
            self.remove_from_KB(position, "O", KB)
            if self.monster_position is not None:
                self.remove_from_KB(self.monster_position, "M", KB)
                self.room_states[self.monster_position]["M"] = 0

        # Recorrer las cláusulas obtenidas a partir de los perceptos y añadirlas al KB
        for knowledge in self.percepts_to_knowledge(percepts):
            self.add_to_KB(position, knowledge, KB)

    def set_clear(self, cell, KB, room_states, also_S=True) -> None:
        if also_S:
            max_index = 6
        else:
            max_index = 5
        for i in self.KB_format[3:max_index]:
            self.add_to_KB(cell, "¬" + i, KB)
            if cell not in room_states:
                room_states[cell] = dict()
            room_states[cell][i] = 0

    def ask_everything(self, cell, KB, room_states) -> None:
        """
        Hace las preguntas necesarias a la celda para inferir información de las celdas adyacentes
        """
        # Actualizamos información de la celda porque igual se tiene nueva información
        # de las celdas de alrededor que no está añadida
        self.update_KB(cell, KB, room_states)

        # conseguimos celdas adyacentes
        adyacent = self.get_adyacent_positions(cell)

        # Recorremos la información de cada objeto para arriba, abajo, izquierda, derecha
        for i, q in enumerate(self.KB_format[6:]):
            # Sacamos la celda adyacente adecuada
            cell_adyacent = adyacent[(i) % 4]

            # Si no se sabe ya la respuesta, se pregunta
            if q[0] not in room_states.get(cell_adyacent, {}):
                # Preguntamos a la celda
                KB_entails_q = self.ask(cell, q, KB)

                # Si es un sí
                if KB_entails_q:
                    # Ponemos propiedad a la celda adyacente
                    self.set_adyacent_cells_property(
                        cell_adyacent, q[0], 1, KB, room_states
                    )

                else:
                    # Preguntamos lo contrario a la celda
                    KB_entails_not_q = self.ask(cell, "¬" + q, KB)
                    # Si es un sí
                    if KB_entails_not_q:
                        # Ponemos propiedad a la celda adyacente
                        self.set_adyacent_cells_property(
                            cell_adyacent, q[0], 0, KB, room_states
                        )

    def set_adyacent_cells_property(
        self, adyacent_position, property, value, KB, room_states
    ) -> None:
        """
        Establece una propiedad de la celda adyacente
        """

        # Negamos la cláusula si es necesario
        proposition = property if value else "¬" + property

        # Añadimos al KB
        self.add_to_KB(adyacent_position, proposition, KB)

        # Establecemos el estado de la celda
        if adyacent_position not in room_states:
            room_states[adyacent_position] = dict()
        room_states[adyacent_position][property] = value

        # Si es monstruo o salida, guardamos la posición
        if property == "M" and value == 1:
            self.monster_position = adyacent_position
        elif property == "S" and value == 1:
            self.salida_position = adyacent_position

    def update_KB(self, cell, KB, room_states) -> None:
        """
        Actualiza la información de la celda a partir de las celdas de alrededor
        """
        positions = {0: "U", 1: "D", 2: "L", 3: "R"}

        # Ponemos la posición como limpia, a excepción de la salida
        self.set_clear(cell, KB, room_states, also_S=False)

        # Recorremos las celdas adyacentes
        for p, adyacent in enumerate(self.get_adyacent_positions(cell)):
            # Se consigue el estado de la celda adyacente, está vacío si no se ha añadido antes
            state = room_states.get(adyacent, {})

            # Se recorren los objetos del estado
            for s, v in state.items():
                proposition = s + positions[p]
                if v == 0:
                    proposition = "¬" + proposition

                # Se añade la información al KB de la celda
                self.add_to_KB(cell, proposition, KB)

    def set_wall_info(self, position, percepts, KB) -> None:
        """
        Dada una posición, comprueba si hay paredes gracias a los perceptos y declara la información de estas celdas
        a las que no se pueden acceder
        """
        positions = {3: "U", 4: "D", 5: "L", 6: "R"}
        # Recorremos las posiciones adyacentes, guardando el índice para saber su posición
        for i, adyacent_position in enumerate(self.get_adyacent_positions(position), 3):
            # Si es una pared
            if percepts[i]:
                # Set to 0 everything on that cell
                for j in range(len(self.KB_format)):
                    clause = [-1 for _ in range(len(self.KB_format))]
                    clause[j] = 0
                    self.add_to_KB(adyacent_position, tuple(clause), KB)

                # Set to 0 everything on cell about adyacent
                for k in ["P", "M", "S"]:
                    proposition = "¬" + k + positions[i]
                    self.add_to_KB(position, proposition, KB)

    def get_posible_moves(
        self, percepts, position=None, KB=None, room_states=None, CK_con_CW=False
    ) -> list:
        """
        Consigue la lista de posibles movimientos
        """
        if position is None:
            position = self.get_position()

        if room_states is None:
            room_states = self.room_states

        if KB is None:
            KB = self.KB

        # Lista de posibles acciones
        actions = []

        positions = {3: "up", 4: "down", 5: "left", 6: "right"}

        # Mira si se puede salir
        if (percepts[self.percept_indexes["CK_con_CW"]] or CK_con_CW) and room_states[
            position
        ].get("S", 0):
            actions.append(("salir", (None, None)))

        # Comprueba si se puede usar el arma
        if percepts[self.percept_indexes["fetido_olor"]]:
            actions.append(("usar arma", position))

        # Recorre las adyacentes y comprueba que no sean paredes y sean seguras
        for i, adyacent_position in enumerate(self.get_adyacent_positions(position), 3):
            if not percepts[i] and self.is_safe(adyacent_position, room_states):
                actions.append((positions[i], adyacent_position))

        return actions

    def is_safe(self, position, room_states) -> bool:
        """
        Determina si una posición es segura o no
        """
        if position is None:
            position = self.get_position()

        if room_states is None:
            room_states = self.room_states

        room_state = room_states.get(position, None)
        return (
            room_state is not None  # Si se tiene información
            and not room_state.get("M", 1)  # Si no está el monstruo
            and not room_state.get("P", 1)  # Si no hay un precipicio
        )

    def dibujar(self) -> None:
        """
        Dibuja el entorno
        """
        self.entorno.dibujar(self.room_states)


from Palacio import Palacio

if __name__ == "__main__":
    palacio = Palacio()
    # palacio.shuffle()
    p = CW_KB(palacio)
    p.perceive_and_act()
