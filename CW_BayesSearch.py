import time
from CW_Bayes import CW_Bayes
from SearchAgent import Node
from PalacioBayes import PalacioBayes
from SearchAgent import SearchAgent


class CW_BayesSearch(CW_Bayes, SearchAgent):
    """
    Clase del agente de búsqueda bayesiano
    """

    def __init__(self, entorno, delay=0, umbral=0.2) -> None:
        CW_Bayes.__init__(self, entorno, umbral=umbral)
        SearchAgent.__init__(self)
        self.delay = delay

    def search(self) -> list:
        """
        Ejecuta la búsqueda
        """

        # Se crea el primer nodo con la posición actual
        position = self.get_position()
        starting_node = Node(position, None)

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
        self.handle_percepts(percepts, position, self.mapas)

        # Comprobamos si se ha encontrado al Coronel
        if percepts[self.percept_indexes["CK_con_CW"]]:
            current_node.CK = True

        # Dibujamos el entorno
        self.entorno.dibujar(self.mapas, position)

        # Se consiguen los posibles movimientos
        posible_moves = self.get_posible_moves(
            percepts, position, self.mapas, self.umbral, current_node.CK
        )

        # Se crean los nuevos nodos y se añaden a la lista
        new_nodes = self.create_nodes(posible_moves, current_node)
        self.queue.add_from_list(new_nodes, False, False)


if __name__ == "__main__":
    p = PalacioBayes()
    cw = CW_BayesSearch(p)
    sol = cw.search()
    print("SOL,", sol)
    cw_lista = CW_Bayes(p, "lista")
    cw_lista.set_moves_lista(sol)
    cw_lista.perceive_and_act()

    # print("SOL", sol)
