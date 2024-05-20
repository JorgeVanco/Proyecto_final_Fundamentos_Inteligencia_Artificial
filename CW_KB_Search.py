import time
from SearchAgent import Node
from Palacio import Palacio
from CW_KB import CW_KB
from SearchAgent import SearchAgent


class CW_KB_Search(CW_KB, SearchAgent):
    """
    Clase del agente de búsqueda basado en conocimiento
    """

    def __init__(self, entorno, delay=0) -> None:
        CW_KB.__init__(self, entorno)
        SearchAgent.__init__(self)
        self.delay = delay

    def search(self) -> list:
        """
        Ejecuta la búsqueda
        """

        # Se crea el primer nodo con la posición actual
        starting_node = Node(
            self.get_position(),
            None,
        )

        # Ponemos la habitación como segura
        self.set_clear(
            starting_node.position,
            self.KB,
            self.room_states,
        )

        # Añadimos a la cola de prioridad el nodo
        self.queue.add(starting_node)

        found_path = False

        # Mientras haya nodos en la cola y no se haya encontrado el camino
        while not self.queue.is_empty() and not found_path:
            # Conseguimos siguiente nodo
            node = self.queue.get()

            # Comprobamos si es el estado de aceptación
            found_path = self.is_goal_state(node)

            if not found_path:
                # Añadimos los siguientes nodos a la cola de prioridad
                self.expand_node(node)
            time.sleep(self.delay)

        if not found_path:
            return None
        else:
            return self.get_solution(node)

    def expand_node(self, current_node) -> None:
        """
        Añade los siguientes posibles nodos a la cola de prioridad dado un nodo
        """

        position = current_node.position

        # Se consiguen los perceptos y se manejan
        percepts = self.get_percepts(position)
        self.handle_percepts(percepts, position, self.KB, self.room_states)

        # Comprobamos si se ha encontrado al Coronel
        if percepts[self.percept_indexes["CK_con_CW"]]:
            current_node.CK = True

        # Se establece la posición del coronel para dibujarlo con el Capitán
        CK = None if not current_node.CK else position

        # Dibujamos el entorno
        self.entorno.dibujar(self.room_states, position, CK)

        # Se consiguen los posibles movimientos
        posible_moves = self.get_posible_moves(
            percepts, position, self.KB, self.room_states, current_node.CK
        )

        # Se crean los nuevos nodos y se añaden a la lista
        new_nodes = self.create_nodes(posible_moves, current_node)
        self.queue.add_from_list(new_nodes, exist_ok=False, visited_ok=False)


if __name__ == "__main__":
    p = Palacio()
    cw = CW_KB_Search(p)
    sol = cw.search()
    print(sol)
    cw.set_type("lista")
    cw.set_moves_lista(sol)
    cw.perceive_and_act()
    print("SOL", sol)
