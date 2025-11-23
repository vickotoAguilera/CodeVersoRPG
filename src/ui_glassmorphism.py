"""
========================================
UI GLASSMORPHISM - Sistema de Ventanas con Efecto de Vidrio
========================================

Funciones helper para crear ventanas con efecto glassmorphism
en todo el juego de forma consistente.

Uso:
    from src.ui_glassmorphism import dibujar_ventana_glass
    
    dibujar_ventana_glass(
        surface=pantalla,
        rect=mi_rect,
        titulo="Mi Ventana",
        color_acento=(100, 150, 255),
        alpha=230
    )
"""

import pygame

from typing import Tuple, Optional

# Colores predefinidos para glassmorphism
COLOR_GLASS_BG = (40, 40, 60)  # Fondo del vidrio
COLOR_GLASS_BORDER = (100, 100, 150)  # Borde brillante
COLOR_GLASS_SHADOW = (0, 0, 0)  # Sombra
COLOR_TEXTO = (255, 255, 255)  # Texto blanco

# Colores de acento predefinidos por tipo de ventana
COLORES_ACENTO = {
    "magia": (150, 80, 200),      # Purpura
    "items": (80, 200, 150),      # Verde
    "victoria": (255, 200, 50),   # Dorado
    "habilidades": (100, 150, 255),  # Azul
    "menu": (80, 200, 255),       # Cyan
    "dialogo": (120, 120, 140),   # Gris
    "acciones": (80, 120, 200),   # Azul oscuro
    "cofre": (200, 150, 80),      # Marron dorado
}


def dibujar_sombra_glass(surface: pygame.Surface, rect: pygame.Rect, 
                         offset: int = 4, blur_alpha: int = 80):
    """
    Dibuja una sombra suave detras de una ventana
    
    Args:
        surface: Superficie donde dibujar
        rect: Rectangulo de la ventana
        offset: Desplazamiento de la sombra (px)
        blur_alpha: Transparencia de la sombra (0-255)
    """
    sombra = pygame.Surface((rect.width + offset * 2, rect.height + offset * 2))
    sombra.set_alpha(blur_alpha)
    sombra.fill(COLOR_GLASS_SHADOW)
    surface.blit(sombra, (rect.x - offset, rect.y - offset))


def dibujar_fondo_glass(surface: pygame.Surface, rect: pygame.Rect,
                        alpha: int = 230, color_bg: Tuple[int, int, int] = COLOR_GLASS_BG):
    """
    Dibuja el fondo semi-transparente de una ventana glassmorphism
    
    Args:
        surface: Superficie donde dibujar
        rect: Rectangulo de la ventana
        alpha: Transparencia del fondo (0-255)
        color_bg: Color del fondo RGB
    """
    fondo = pygame.Surface((rect.width, rect.height))
    fondo.set_alpha(alpha)
    fondo.fill(color_bg)
    surface.blit(fondo, (rect.x, rect.y))


def dibujar_borde_glass(surface: pygame.Surface, rect: pygame.Rect,
                        color_borde: Tuple[int, int, int] = COLOR_GLASS_BORDER,
                        grosor: int = 2, radio: int = 10):
    """
    Dibuja el borde brillante de una ventana glassmorphism
    
    Args:
        surface: Superficie donde dibujar
        rect: Rectangulo de la ventana
        color_borde: Color del borde RGB
        grosor: Grosor del borde (px)
        radio: Radio de las esquinas redondeadas (px)
    """
    pygame.draw.rect(surface, color_borde, rect, grosor, border_radius=radio)


def dibujar_titulo_glass(surface: pygame.Surface, rect: pygame.Rect,
                         titulo: str, color_acento: Tuple[int, int, int],
                         altura_titulo: int = 35, alpha_titulo: int = 180):
    """
    Dibuja la barra de titulo con color de acento
    
    Args:
        surface: Superficie donde dibujar
        rect: Rectangulo de la ventana
        titulo: Texto del titulo
        color_acento: Color de acento RGB
        altura_titulo: Altura de la barra de titulo (px)
        alpha_titulo: Transparencia de la barra (0-255)
    """
    # Barra de titulo
    titulo_surface = pygame.Surface((rect.width, altura_titulo))
    titulo_surface.set_alpha(alpha_titulo)
    titulo_surface.fill(color_acento)
    surface.blit(titulo_surface, (rect.x, rect.y))
    
    # Texto del titulo
    fuente = pygame.font.Font(None, 24)
    texto = fuente.render(titulo, True, COLOR_TEXTO)
    surface.blit(texto, (rect.x + 10, rect.y + 8))


