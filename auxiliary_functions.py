import pygame


def is_adyacent(p, q) -> bool:
    """
    Comprueba si dos posiciones son adyacentes
    """
    return (p[0] == q[0] and abs(p[1] - q[1]) == 1) or (
        p[1] == q[1] and abs(p[0] - q[0]) == 1
    )


def mostrar_texto_medio(screen, texto: str) -> None:
    """
    Muestra el texto sobre un fondo negro en la pantalla
    """
    font = pygame.font.Font(None, 35)
    screen.fill((0, 0, 0))
    imprimir_mensaje(screen, texto, font, (255, 255, 255))
    pygame.display.update()


def imprimir_mensaje(screen, mensaje, font, color) -> None:
    """
    Imprime el mensaje en el medio de la pantalla
    """
    text = font.render(mensaje, True, (0, 0, 0))
    text_rect = text.get_rect(
        center=(screen.get_width() / 2 + 1, screen.get_height() / 2 + 1)
    )
    screen.blit(text, text_rect)

    text = font.render(mensaje, True, color)
    text_rect = text.get_rect(center=(screen.get_width() / 2, screen.get_height() / 2))
    screen.blit(text, text_rect)


def change_pos(pos, displacement_x, displacement_y) -> tuple:
    """
    Desplaza la posición
    """
    return (pos[0] + displacement_x, pos[1] + displacement_y)


def render_text_cell(text, pos, screen, font) -> None:
    """
    Imprime texto en una celda
    """
    text_to_display = font.render(text, True, (0, 0, 0))
    text_rect = text_to_display.get_rect(center=pos)
    screen.blit(text_to_display, text_rect)
