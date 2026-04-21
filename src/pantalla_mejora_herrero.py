import pygame
from typing import Dict, Optional, List, Tuple
from src.npc_comercio_herrero import _get_mejora_equipo_heroe, _costo_mejora_equipo, _stat_principal_equipo

class PantallaMejoraHerrero:
    """UI visual premium para mejorar equipo en el herrero."""

    def __init__(self, ancho: int = 800, alto: int = 600):
        self.ancho = ancho
        self.alto = alto
        
        # Estilo Premium Glassmorphism
        self.COLOR_FONDO_MAIN = (10, 12, 20, 230)
        self.COLOR_PANEL = (20, 25, 45, 200)
        self.COLOR_BORDE = (70, 100, 200, 255)
        self.COLOR_BORDE_SELECT = (150, 200, 255, 255)
        self.COLOR_TITULO = (230, 240, 255)
        self.COLOR_TEXTO = (180, 190, 210)
        self.COLOR_STAT = (120, 255, 120)
        self.COLOR_ORO = (255, 215, 0)
        
        # Estado
        self.cursor_indice = 0
        self.equipo_lista = []  
        self.estado_ui = "lista" # "lista" o "detalle"
        self.lista_scroll = 0
        self.detalle_scroll = 0
        self.items_visibles_lista = 6
        
        # Helper fonts (lazy loading)
        self.font_titulo = None
        self.font_item = None
        self.font_info = None

    def _init_fonts(self):
        if not self.font_titulo:
            # Usamos fuente base de pygame para mantener el estilo visual del juego.
            self.font_titulo = pygame.font.Font(None, 56)
            self.font_item = pygame.font.Font(None, 40)
            self.font_info = pygame.font.Font(None, 32)

    def _recortar_texto(self, fuente, texto: str, max_ancho: int) -> str:
        txt = str(texto or "")
        if fuente.size(txt)[0] <= max_ancho:
            return txt
        sufijo = "..."
        base = txt
        while base and fuente.size(base + sufijo)[0] > max_ancho:
            base = base[:-1]
        return (base + sufijo) if base else sufijo

    def _dibujar_texto_envuelto(self, pantalla, fuente, texto: str, color, area_rect: pygame.Rect, max_lineas: int = 2):
        lineas = self._envolver_texto(fuente, texto, area_rect.w)
        if max_lineas > 0 and len(lineas) > max_lineas:
            visibles = lineas[:max_lineas]
            visibles[-1] = self._recortar_texto(fuente, visibles[-1], area_rect.w)
            lineas = visibles

        line_h = fuente.get_linesize()
        y = area_rect.y
        for linea in lineas:
            if y + line_h > area_rect.y + area_rect.h:
                break
            surf = fuente.render(linea, True, color)
            pantalla.blit(surf, (area_rect.x, y))
            y += line_h

    def _envolver_texto(self, fuente, texto: str, max_ancho: int) -> List[str]:
        palabras = str(texto or "").split()
        if not palabras:
            return [""]
        lineas = []
        actual = palabras[0]
        for palabra in palabras[1:]:
            candidato = f"{actual} {palabra}"
            if fuente.size(candidato)[0] <= max_ancho:
                actual = candidato
            else:
                lineas.append(actual)
                actual = palabra
        lineas.append(actual)
        return lineas

    def _materiales_necesarios(self, nivel: int) -> Dict[str, int]:
        """Calcula dinámicamente los materiales necesarios según el nivel a alcanzar."""
        siguiente_nivel = nivel + 1
        return {
            "MINERAL_HIERRO": siguiente_nivel,
            "POLVO_CRISTAL": max(0, siguiente_nivel - 1)
        }

    def actualizar_equipo(self, heroe, equipo_db: Dict):
        """Carga TODO el equipo del héroe (Equipado + Inventario)."""
        self.equipo_lista = []
        ids_vistos = set()
        
        # 1. Equipo equipado
        for slot_nombre, id_equipo in heroe.equipo.items():
            if id_equipo and id_equipo not in ids_vistos:
                self._agregar_a_lista(heroe, id_equipo, equipo_db, f"Equipado ({slot_nombre})")
                ids_vistos.add(id_equipo)
        
        # 2. Equipo en la mochila (buscar en inventario)
        for id_item, cantidad in heroe.inventario.items():
            # Si es un equipo y no está ya visto
            if id_item in equipo_db and id_item not in ids_vistos and cantidad > 0:
                self._agregar_a_lista(heroe, id_item, equipo_db, "Mochila")
                ids_vistos.add(id_item)
                
        self.cursor_indice = 0
        self.estado_ui = "lista"
        self.lista_scroll = 0
        self.detalle_scroll = 0

    def _agregar_a_lista(self, heroe, id_equipo: str, equipo_db: Dict, ubicacion: str):
        data = equipo_db.get(id_equipo)
        if not data: return
        
        mejora_heroe = _get_mejora_equipo_heroe(heroe, id_equipo)
        nivel = int(mejora_heroe.get("nivel_mejora", 0) or 0)
        costo_oro = _costo_mejora_equipo(nivel)
        materiales = self._materiales_necesarios(nivel)
        nombre = data.get("nombre", id_equipo)
        
        self.equipo_lista.append({
            "id_equipo": id_equipo,
            "nombre": nombre,
            "nivel": nivel,
            "costo": costo_oro,
            "materiales": materiales,
            "stats": data.get("stats", {}),
            "ubicacion": ubicacion
        })

    def procesar_entrada(self, event) -> Optional[Dict]:
        """Procesa entradas para navegación y mejora."""
        if event.type != pygame.KEYDOWN:
            return None
        
        if self.estado_ui == "lista":
            if event.key in (pygame.K_UP, pygame.K_w):
                self.cursor_indice = max(0, self.cursor_indice - 1)
                if self.cursor_indice < self.lista_scroll:
                    self.lista_scroll = self.cursor_indice
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.cursor_indice = min(len(self.equipo_lista) - 1, self.cursor_indice + 1)
                if self.cursor_indice >= self.lista_scroll + self.items_visibles_lista:
                    self.lista_scroll = self.cursor_indice - self.items_visibles_lista + 1
            elif event.key == pygame.K_RETURN:
                if 0 <= self.cursor_indice < len(self.equipo_lista):
                    self.estado_ui = "detalle"
                    self.detalle_scroll = 0
            elif event.key == pygame.K_ESCAPE:
                return {"accion": "cerrar"}
                
        elif self.estado_ui == "detalle":
            if event.key == pygame.K_ESCAPE:
                self.estado_ui = "lista"
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self.estado_ui = "lista"
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.detalle_scroll = max(0, self.detalle_scroll - 1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.detalle_scroll += 1
            elif event.key == pygame.K_PAGEUP:
                self.detalle_scroll = max(0, self.detalle_scroll - 5)
            elif event.key == pygame.K_PAGEDOWN:
                self.detalle_scroll += 5
            elif event.key == pygame.K_RETURN:
                if 0 <= self.cursor_indice < len(self.equipo_lista):
                    item = self.equipo_lista[self.cursor_indice]
                    return {
                        "accion": "intentar_mejora",
                        "id_equipo": item["id_equipo"],
                        "nombre": item["nombre"],
                        "nivel_actual": item["nivel"],
                        "costo_oro": item["costo"],
                        "materiales": item["materiales"]
                    }
        return None

    def dibujar(self, pantalla: pygame.Surface, heroe, items_db: Dict):
        """Dibuja la UI principal del Herrero."""
        self._init_fonts()
        
        # Capa oscura base (modal effect)
        bg = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 150))
        pantalla.blit(bg, (0, 0))
        
        # Panel principal
        panel_w, panel_h = int(self.ancho * 0.8), int(self.alto * 0.8)
        panel_x, panel_y = (self.ancho - panel_w) // 2, (self.alto - panel_h) // 2
        
        panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel_surf.fill(self.COLOR_FONDO_MAIN)
        pygame.draw.rect(panel_surf, self.COLOR_BORDE, panel_surf.get_rect(), 2, border_radius=12)
        pantalla.blit(panel_surf, (panel_x, panel_y))
        
        # Título + Oro en la misma franja, sin solaparse
        oro_text = self.font_item.render(f"Oro: {heroe.oro}G", True, self.COLOR_ORO)
        oro_x = panel_x + panel_w - oro_text.get_width() - 30
        pantalla.blit(oro_text, (oro_x, panel_y + 25))

        titulo_max_w = max(80, oro_x - (panel_x + 30) - 18)
        titulo_txt = self._recortar_texto(self.font_titulo, "Forja y Mejora de Equipo", titulo_max_w)
        titulo = self.font_titulo.render(titulo_txt, True, self.COLOR_TITULO)
        pantalla.blit(titulo, (panel_x + 30, panel_y + 20))
        
        pygame.draw.line(pantalla, self.COLOR_BORDE, (panel_x + 30, panel_y + 65), (panel_x + panel_w - 30, panel_y + 65), 1)

        # Si no hay equipo, seguir mostrando una ventana clara en vez de dejar solo fondo oscuro
        if not self.equipo_lista:
            vacio_rect = pygame.Rect(panel_x + 40, panel_y + 95, panel_w - 80, 120)
            pygame.draw.rect(pantalla, self.COLOR_PANEL, vacio_rect, border_radius=10)
            pygame.draw.rect(pantalla, self.COLOR_BORDE_SELECT, vacio_rect, 1, border_radius=10)

            vacio = self.font_item.render("No tienes equipo para mejorar.", True, self.COLOR_TITULO)
            pantalla.blit(vacio, (vacio_rect.x + 20, vacio_rect.y + 20))

            ayuda = self.font_info.render("Equipa un arma o armadura para ver mejoras aqui.", True, self.COLOR_TEXTO)
            pantalla.blit(ayuda, (vacio_rect.x + 20, vacio_rect.y + 55))

            salir = self.font_info.render("ESC: volver", True, self.COLOR_ORO)
            pantalla.blit(salir, (vacio_rect.x + 20, vacio_rect.y + 85))
            return

        # Vista dividida si es detalle, solo lista si no
        lista_w = (panel_w // 2 - 40) if self.estado_ui == "detalle" else (panel_w - 60)
        
        # Dibujar lista
        y_cursor = panel_y + 80
        alto_item = 58
        paso_item = 62
        fin_lista = min(len(self.equipo_lista), self.lista_scroll + self.items_visibles_lista)
        for i in range(self.lista_scroll, fin_lista):
            item = self.equipo_lista[i]
                
            r = pygame.Rect(panel_x + 30, y_cursor, lista_w, alto_item)
            activo = (i == self.cursor_indice)
            color_bg = self.COLOR_PANEL if activo else (0,0,0,0)
            
            # Fondo del item
            if activo:
                pygame.draw.rect(pantalla, color_bg, r, border_radius=5)
                pygame.draw.rect(pantalla, self.COLOR_BORDE_SELECT, r, 1, border_radius=5)
                
            texto_item = f"{item['nombre']} +{item['nivel']}  [{item['ubicacion']}]"
            color_txt = self.COLOR_TITULO if activo else self.COLOR_TEXTO
            area_item = pygame.Rect(r.x + 10, r.y + 6, r.w - 20, r.h - 10)
            self._dibujar_texto_envuelto(pantalla, self.font_item, texto_item, color_txt, area_item, max_lineas=2)
            
            y_cursor += paso_item

        # Si estamos en detalle, dibujar panel derecho
        if self.estado_ui == "detalle":
            item = self.equipo_lista[self.cursor_indice]
            
            panel_d_x = panel_x + (panel_w // 2) + 10
            panel_d_y = panel_y + 80
            panel_d_w = (panel_w // 2) - 40
            panel_d_h = panel_h - 110
            
            # Fondo detalle
            pd_rect = pygame.Rect(panel_d_x, panel_d_y, panel_d_w, panel_d_h)
            pygame.draw.rect(pantalla, self.COLOR_PANEL, pd_rect, border_radius=8)
            pygame.draw.rect(pantalla, self.COLOR_BORDE, pd_rect, 1, border_radius=8)
            
            # Info del item (flujo vertical tipo chat)
            y_info = panel_d_y + 14

            area_titulo = pygame.Rect(panel_d_x + 20, y_info, panel_d_w - 40, 118)
            self._dibujar_texto_envuelto(pantalla, self.font_titulo, item['nombre'], self.COLOR_TITULO, area_titulo, max_lineas=3)
            y_info += min(3, len(self._envolver_texto(self.font_titulo, item['nombre'], panel_d_w - 40))) * self.font_titulo.get_linesize() + 6

            nv_txt = f"Nivel actual: +{item['nivel']} -> Nivel proyectado: +{item['nivel']+1}"
            area_nv = pygame.Rect(panel_d_x + 20, y_info, panel_d_w - 40, 52)
            self._dibujar_texto_envuelto(pantalla, self.font_item, nv_txt, self.COLOR_TEXTO, area_nv, max_lineas=2)
            y_info += min(2, len(self._envolver_texto(self.font_item, nv_txt, panel_d_w - 40))) * self.font_item.get_linesize() + 8
            
            # Stats (Antes vs Después)
            stat_key = _stat_principal_equipo({"stats": item["stats"]})
            stat_val = int(item["stats"].get(stat_key, 0))
            
            # La fórmula antigua en npc_comercio era +1 a la principal cada mejora
            stat_total_actual = stat_val + item["nivel"]
            stat_total_nueva = stat_total_actual + 1
            
            stat_r = self.font_item.render(f"{stat_key.capitalize()}: {stat_total_actual} -> ", True, self.COLOR_TEXTO)
            pantalla.blit(stat_r, (panel_d_x + 20, y_info))
            stat_r2 = self.font_titulo.render(f"{stat_total_nueva}", True, self.COLOR_STAT)
            stat_r2_x = min(panel_d_x + panel_d_w - stat_r2.get_width() - 20, panel_d_x + 20 + stat_r.get_width())
            pantalla.blit(stat_r2, (stat_r2_x, y_info - 10))
            y_info += max(self.font_item.get_linesize(), self.font_titulo.get_linesize() - 8) + 10

            # Requisitos
            req_tit = self.font_item.render("Materiales requeridos:", True, self.COLOR_TITULO)
            pantalla.blit(req_tit, (panel_d_x + 20, y_info))
            
            base_ry = y_info + self.font_item.get_linesize() + 4

            # Construir lineas de detalle (oro + materiales) para render con scroll
            lineas_detalle = []
            t_oro = "Suficiente" if heroe.oro >= item["costo"] else "(Insuficiente)"
            color_o = self.COLOR_TEXTO if heroe.oro >= item["costo"] else (255, 100, 100)
            oro_txt = f"- Oro: {item['costo']}G {t_oro}"
            for linea in self._envolver_texto(self.font_info, oro_txt, panel_d_w - 40):
                lineas_detalle.append((linea, color_o))
            
            # Mats
            for mat_id, mat_cant in item["materiales"].items():
                if mat_cant > 0:
                    mat_name = items_db.get(mat_id, {}).get("nombre", mat_id)
                    inv_cant = heroe.inventario.get(mat_id, 0)
                    t_m = "" if inv_cant >= mat_cant else f" (Faltan {mat_cant - inv_cant})"
                    c_m = self.COLOR_TEXTO if inv_cant >= mat_cant else (255, 100, 100)
                    
                    linea_mat = f"- {mat_name}: {mat_cant} en mochila: {inv_cant}{t_m}"
                    for linea in self._envolver_texto(self.font_info, linea_mat, panel_d_w - 40):
                        lineas_detalle.append((linea, c_m))

            # Render scrollable de lineas de detalle
            viewport_y = base_ry
            viewport_h = panel_d_h - (base_ry - panel_d_y) - 58
            line_h = self.font_info.get_linesize()
            visibles = max(1, viewport_h // line_h)
            max_scroll = max(0, len(lineas_detalle) - visibles)
            self.detalle_scroll = max(0, min(self.detalle_scroll, max_scroll))

            y_linea = viewport_y
            inicio = self.detalle_scroll
            fin = min(len(lineas_detalle), inicio + visibles)
            for i in range(inicio, fin):
                texto_linea, color_linea = lineas_detalle[i]
                surf = self.font_info.render(texto_linea, True, color_linea)
                pantalla.blit(surf, (panel_d_x + 20, y_linea))
                y_linea += line_h

            # Indicador de scroll en detalle
            if max_scroll > 0:
                ind_txt = self.font_info.render(f"[{self.detalle_scroll + 1}/{max_scroll + 1}]", True, self.COLOR_TEXTO)
                pantalla.blit(ind_txt, (panel_d_x + panel_d_w - ind_txt.get_width() - 16, panel_d_y + panel_d_h - 58))
            
            # Botones
            btn_txt = self.font_item.render("PULSA ENTER PARA MEJORAR", True, self.COLOR_STAT)
            pantalla.blit(btn_txt, (panel_d_x + panel_d_w//2 - btn_txt.get_width()//2, panel_d_y + panel_d_h - 40))
            
        else:
            # Instrucciones lista
            instr = self.font_info.render("ARRIBA/ABAJO: Navegar  |  ENTER: Detalles  |  ESC: Salir", True, self.COLOR_TEXTO)
            pantalla.blit(instr, (panel_x + panel_w//2 - instr.get_width()//2, panel_y + panel_h - 30))

        return True