def dibujar_ventana_glass(surface: pygame.Surface, rect: pygame.Rect,
                          titulo: str, color_acento: Tuple[int, int, int],
                          alpha: int = 230, con_sombra: bool = True,
                          seleccionada: bool = False):
    """
    Dibuja una ventana completa con efecto glassmorphism
    
    Esta es la funcion principal que combina todos los elementos.
    
    Args:
        surface: Superficie donde dibujar
        rect: Rectangulo de la ventana
        titulo: Texto del titulo
        color_acento: Color de acento RGB (o nombre de tipo)
        alpha: Transparencia del fondo (0-255)
        con_sombra: Si dibujar sombra o no
        seleccionada: Si la ventana esta seleccionada (borde dorado)
    
    Ejemplo:
        rect = pygame.Rect(100, 100, 400, 300)
        dibujar_ventana_glass(
            pantalla, rect, "Magias", 
            COLORES_ACENTO["magia"]
        )
    """
    # Sombra
    if con_sombra:
        dibujar_sombra_glass(surface, rect)
    
    # Fondo transparente
    dibujar_fondo_glass(surface, rect, alpha)
    
    # Borde (dorado si esta seleccionada)
    color_borde = (255, 215, 0) if seleccionada else COLOR_GLASS_BORDER
    dibujar_borde_glass(surface, rect, color_borde)
    
    # Titulo
    dibujar_titulo_glass(surface, rect, titulo, color_acento)


def obtener_color_acento(tipo: str) -> Tuple[int, int, int]:
    """
    Obtiene el color de acento predefinido para un tipo de ventana
    
    Args:
        tipo: Tipo de ventana ("magia", "items", "victoria", etc.)
    
    Returns:
        Tupla RGB del color de acento
    """
    return COLORES_ACENTO.get(tipo.lower(), (100, 150, 255))


def crear_superficie_glass(ancho: int, alto: int, alpha: int = 230) -> pygame.Surface:
    """
    Crea una superficie con transparencia para efectos glass
    
    Args:
        ancho: Ancho de la superficie
        alto: Alto de la superficie
        alpha: Transparencia (0-255)
    
    Returns:
        Superficie de pygame con transparencia
    """
    superficie = pygame.Surface((ancho, alto))
    superficie.set_alpha(alpha)
    superficie.fill(COLOR_GLASS_BG)
    return superficie


# Funcion de conveniencia para ventanas simples
def ventana_glass_simple(surface: pygame.Surface, x: int, y: int,
                         ancho: int, alto: int, titulo: str,
                         tipo: str = "menu", alpha: int = 230):
    """
    Dibuja una ventana glassmorphism simple con parametros minimos
    
    Args:
        surface: Superficie donde dibujar
        x, y: Posicion de la ventana
        ancho, alto: Dimensiones de la ventana
        titulo: Texto del titulo
        tipo: Tipo de ventana (para color de acento)
        alpha: Transparencia
    
    Ejemplo:
        ventana_glass_simple(pantalla, 100, 100, 400, 300, "Inventario", "items")
    """
    rect = pygame.Rect(x, y, ancho, alto)
    color_acento = obtener_color_acento(tipo)
    dibujar_ventana_glass(surface, rect, titulo, color_acento, alpha)


if __name__ == "__main__":
    # Demo del sistema glassmorphism
    pygame.init()
    pantalla = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Demo UI Glassmorphism")
    reloj = pygame.time.Clock()
    
    ejecutando = True
    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
        
        # Fondo degradado
        for y in range(0, 600, 2):
            color = (20 + y // 20, 20 + y // 20, 30 + y // 15)
            pygame.draw.line(pantalla, color, (0, y), (800, y))
        
        # Demostrar diferentes ventanas
        ventana_glass_simple(pantalla, 50, 50, 300, 200, "Magia", "magia")
        ventana_glass_simple(pantalla, 400, 50, 300, 200, "Items", "items")
        ventana_glass_simple(pantalla, 50, 300, 300, 200, "Victoria", "victoria")
        ventana_glass_simple(pantalla, 400, 300, 300, 200, "Habilidades", "habilidades")
        
        pygame.display.flip()
        reloj.tick(60)
    
    pygame.quit()
    print("[OK] Demo cerrado")
