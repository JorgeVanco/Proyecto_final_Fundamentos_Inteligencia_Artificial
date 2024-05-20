class SearchAgent:
    """
    Clase del Agente de búsqueda
    """

    def __init__(self) -> None:
        self.queue = Queue()

    def evaluation_function(self, position, parent_node) -> tuple:
        """
        Función de evaluación del agente de búsqueda
        """
        count = 0

        if parent_node.CK:
            # Apremiamos que tenga al Coronel Kurtz
            count -= 50

        heuristic = 0
        if self.salida_position is not None and parent_node.CK:
            # Apremiamos que se haya encontrado la salida y se tenga al Coronel
            count -= 100

            # Si se tiene al Coronel y se conoce la salida, se convierte en A*
            heuristic = self.distance(self.salida_position, position)

        # Sumamos un paso
        steps = parent_node.steps + 1

        # Calculamos el coste
        cost = steps + count + heuristic
        return cost, steps

    def is_goal_state(self, node) -> bool:
        """
        Determina si el nodo es el estado de aceptación
        """
        return node.action == "salir"

    def create_nodes(self, posible_moves, parent_node) -> list:
        return [
            Node(
                p,
                action,
                parent_node,
                *self.evaluation_function(p, parent_node),
            )
            for action, p in posible_moves
        ]

    def distance(self, position1, position2) -> int:
        """
        Distancia de manhattan entre dos puntos
        """
        q1, q2 = position1
        p1, p2 = position2
        if q1 is None or p1 is None:
            return 0
        return abs(q1 - p1) + abs(q2 - p2)

    def get_solution(self, node) -> list:
        """
        Devuelve la solución dado el nodo final
        """
        actions = []
        while node and node.action is not None:
            actions.append(node.action)
            node = node.father
        return actions[::-1]


class Node:
    def __init__(self, position, action, father=None, cost=0, steps=0) -> None:
        self.position = position
        self.father = father
        self.action = action
        self.cost = cost
        self.steps = steps
        self.CK = self.father.CK if self.father else False

    def __repr__(self) -> str:
        return f"({self.cost}, {self.position}, {self.action})"


class Queue:
    def __init__(self) -> None:
        self.queue = []
        self.visited = []

    def add(self, node, exist_ok=False, visited_ok=False) -> None:
        """
        Añade un nodo a la cola
        """
        if (exist_ok or not self.exists(node)) and (
            visited_ok or not self.exists(node, True)
        ):
            i = 0
            position_founded = False

            # Busca la posición del nodo (está ordenada de menor a mayor)
            while i < len(self.queue) and not position_founded:
                if node.cost < self.queue[i].cost:
                    position_founded = True
                else:
                    i += 1

            # Añade el nodo en su posición
            self.queue.insert(i, node)

    def add_from_list(self, list, exist_ok=False, visited_ok=False) -> None:
        """
        Añade una lista de nodos a la cola
        """
        for node in list:
            self.add(node, exist_ok, visited_ok)

    def get(self) -> Node:
        """
        Función para obtener el siguiente de la muestra
        """
        o = self.queue.pop(0)
        self.visited.append(o)
        return o

    def is_empty(self) -> bool:
        """
        Comprueba si la cola está vacía o no
        """
        return len(self.queue) == 0

    def exists(self, object, visited=False) -> bool:
        """
        Comprueba si el nodo existe en la cola o en los nodos visitados
        """
        if visited:
            to_check = self.visited
        else:
            to_check = self.queue
        for o in to_check:
            # Comprueba que el nuevo coste no sea superior al existente
            if object.position == o.position and object.cost >= o.cost:
                return True
        return False
