"""
Editor de Cofres para CodeVerso RPG
====================================
Editor visual para colocar cofres en mapas con gestión de contenido.

Características:
- Arrastrar cofres desde panel lateral al mapa
- Redimensionar cofres arrastrando bordes
- Asignar 3 sprites (cerrado, abierto con items, abierto vacío)
- Gestionar contenido: items, equipo, especiales, oro
- Sistema de llaves por tipo de cofre
- Generación random de loot
- Zoom y pan
"""

import pygame
import json
import random
from pathlib import Path

# === CONFIGURACIÓN ===
ANCHO, ALTO = 1400, 900
FPS = 60
PANEL_ANCHO = 350
ZOOM_MIN, ZOOM_MAX = 0.25, 2.0

# Colores
COLOR_FONDO = (30, 30, 35)
COLOR_PANEL = (40, 40, 45)
COLOR_TEXTO = (220, 220, 220)
COLOR_HOVER = (70, 70, 80)
COLOR_SELECCION = (100, 150, 255)
COLOR_BORDE = (255, 165, 0)
COLOR_COFRE_MADERA = (139, 69, 19)
COLOR_COFRE_BRONCE = (205, 127, 50)
COLOR_COFRE_PLATA = (192, 192, 192)
COLOR_COFRE_ORO = (255, 215, 0)
COLOR_COFRE_ESPECIAL = (138, 43, 226)

# === CLASES DE DATOS ===
class MapaInfo:
    def __init__(self, nombre, archivo, ruta, categoria, subcarpeta=None):
        self.nombre = nombre
        self.archivo = archivo
        self.ruta = ruta
        self.categoria = categoria
        self.subcarpeta = subcarpeta

class SpriteInfo:
    def __init__(self, nombre, ruta, tipo):
        self.nombre = nombre
        self.ruta = ruta
        self.tipo = tipo  # 'cerrado', 'abierto', 'vacio'

class Cofre:
    def __init__(self, id, x, y, ancho, alto, tipo="madera"):
        self.id = id
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto
        self.tipo = tipo  # madera, bronce, plata, oro, especial
        self.nombre = f"Cofre_{tipo.capitalize()}_{id}"
        
        # Sprites
        self.sprite_cerrado = None
        self.sprite_abierto_items = None
        self.sprite_abierto_vacio = None
        
        # Contenido
        self.oro = 0
        self.items_contenido = {}  # {id_item: cantidad}
        self.equipo_contenido = {}
        self.especiales_contenido = {}
        
        # Configuración
        self.requiere_llave = None
        self.puede_reabrir = True
        self.tiempo_reapertura = 60  # minutos

class SeccionDesplegable:
    def __init__(self, titulo, x, y, ancho, altura_minima=30):
        self.titulo = titulo
        self.x = x
        self.y = y
        self.ancho = ancho
        self.altura_minima = altura_minima
        self.expandida = False
        self.items = []
        self.scroll_offset = 0
        self.hover_index = -1
    
    def draw(self, screen, font_small):
        # Cabecera
        simbolo = "▼" if self.expandida else "▶"
        texto = font_small.render(f"{simbolo} {self.titulo} ({len(self.items)})", True, COLOR_TEXTO)
        rect_header = pygame.Rect(self.x, self.y, self.ancho, self.altura_minima)
        
        pygame.draw.rect(screen, COLOR_PANEL, rect_header)
        pygame.draw.rect(screen, COLOR_BORDE, rect_header, 1)
        screen.blit(texto, (self.x + 10, self.y + 8))
        
        # Contenido expandido
        if self.expandida and self.items:
            y_actual = self.y + self.altura_minima
            items_visibles = 6
            for i, item in enumerate(self.items[self.scroll_offset:self.scroll_offset + items_visibles]):
                idx = i + self.scroll_offset
                rect_item = pygame.Rect(self.x + 5, y_actual, self.ancho - 10, 25)
                
                if idx == self.hover_index:
                    pygame.draw.rect(screen, COLOR_HOVER, rect_item)
                
                texto_item = font_small.render(item, True, COLOR_TEXTO)
                screen.blit(texto_item, (self.x + 15, y_actual + 5))
                y_actual += 27
        
        return rect_header
    
    def toggle(self):
        self.expandida = not self.expandida
    
    def get_altura_total(self):
        if not self.expandida:
            return self.altura_minima
        items_visibles = min(6, len(self.items))
        return self.altura_minima + (items_visibles * 27)

# === EDITOR PRINCIPAL ===
class EditorCofres:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("Editor de Cofres - CodeVerso RPG")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Fuentes
        self.font = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 22)
        self.font_tiny = pygame.font.Font(None, 18)
        
        # Bases de datos
        self.items_db = self._cargar_json("src/database/items_db.json")
        self.equipo_db = self._cargar_json("src/database/equipo_db.json")
        self.especiales_db = self._cargar_json("src/database/items_especiales_db.json")
        self.cofres_db = self._cargar_json("src/database/cofres_db.json")
        
        # Mapa actual
        self.mapa_actual = None
        self.mapa_img = None
        self.mapa_zoom = 1.0
        self.mapa_offset_x = 0
        self.mapa_offset_y = 0
        
        # Cofres
        self.cofres = []
        self.contador_cofres = 0
        self.cofre_seleccionado = None
        self.cofre_copiado = None  # Cofre en portapapeles
        self.arrastrando_cofre = False
        self.redimensionando = False
        self.borde_seleccionado = None  # 'n', 's', 'e', 'w', 'ne', 'nw', 'se', 'sw'
        self.offset_arrastre = (0, 0)
        
        # UI
        self.modo_actual = "colocar"  # colocar, editar
        self.modal_abierto = False
        self.modal_cofre = None
        
        # Selección de items en modal
        self.items_seleccionados = set()  # IDs de items seleccionados para agregar
        self.equipo_seleccionado = set()
        self.especiales_seleccionados = set()
        
        # Edición de cantidad
        self.editando_cantidad = None  # (tipo, item_id)
        self.input_cantidad = ""
        
        # Secciones desplegables del modal
        self.modal_seccion_consumibles_expandida = True
        self.modal_seccion_equipo_expandida = False
        self.modal_seccion_especiales_expandida = False
        
        # Secciones
        self.seccion_mapas = []
        self.seccion_sprites = SeccionDesplegable("Sprites de Cofres", 10, 60, PANEL_ANCHO - 20)
        self.seccion_items = SeccionDesplegable("Items", 10, 300, PANEL_ANCHO - 20)
        self.seccion_equipo = SeccionDesplegable("Equipo", 10, 400, PANEL_ANCHO - 20)
        self.seccion_especiales = SeccionDesplegable("Especiales", 10, 500, PANEL_ANCHO - 20)
        
        # Cargar recursos
        self._cargar_mapas()
        self._cargar_sprites_cofres()
        self._actualizar_listas_items()
        
        # Panning
        self.panning = False
        self.ultimo_mouse_pos = (0, 0)
        
        # Drag & Drop
        self.arrastrando_mapa = False
        self.mapa_arrastrado = None
        
        # Ayuda
        self.mostrar_ayuda = False
        
        # Autosave
        self.tiempo_autosave = 0

    def _buscar_imagen_mapa(self, categoria, nombre_stem, subcarpeta_hint=None):
        """Busca la imagen del mapa probando extensiones y subcarpetas.
        Devuelve (ruta_imagen: Path | None, subcarpeta_real: str | None).
        """
        base_cat = Path("assets/maps") / categoria
        exts = ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']

        # 1) Intento directo según hint de subcarpeta (si viene del JSON)
        if subcarpeta_hint:
            for ext in exts:
                p = base_cat / subcarpeta_hint / f"{nombre_stem}{ext}"
                if p.exists():
                    return p, subcarpeta_hint.replace('\\', '/').strip('/') or None

        # 2) Intento directo en la raíz de la categoría
        for ext in exts:
            p = base_cat / f"{nombre_stem}{ext}"
            if p.exists():
                return p, None

        # 3) Búsqueda recursiva en toda la categoría (cualquier subcarpeta)
        try:
            for ext in exts:
                for p in base_cat.rglob(f"{nombre_stem}{ext}"):
                    if p.is_file():
                        # Subcarpeta real relativa a la categoría
                        rel_parent = p.parent.relative_to(base_cat)
                        sub_real = str(rel_parent).replace('\\', '/') if str(rel_parent) != '.' else None
                        return p, sub_real
        except Exception:
            pass

        return None, None
    
    def _cargar_json(self, ruta):
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def _cargar_mapas(self):
        """Escanea src/database/mapas/ y organiza por categorías, mostrando SOLO los que tengan imagen."""
        base = Path("src/database/mapas")
        if not base.exists():
            return

        mapas_por_categoria = {}

        # Recorrer todas las categorías
        for cat_dir in base.iterdir():
            if not cat_dir.is_dir():
                continue

            categoria = cat_dir.name
            mapas_por_categoria[categoria] = []

            # Buscar todos los JSON recursivamente
            for json_file in cat_dir.rglob("*.json"):
                nombre = json_file.stem

                # Calcular subcarpeta relativa a la categoría (hint)
                ruta_relativa = json_file.relative_to(cat_dir)
                if len(ruta_relativa.parts) > 1:
                    subcarpeta_hint = str(ruta_relativa.parent).replace('\\', '/')
                else:
                    subcarpeta_hint = None

                # Buscar imagen asociada (usa hint y, si no, búsqueda recursiva)
                img_path, sub_real = self._buscar_imagen_mapa(categoria, nombre, subcarpeta_hint)
                if not img_path:
                    # No se encontró imagen: ocultar de la lista
                    continue

                mapa_info = MapaInfo(
                    nombre=nombre,
                    archivo=json_file.name,
                    ruta=str(json_file),
                    categoria=categoria,
                    subcarpeta=sub_real
                )
                mapas_por_categoria[categoria].append(mapa_info)

                # Debug
                # print(f"  ✓ Mapa: {nombre} | Categoría: {categoria} | Subcarpeta real: {sub_real} | Img: {img_path.name}")

        # Crear secciones desplegables SOLO con mapas válidos
        y_offset = 60
        for cat, mapas in sorted(mapas_por_categoria.items()):
            if not mapas:
                continue
            seccion = SeccionDesplegable(cat.replace('_', ' ').title(), 10, y_offset, PANEL_ANCHO - 20)
            seccion.items = [m.nombre for m in mapas]
            seccion.datos = mapas
            self.seccion_mapas.append(seccion)
            y_offset += 35
    
    def _cargar_sprites_cofres(self):
        """Escanea assets/sprites/cofres y demas/cofres/"""
        base = Path("assets/sprites/cofres y demas/cofres")
        if not base.exists():
            return
        
        sprites = []
        for tipo_dir in base.iterdir():
            if not tipo_dir.is_dir():
                continue
            
            for archivo in tipo_dir.glob("*.png"):
                nombre = f"{tipo_dir.name}/{archivo.stem}"
                tipo = "cerrado" if "cerrado" in archivo.stem.lower() else \
                       "vacio" if "vacio" in archivo.stem.lower() or "sin" in archivo.stem.lower() else \
                       "abierto"
                sprites.append(SpriteInfo(nombre, str(archivo), tipo))
        
        self.seccion_sprites.items = [s.nombre for s in sprites]
        self.seccion_sprites.datos = sprites
    
    def _actualizar_listas_items(self):
        """Actualiza las listas de items, equipo y especiales"""
        # Items consumibles
        items_lista = [f"{v['nombre']} ({k})" for k, v in self.items_db.items() if v.get('tipo') == 'Consumible']
        self.seccion_items.items = items_lista
        self.seccion_items.datos = list(self.items_db.keys())
        
        # Equipo
        equipo_lista = [f"{v['nombre']} ({k})" for k, v in self.equipo_db.items()]
        self.seccion_equipo.items = equipo_lista
        self.seccion_equipo.datos = list(self.equipo_db.keys())
        
        # Especiales
        especiales_lista = [f"{v['nombre']} ({k})" for k, v in self.especiales_db.items()]
        self.seccion_especiales.items = especiales_lista
        self.seccion_especiales.datos = list(self.especiales_db.keys())
    
    def cargar_mapa(self, mapa_info):
        """Carga un mapa y sus cofres"""
        # Construir ruta base considerando subcarpetas
        if mapa_info.subcarpeta:
            base_path = Path(f"assets/maps/{mapa_info.categoria}/{mapa_info.subcarpeta}/{mapa_info.archivo.replace('.json', '')}")
        else:
            base_path = Path(f"assets/maps/{mapa_info.categoria}/{mapa_info.archivo.replace('.json', '')}")
        
        img_path = None
        
        # Probar diferentes extensiones
        for ext in ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']:
            test_path = Path(str(base_path) + ext)
            if test_path.exists():
                img_path = test_path
                break
        
        if not img_path:
            print(f"⚠ Imagen no encontrada para: {mapa_info.archivo}")
            if mapa_info.subcarpeta:
                print(f"   Buscado en: assets/maps/{mapa_info.categoria}/{mapa_info.subcarpeta}/")
            else:
                print(f"   Buscado en: assets/maps/{mapa_info.categoria}/")
            print(f"   Extensiones probadas: .png, .jpg, .jpeg")
            return
        
        try:
            self.mapa_img = pygame.image.load(str(img_path)).convert()
            self.mapa_actual = mapa_info
            print(f"✓ Imagen cargada: {img_path.name}")
        except Exception as e:
            print(f"⚠ Error al cargar imagen {img_path}: {e}")
            return
        
        # Auto-fit zoom
        viewport_ancho = ANCHO - PANEL_ANCHO
        viewport_alto = ALTO
        zoom_x = viewport_ancho / self.mapa_img.get_width()
        zoom_y = viewport_alto / self.mapa_img.get_height()
        self.mapa_zoom = min(zoom_x, zoom_y, 1.0)
        self.mapa_offset_x = (viewport_ancho - self.mapa_img.get_width() * self.mapa_zoom) // 2
        self.mapa_offset_y = (viewport_alto - self.mapa_img.get_height() * self.mapa_zoom) // 2
        
        # Cargar cofres del JSON
        self.cofres = []
        try:
            with open(mapa_info.ruta, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for cofre_data in data.get("cofres", []):
                cofre = Cofre(
                    id=cofre_data.get("id", f"C{self.contador_cofres}"),
                    x=cofre_data["x"],
                    y=cofre_data["y"],
                    ancho=cofre_data["ancho"],
                    alto=cofre_data["alto"],
                    tipo=cofre_data.get("tipo", "madera")
                )
                cofre.nombre = cofre_data.get("nombre", cofre.nombre)
                cofre.sprite_cerrado = cofre_data.get("sprite_cerrado")
                cofre.sprite_abierto_items = cofre_data.get("sprite_abierto_items")
                cofre.sprite_abierto_vacio = cofre_data.get("sprite_abierto_vacio")
                cofre.oro = cofre_data.get("oro", 0)
                cofre.items_contenido = cofre_data.get("items_contenido", {})
                cofre.equipo_contenido = cofre_data.get("equipo_contenido", {})
                cofre.especiales_contenido = cofre_data.get("especiales_contenido", {})
                cofre.requiere_llave = cofre_data.get("requiere_llave")
                cofre.puede_reabrir = cofre_data.get("puede_reabrir", True)
                cofre.tiempo_reapertura = cofre_data.get("tiempo_reapertura", 60)
                
                self.cofres.append(cofre)
                self.contador_cofres = max(self.contador_cofres, int(cofre.id[1:]) + 1 if cofre.id.startswith('C') else 0)
        except:
            pass
        
        print(f"✓ Mapa cargado: {mapa_info.nombre} ({len(self.cofres)} cofres)")
    
    def guardar_mapa(self):
        """Guarda el mapa actual con sus cofres"""
        if not self.mapa_actual:
            return
        
        # Cargar JSON existente
        try:
            with open(self.mapa_actual.ruta, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            data = {}
        
        # Actualizar cofres
        data["cofres"] = []
        for cofre in self.cofres:
            data["cofres"].append({
                "id": cofre.id,
                "nombre": cofre.nombre,
                "tipo": cofre.tipo,
                "x": cofre.x,
                "y": cofre.y,
                "ancho": cofre.ancho,
                "alto": cofre.alto,
                "sprite_cerrado": cofre.sprite_cerrado,
                "sprite_abierto_items": cofre.sprite_abierto_items,
                "sprite_abierto_vacio": cofre.sprite_abierto_vacio,
                "oro": cofre.oro,
                "items_contenido": cofre.items_contenido,
                "equipo_contenido": cofre.equipo_contenido,
                "especiales_contenido": cofre.especiales_contenido,
                "requiere_llave": cofre.requiere_llave,
                "puede_reabrir": cofre.puede_reabrir,
                "tiempo_reapertura": cofre.tiempo_reapertura
            })
        
        # Guardar
        with open(self.mapa_actual.ruta, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Guardado: {self.mapa_actual.nombre}")
    
    def _map_to_screen(self, x, y):
        """Convierte coordenadas del mapa a pantalla"""
        return (int(x * self.mapa_zoom + self.mapa_offset_x + PANEL_ANCHO),
                int(y * self.mapa_zoom + self.mapa_offset_y))
    
    def _screen_to_map(self, sx, sy):
        """Convierte coordenadas de pantalla a mapa"""
        return (int((sx - PANEL_ANCHO - self.mapa_offset_x) / self.mapa_zoom),
                int((sy - self.mapa_offset_y) / self.mapa_zoom))
    
    def _detectar_borde_cofre(self, cofre, mx_map, my_map):
        """Detecta si el mouse está sobre un borde del cofre para redimensionar"""
        margen = 10 / self.mapa_zoom
        
        en_izq = abs(mx_map - cofre.x) < margen
        en_der = abs(mx_map - (cofre.x + cofre.ancho)) < margen
        en_arr = abs(my_map - cofre.y) < margen
        en_aba = abs(my_map - (cofre.y + cofre.alto)) < margen
        
        if en_izq and en_arr: return 'nw'
        if en_der and en_arr: return 'ne'
        if en_izq and en_aba: return 'sw'
        if en_der and en_aba: return 'se'
        if en_izq: return 'w'
        if en_der: return 'e'
        if en_arr: return 'n'
        if en_aba: return 's'
        return None
    
    def _generar_loot_random(self, cofre):
        """Genera loot aleatorio según el tipo de cofre"""
        if cofre.tipo not in self.cofres_db.get("tipos_cofre", {}):
            return
        
        config = self.cofres_db["tipos_cofre"][cofre.tipo]
        
        # IMPORTANTE: Limpiar contenido previo antes de generar nuevo loot
        cofre.items_contenido = {}
        cofre.equipo_contenido = {}
        cofre.especiales_contenido = {}
        cofre.oro = 0
        
        # Oro
        if cofre.tipo != "especial":
            cofre.oro = random.randint(config["oro_min"], config["oro_max"])
        
        # Items
        if "items_random" in config:
            ir = config["items_random"]
            cant_items = random.randint(ir["min"], ir["max"])
            
            if cofre.tipo == "especial":
                # Solo items especiales
                if "pool_especiales" in ir:
                    seleccionados = random.sample(ir["pool_especiales"], min(cant_items, len(ir["pool_especiales"])))
                    for item_id in seleccionados:
                        cofre.especiales_contenido[item_id] = random.randint(1, 2)
            else:
                # Consumibles
                if "pool_consumibles" in ir:
                    for _ in range(cant_items):
                        item_id = random.choice(ir["pool_consumibles"])
                        cofre.items_contenido[item_id] = cofre.items_contenido.get(item_id, 0) + random.randint(1, 3)
                
                # Equipo
                if "pool_equipo" in ir and cofre.tipo == "madera":
                    if random.random() < 0.5:  # 50% chance
                        equipo_id = random.choice(ir["pool_equipo"])
                        cofre.equipo_contenido[equipo_id] = 1
        
        print(f"✓ Loot generado para {cofre.nombre}: {cofre.oro} oro, {len(cofre.items_contenido)} items")
    
    def run(self):
        """Loop principal"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.tiempo_autosave += dt
            
            # Autosave cada 5 segundos
            if self.tiempo_autosave >= 5.0:
                if self.mapa_actual:
                    self.guardar_mapa()
                self.tiempo_autosave = 0
            
            self._handle_events()
            self._draw()
        
        pygame.quit()
    
    def _handle_events(self):
        mx, my = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.mapa_actual:
                    self.guardar_mapa()
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.modal_abierto:
                        self.modal_abierto = False
                        self.modal_cofre = None
                    else:
                        if self.mapa_actual:
                            self.guardar_mapa()
                        self.running = False
                
                elif event.key == pygame.K_g:
                    if self.mapa_actual:
                        self.guardar_mapa()
                
                elif event.key == pygame.K_h:
                    self.mostrar_ayuda = not self.mostrar_ayuda
                
                # Edición de cantidad en modal
                elif self.modal_abierto and self.editando_cantidad:
                    if event.key == pygame.K_RETURN:
                        # Confirmar edición
                        tipo, item_id = self.editando_cantidad
                        try:
                            nueva_cant = int(self.input_cantidad)
                            if tipo == "oro":
                                if nueva_cant >= 0:
                                    self.modal_cofre.oro = nueva_cant
                            elif nueva_cant > 0:
                                if tipo == "items":
                                    self.modal_cofre.items_contenido[item_id] = nueva_cant
                                elif tipo == "equipo":
                                    self.modal_cofre.equipo_contenido[item_id] = nueva_cant
                                elif tipo == "especiales":
                                    self.modal_cofre.especiales_contenido[item_id] = nueva_cant
                        except ValueError:
                            pass
                        self.editando_cantidad = None
                        self.input_cantidad = ""
                    
                    elif event.key == pygame.K_ESCAPE:
                        # Cancelar edición
                        self.editando_cantidad = None
                        self.input_cantidad = ""
                    
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_cantidad = self.input_cantidad[:-1]
                    
                    elif event.unicode.isdigit():
                        self.input_cantidad += event.unicode
                
                elif event.key == pygame.K_DELETE:
                    if self.cofre_seleccionado:
                        self.cofres.remove(self.cofre_seleccionado)
                        self.cofre_seleccionado = None
                
                # Ctrl+C: Copiar cofre seleccionado
                elif event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    if self.cofre_seleccionado and not self.modal_abierto:
                        self.cofre_copiado = self.cofre_seleccionado
                        print(f"✓ Cofre copiado: {self.cofre_copiado.nombre}")
                
                # Ctrl+V: Pegar cofre en posición del mouse
                elif event.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    if self.cofre_copiado and self.mapa_actual and not self.modal_abierto:
                        # Verificar que el mouse esté en el viewport
                        if mx >= PANEL_ANCHO:
                            mx_map, my_map = self._screen_to_map(mx, my)
                            
                            # Crear nuevo cofre con datos copiados
                            self.contador_cofres += 1
                            nuevo_id = f"C{self.contador_cofres}"
                            
                            nuevo_cofre = Cofre(
                                id=nuevo_id,
                                x=mx_map,
                                y=my_map,
                                ancho=self.cofre_copiado.ancho,
                                alto=self.cofre_copiado.alto,
                                tipo=self.cofre_copiado.tipo
                            )
                            
                            # Copiar contenido
                            nuevo_cofre.oro = self.cofre_copiado.oro
                            nuevo_cofre.items_contenido = self.cofre_copiado.items_contenido.copy()
                            nuevo_cofre.equipo_contenido = self.cofre_copiado.equipo_contenido.copy()
                            nuevo_cofre.especiales_contenido = self.cofre_copiado.especiales_contenido.copy()
                            nuevo_cofre.requiere_llave = self.cofre_copiado.requiere_llave
                            nuevo_cofre.puede_reabrir = self.cofre_copiado.puede_reabrir
                            nuevo_cofre.tiempo_reapertura = self.cofre_copiado.tiempo_reapertura
                            
                            # Copiar sprites si existen
                            nuevo_cofre.sprite_cerrado = self.cofre_copiado.sprite_cerrado
                            nuevo_cofre.sprite_abierto_items = self.cofre_copiado.sprite_abierto_items
                            nuevo_cofre.sprite_abierto_vacio = self.cofre_copiado.sprite_abierto_vacio
                            
                            self.cofres.append(nuevo_cofre)
                            self.cofre_seleccionado = nuevo_cofre
                            print(f"✓ Cofre pegado: {nuevo_cofre.nombre} en ({mx_map}, {my_map})")
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Click izquierdo
                    # Verificar si está arrastrando desde panel
                    if mx < PANEL_ANCHO:
                        for seccion in self.seccion_mapas:
                            if seccion.expandida:
                                rect_header = pygame.Rect(seccion.x, seccion.y, seccion.ancho, seccion.altura_minima)
                                y_items = rect_header.bottom
                                for i, mapa in enumerate(seccion.datos[seccion.scroll_offset:]):
                                    rect_item = pygame.Rect(seccion.x + 5, y_items + i * 27, seccion.ancho - 10, 25)
                                    if rect_item.collidepoint(mx, my):
                                        self.arrastrando_mapa = True
                                        self.mapa_arrastrado = mapa
                                        return
                    
                    self._handle_click_izquierdo(mx, my)
                
                elif event.button == 3:  # Click derecho
                    self._handle_click_derecho(mx, my)
                
                elif event.button == 4:  # Scroll arriba (zoom in)
                    if mx > PANEL_ANCHO and not self.modal_abierto:
                        self.mapa_zoom = min(self.mapa_zoom * 1.1, ZOOM_MAX)
                
                elif event.button == 5:  # Scroll abajo (zoom out)
                    if mx > PANEL_ANCHO and not self.modal_abierto:
                        self.mapa_zoom = max(self.mapa_zoom / 1.1, ZOOM_MIN)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    # Finalizar drag & drop de mapa o click en item
                    if self.arrastrando_mapa and self.mapa_arrastrado:
                        # Si se soltó en el viewport, cargar
                        if mx > PANEL_ANCHO:
                            self.cargar_mapa(self.mapa_arrastrado)
                        else:
                            # Tratar como click simple en el item: cargar igual
                            self.cargar_mapa(self.mapa_arrastrado)
                        self.arrastrando_mapa = False
                        self.mapa_arrastrado = None
                    
                    self.arrastrando_cofre = False
                    self.redimensionando = False
                    self.borde_seleccionado = None
                
                elif event.button == 3:
                    self.panning = False
            
            elif event.type == pygame.MOUSEMOTION:
                if self.panning:
                    dx = mx - self.ultimo_mouse_pos[0]
                    dy = my - self.ultimo_mouse_pos[1]
                    self.mapa_offset_x += dx
                    self.mapa_offset_y += dy
                
                if self.arrastrando_cofre and self.cofre_seleccionado:
                    mx_map, my_map = self._screen_to_map(mx, my)
                    self.cofre_seleccionado.x = mx_map - self.offset_arrastre[0]
                    self.cofre_seleccionado.y = my_map - self.offset_arrastre[1]
                
                if self.redimensionando and self.cofre_seleccionado:
                    mx_map, my_map = self._screen_to_map(mx, my)
                    c = self.cofre_seleccionado
                    
                    if 'w' in self.borde_seleccionado:
                        nuevo_x = mx_map
                        c.ancho += c.x - nuevo_x
                        c.x = nuevo_x
                    if 'e' in self.borde_seleccionado:
                        c.ancho = mx_map - c.x
                    if 'n' in self.borde_seleccionado:
                        nuevo_y = my_map
                        c.alto += c.y - nuevo_y
                        c.y = nuevo_y
                    if 's' in self.borde_seleccionado:
                        c.alto = my_map - c.y
                    
                    # Límites mínimos
                    c.ancho = max(c.ancho, 20)
                    c.alto = max(c.alto, 20)
                
                self.ultimo_mouse_pos = (mx, my)
    
    def _handle_click_izquierdo(self, mx, my):
        """Maneja click izquierdo"""
        # En panel lateral
        if mx < PANEL_ANCHO:
            # Check secciones de mapas
            for seccion in self.seccion_mapas:
                rect = seccion.draw(self.screen, self.font_small)
                if rect.collidepoint(mx, my):
                    seccion.toggle()
                    return
                
                if seccion.expandida:
                    y_items = rect.bottom
                    for i, mapa in enumerate(seccion.datos[seccion.scroll_offset:]):
                        rect_item = pygame.Rect(seccion.x + 5, y_items + i * 27, seccion.ancho - 10, 25)
                        if rect_item.collidepoint(mx, my):
                            self.cargar_mapa(mapa)
                            return
            return
        
        # En viewport
        if not self.mapa_actual:
            return
        
        # Bloquear si el modal está abierto
        if self.modal_abierto:
            return
        
        mx_map, my_map = self._screen_to_map(mx, my)
        
        # Check si click en cofre existente
        for cofre in reversed(self.cofres):
            if (cofre.x <= mx_map <= cofre.x + cofre.ancho and
                cofre.y <= my_map <= cofre.y + cofre.alto):
                
                # Check si es para redimensionar
                borde = self._detectar_borde_cofre(cofre, mx_map, my_map)
                if borde:
                    self.cofre_seleccionado = cofre
                    self.redimensionando = True
                    self.borde_seleccionado = borde
                else:
                    self.cofre_seleccionado = cofre
                    self.arrastrando_cofre = True
                    self.offset_arrastre = (mx_map - cofre.x, my_map - cofre.y)
                return
        
        # Crear nuevo cofre
        self.contador_cofres += 1
        nuevo_cofre = Cofre(f"C{self.contador_cofres}", mx_map, my_map, 64, 64)
        self.cofres.append(nuevo_cofre)
        self.cofre_seleccionado = nuevo_cofre
        print(f"✓ Cofre creado: {nuevo_cofre.nombre}")
    
    def _handle_click_derecho(self, mx, my):
        """Maneja click derecho"""
        # Panning en viewport
        if mx > PANEL_ANCHO and self.mapa_actual:
            mx_map, my_map = self._screen_to_map(mx, my)
            
            # Check si click en cofre para abrir modal
            for cofre in reversed(self.cofres):
                if (cofre.x <= mx_map <= cofre.x + cofre.ancho and
                    cofre.y <= my_map <= cofre.y + cofre.alto):
                    self.modal_abierto = True
                    self.modal_cofre = cofre
                    return
            
            # Si no, iniciar panning
            self.panning = True
    
    def _draw(self):
        """Dibuja todo"""
        self.screen.fill(COLOR_FONDO)
        
        # Panel lateral
        self._draw_panel()
        
        # Viewport
        if self.mapa_actual and self.mapa_img:
            self._draw_viewport()
        
        # Modal
        if self.modal_abierto and self.modal_cofre:
            self._draw_modal()
        
        # Ayuda
        if self.mostrar_ayuda:
            self._draw_ayuda()
        
        # Overlay
        self._draw_overlay()
        
        pygame.display.flip()
    
    def _draw_panel(self):
        """Dibuja panel lateral"""
        pygame.draw.rect(self.screen, COLOR_PANEL, (0, 0, PANEL_ANCHO, ALTO))
        
        # Título
        titulo = self.font.render("Editor de Cofres", True, COLOR_TEXTO)
        self.screen.blit(titulo, (10, 10))
        
        # Instrucción drag & drop
        if not self.mapa_actual:
            instruccion = self.font_tiny.render("Arrastra un mapa aquí →", True, (150, 150, 150))
            self.screen.blit(instruccion, (10, 35))
        
        # Secciones de mapas
        y_offset = 60
        for seccion in self.seccion_mapas:
            seccion.y = y_offset
            rect = seccion.draw(self.screen, self.font_small)
            y_offset += seccion.get_altura_total() + 5
        
        # Botón ayuda
        btn_ayuda = self.font_small.render("[H] Ayuda", True, COLOR_TEXTO)
        self.screen.blit(btn_ayuda, (10, ALTO - 30))
    
    def _draw_viewport(self):
        """Dibuja viewport del mapa"""
        # Mapa escalado
        img_escalada = pygame.transform.scale(self.mapa_img, 
            (int(self.mapa_img.get_width() * self.mapa_zoom),
             int(self.mapa_img.get_height() * self.mapa_zoom)))
        
        self.screen.blit(img_escalada, (PANEL_ANCHO + self.mapa_offset_x, self.mapa_offset_y))
        
        # Cofres
        for cofre in self.cofres:
            self._draw_cofre(cofre)
    
    def _draw_cofre(self, cofre):
        """Dibuja un cofre en el mapa"""
        sx, sy = self._map_to_screen(cofre.x, cofre.y)
        ancho_screen = int(cofre.ancho * self.mapa_zoom)
        alto_screen = int(cofre.alto * self.mapa_zoom)
        
        # Color según tipo
        colores = {
            "madera": COLOR_COFRE_MADERA,
            "bronce": COLOR_COFRE_BRONCE,
            "plata": COLOR_COFRE_PLATA,
            "oro": COLOR_COFRE_ORO,
            "especial": COLOR_COFRE_ESPECIAL
        }
        color = colores.get(cofre.tipo, COLOR_COFRE_MADERA)
        
        # Rectángulo del cofre
        rect = pygame.Rect(sx, sy, ancho_screen, alto_screen)
        pygame.draw.rect(self.screen, color, rect)
        
        # Borde
        borde_color = COLOR_SELECCION if cofre == self.cofre_seleccionado else COLOR_BORDE
        pygame.draw.rect(self.screen, borde_color, rect, 2)
        
        # Label con nombre
        if self.mapa_zoom > 0.5:
            texto = self.font_tiny.render(cofre.id, True, (255, 255, 255))
            rect_texto = texto.get_rect()
            rect_fondo = pygame.Rect(sx, sy - 20, rect_texto.width + 6, rect_texto.height + 4)
            pygame.draw.rect(self.screen, (0, 0, 0), rect_fondo)
            pygame.draw.rect(self.screen, COLOR_BORDE, rect_fondo, 1)
            self.screen.blit(texto, (sx + 3, sy - 18))
    
    def _draw_modal(self):
        """Dibuja modal de edición de cofre con listas de items disponibles"""
        # Fondo oscuro
        overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Ventana modal más grande
        modal_ancho, modal_alto = 1300, 800
        modal_x = (ANCHO - modal_ancho) // 2
        modal_y = (ALTO - modal_alto) // 2
        modal_rect = pygame.Rect(modal_x, modal_y, modal_ancho, modal_alto)
        
        pygame.draw.rect(self.screen, COLOR_PANEL, modal_rect)
        pygame.draw.rect(self.screen, COLOR_BORDE, modal_rect, 3)
        
        cofre = self.modal_cofre
        mx, my = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0]
        y = modal_y + 20
        
        # Título
        titulo = self.font.render(f"Editar: {cofre.nombre}", True, COLOR_TEXTO)
        self.screen.blit(titulo, (modal_x + 20, y))
        y += 50
        
        # Tipo de cofre
        texto_tipo = self.font_small.render(f"Tipo: {cofre.tipo.upper()}", True, COLOR_TEXTO)
        self.screen.blit(texto_tipo, (modal_x + 20, y))
        y += 30
        
        # Botones para cambiar tipo
        tipos = ["madera", "bronce", "plata", "oro", "especial"]
        x_btn = modal_x + 20
        for tipo in tipos:
            btn_rect = pygame.Rect(x_btn, y, 100, 30)
            color = COLOR_SELECCION if tipo == cofre.tipo else COLOR_HOVER
            pygame.draw.rect(self.screen, color, btn_rect)
            pygame.draw.rect(self.screen, COLOR_BORDE, btn_rect, 1)
            
            texto = self.font_tiny.render(tipo.capitalize(), True, COLOR_TEXTO)
            texto_rect = texto.get_rect(center=btn_rect.center)
            self.screen.blit(texto, texto_rect)
            
            # Click
            mx, my = pygame.mouse.get_pos()
            if btn_rect.collidepoint(mx, my) and pygame.mouse.get_pressed()[0]:
                cofre.tipo = tipo
                cofre.nombre = f"Cofre_{tipo.capitalize()}_{cofre.id[1:]}"
                # Aplicar configuración automática
                if tipo in self.cofres_db.get("tipos_cofre", {}):
                    config = self.cofres_db["tipos_cofre"][tipo]
                    cofre.requiere_llave = config.get("requiere_llave")
                    cofre.puede_reabrir = config.get("puede_reabrir", True)
                    cofre.tiempo_reapertura = config.get("tiempo_reapertura_minutos", 60)
            
            x_btn += 110
        y += 50
        
        # === ORO EDITABLE ===
        texto_oro_label = self.font_small.render("Oro:", True, (255, 215, 0))
        self.screen.blit(texto_oro_label, (modal_x + 20, y + 5))
        
        # Input de oro
        input_oro_x = modal_x + 80
        input_oro_rect = pygame.Rect(input_oro_x, y, 100, 30)
        pygame.draw.rect(self.screen, (60, 60, 60), input_oro_rect)
        pygame.draw.rect(self.screen, (200, 180, 0), input_oro_rect, 2)
        
        # Mostrar cantidad o input
        if self.editando_cantidad == ("oro", None):
            texto_oro = self.font_small.render(self.input_cantidad + "_", True, (255, 255, 100))
        else:
            texto_oro = self.font_small.render(str(cofre.oro), True, (255, 215, 0))
        
        self.screen.blit(texto_oro, (input_oro_x + 8, y + 5))
        
        # Click para editar oro
        mx, my = pygame.mouse.get_pos()
        if input_oro_rect.collidepoint(mx, my) and click:
            # Guardar cantidad anterior si existía
            if self.editando_cantidad and self.input_cantidad:
                tipo_anterior, item_anterior = self.editando_cantidad
                try:
                    if tipo_anterior == "oro":
                        nueva_cant = int(self.input_cantidad)
                        if nueva_cant >= 0:
                            cofre.oro = nueva_cant
                    else:
                        nueva_cant = int(self.input_cantidad)
                        if nueva_cant > 0:
                            if tipo_anterior == "items":
                                cofre.items_contenido[item_anterior] = nueva_cant
                            elif tipo_anterior == "equipo":
                                cofre.equipo_contenido[item_anterior] = nueva_cant
                            elif tipo_anterior == "especiales":
                                cofre.especiales_contenido[item_anterior] = nueva_cant
                except ValueError:
                    pass
            
            # Iniciar edición del oro
            self.editando_cantidad = ("oro", None)
            self.input_cantidad = str(cofre.oro)
            pygame.time.wait(150)
        
        # Botón random oro
        btn_random_oro = pygame.Rect(modal_x + 200, y, 120, 30)
        pygame.draw.rect(self.screen, COLOR_HOVER, btn_random_oro)
        pygame.draw.rect(self.screen, COLOR_BORDE, btn_random_oro, 1)
        texto_btn = self.font_tiny.render("Random Oro", True, COLOR_TEXTO)
        self.screen.blit(texto_btn, (btn_random_oro.x + 10, btn_random_oro.y + 7))
        
        if btn_random_oro.collidepoint(mx, my) and pygame.mouse.get_pressed()[0]:
            if cofre.tipo in self.cofres_db.get("tipos_cofre", {}):
                config = self.cofres_db["tipos_cofre"][cofre.tipo]
                cofre.oro = random.randint(config["oro_min"], config["oro_max"])
                pygame.time.wait(150)
        
        y += 50
        
        # === COLUMNA IZQUIERDA: Items Disponibles con Checkboxes ===
        col_izq_x = modal_x + 20
        col_izq_ancho = 400
        y_izq = y
        
        texto_disponibles = self.font_small.render("Items Disponibles (selecciona para agregar):", True, (150, 255, 150))
        self.screen.blit(texto_disponibles, (col_izq_x, y_izq))
        y_izq += 30
        
        # === CONSUMIBLES DESPLEGABLE ===
        simbolo_cons = "▼" if self.modal_seccion_consumibles_expandida else "▶"
        consumibles_list = [(item_id, item_data) for item_id, item_data in self.items_db.items() if item_data.get('tipo') == 'Consumible']
        texto_cons = self.font_tiny.render(f"{simbolo_cons} Consumibles ({len(consumibles_list)}):", True, (200, 220, 255))
        header_cons_rect = pygame.Rect(col_izq_x, y_izq, col_izq_ancho - 20, 22)
        pygame.draw.rect(self.screen, (50, 50, 55), header_cons_rect)
        pygame.draw.rect(self.screen, (80, 80, 90), header_cons_rect, 1)
        self.screen.blit(texto_cons, (col_izq_x + 5, y_izq + 3))
        
        # Click en header para expandir/colapsar
        if header_cons_rect.collidepoint(mx, my) and click:
            self.modal_seccion_consumibles_expandida = not self.modal_seccion_consumibles_expandida
            pygame.time.wait(150)
        
        y_izq += 24
        
        # Contenido si está expandido
        if self.modal_seccion_consumibles_expandida:
            for item_id, item_data in consumibles_list[:8]:  # Máximo 8 items
                nombre = item_data.get('nombre', item_id)[:28]
                
                # Checkbox
                checkbox_rect = pygame.Rect(col_izq_x + 10, y_izq, 16, 16)
                pygame.draw.rect(self.screen, (100, 100, 100), checkbox_rect, 1)
                
                if item_id in self.items_seleccionados:
                    pygame.draw.rect(self.screen, (100, 255, 100), checkbox_rect.inflate(-4, -4))
                
                # Detectar click en checkbox
                if checkbox_rect.collidepoint(mx, my) and click:
                    if item_id in self.items_seleccionados:
                        self.items_seleccionados.remove(item_id)
                    else:
                        self.items_seleccionados.add(item_id)
                    pygame.time.wait(150)  # Debounce
                
                # Texto
                texto = self.font_tiny.render(nombre, True, (200, 200, 200))
                self.screen.blit(texto, (col_izq_x + 32, y_izq))
                y_izq += 20
        
        y_izq += 5
        
        # === EQUIPO DESPLEGABLE ===
        simbolo_eq = "▼" if self.modal_seccion_equipo_expandida else "▶"
        equipo_list = list(self.equipo_db.items())
        texto_eq = self.font_tiny.render(f"{simbolo_eq} Equipo ({len(equipo_list)}):", True, (200, 220, 255))
        header_eq_rect = pygame.Rect(col_izq_x, y_izq, col_izq_ancho - 20, 22)
        pygame.draw.rect(self.screen, (50, 50, 55), header_eq_rect)
        pygame.draw.rect(self.screen, (80, 80, 90), header_eq_rect, 1)
        self.screen.blit(texto_eq, (col_izq_x + 5, y_izq + 3))
        
        # Click en header para expandir/colapsar
        if header_eq_rect.collidepoint(mx, my) and click:
            self.modal_seccion_equipo_expandida = not self.modal_seccion_equipo_expandida
            pygame.time.wait(150)
        
        y_izq += 24
        
        # Contenido si está expandido
        if self.modal_seccion_equipo_expandida:
            for equipo_id, equipo_data in equipo_list[:8]:  # Máximo 8 items
                nombre = equipo_data.get('nombre', equipo_id)[:28]
                
                # Checkbox
                checkbox_rect = pygame.Rect(col_izq_x + 10, y_izq, 16, 16)
                pygame.draw.rect(self.screen, (100, 100, 100), checkbox_rect, 1)
                
                if equipo_id in self.equipo_seleccionado:
                    pygame.draw.rect(self.screen, (100, 255, 100), checkbox_rect.inflate(-4, -4))
                
                # Detectar click en checkbox
                if checkbox_rect.collidepoint(mx, my) and click:
                    if equipo_id in self.equipo_seleccionado:
                        self.equipo_seleccionado.remove(equipo_id)
                    else:
                        self.equipo_seleccionado.add(equipo_id)
                    pygame.time.wait(150)  # Debounce
                
                # Texto
                texto = self.font_tiny.render(nombre, True, (200, 200, 200))
                self.screen.blit(texto, (col_izq_x + 32, y_izq))
                y_izq += 20
        
        y_izq += 5
        
        # === ESPECIALES DESPLEGABLE ===
        simbolo_esp = "▼" if self.modal_seccion_especiales_expandida else "▶"
        especiales_list = list(self.especiales_db.items())
        texto_esp_disp = self.font_tiny.render(f"{simbolo_esp} Especiales ({len(especiales_list)}):", True, (200, 220, 255))
        header_esp_rect = pygame.Rect(col_izq_x, y_izq, col_izq_ancho - 20, 22)
        pygame.draw.rect(self.screen, (50, 50, 55), header_esp_rect)
        pygame.draw.rect(self.screen, (80, 80, 90), header_esp_rect, 1)
        self.screen.blit(texto_esp_disp, (col_izq_x + 5, y_izq + 3))
        
        # Click en header para expandir/colapsar
        if header_esp_rect.collidepoint(mx, my) and click:
            self.modal_seccion_especiales_expandida = not self.modal_seccion_especiales_expandida
            pygame.time.wait(150)
        
        y_izq += 24
        
        # Contenido si está expandido
        if self.modal_seccion_especiales_expandida:
            for esp_id, esp_data in especiales_list[:8]:  # Máximo 8 items
                nombre = esp_data.get('nombre', esp_id)[:28]
                
                # Checkbox
                checkbox_rect = pygame.Rect(col_izq_x + 10, y_izq, 16, 16)
                pygame.draw.rect(self.screen, (100, 100, 100), checkbox_rect, 1)
                
                if esp_id in self.especiales_seleccionados:
                    pygame.draw.rect(self.screen, (100, 255, 100), checkbox_rect.inflate(-4, -4))
                
                # Detectar click en checkbox
                if checkbox_rect.collidepoint(mx, my) and click:
                    if esp_id in self.especiales_seleccionados:
                        self.especiales_seleccionados.remove(esp_id)
                    else:
                        self.especiales_seleccionados.add(esp_id)
                    pygame.time.wait(150)  # Debounce
                
                # Texto
                texto = self.font_tiny.render(nombre, True, (200, 200, 200))
                self.screen.blit(texto, (col_izq_x + 32, y_izq))
                y_izq += 20
        
        y_izq += 10
        
        # === BOTÓN AGREGAR SELECCIONADOS (más prominente) ===
        btn_agregar = pygame.Rect(col_izq_x + 10, y_izq, 220, 45)
        total_seleccionados = len(self.items_seleccionados) + len(self.equipo_seleccionado) + len(self.especiales_seleccionados)
        color_btn = (50, 200, 50) if total_seleccionados > 0 else (60, 60, 65)
        
        # Borde brillante si hay selección
        if total_seleccionados > 0:
            pygame.draw.rect(self.screen, (100, 255, 100), btn_agregar.inflate(6, 6), 3)
        
        pygame.draw.rect(self.screen, color_btn, btn_agregar)
        pygame.draw.rect(self.screen, (200, 200, 200) if total_seleccionados > 0 else (100, 100, 100), btn_agregar, 2)
        
        texto_agregar = self.font_small.render(f"AGREGAR ({total_seleccionados})", True, COLOR_TEXTO)
        texto_rect = texto_agregar.get_rect(center=btn_agregar.center)
        self.screen.blit(texto_agregar, texto_rect)
        
        if btn_agregar.collidepoint(mx, my) and click and total_seleccionados > 0:
            # Agregar items seleccionados al cofre con cantidad 1
            for item_id in self.items_seleccionados:
                if item_id not in cofre.items_contenido:
                    cofre.items_contenido[item_id] = 1
            for equipo_id in self.equipo_seleccionado:
                if equipo_id not in cofre.equipo_contenido:
                    cofre.equipo_contenido[equipo_id] = 1
            for esp_id in self.especiales_seleccionados:
                if esp_id not in cofre.especiales_contenido:
                    cofre.especiales_contenido[esp_id] = 1
            
            # Limpiar selecciones
            self.items_seleccionados.clear()
            self.equipo_seleccionado.clear()
            self.especiales_seleccionados.clear()
            pygame.time.wait(150)
        
        # === COLUMNA DERECHA: Contenido del Cofre con Inputs de Cantidad ===
        col_der_x = modal_x + 450
        col_der_ancho = 400
        y_der = y
        y_der_inicial = y  # Guardar posición inicial para detectar área
        
        texto_contenido = self.font_small.render("Contenido del Cofre (click cantidad para editar):", True, (255, 200, 100))
        self.screen.blit(texto_contenido, (col_der_x, y_der))
        y_der += 30
        
        # Items en el cofre
        texto_items = self.font_tiny.render("Items Consumibles:", True, COLOR_TEXTO)
        self.screen.blit(texto_items, (col_der_x, y_der))
        y_der += 20
        if cofre.items_contenido:
            for item_id, cant in list(cofre.items_contenido.items())[:12]:
                nombre = self.items_db.get(item_id, {}).get("nombre", item_id)[:20]
                
                # Nombre del item
                texto = self.font_tiny.render(f"  • {nombre}", True, COLOR_TEXTO)
                self.screen.blit(texto, (col_der_x + 10, y_der))
                
                # Input de cantidad
                input_x = col_der_x + 250
                input_rect = pygame.Rect(input_x, y_der - 2, 60, 18)
                pygame.draw.rect(self.screen, (60, 60, 60), input_rect)
                pygame.draw.rect(self.screen, (100, 100, 100), input_rect, 1)
                
                # Mostrar cantidad o input
                if self.editando_cantidad == ("items", item_id):
                    texto_cant = self.font_tiny.render(self.input_cantidad + "_", True, (255, 255, 100))
                else:
                    texto_cant = self.font_tiny.render(f"x {cant}", True, COLOR_TEXTO)
                
                self.screen.blit(texto_cant, (input_x + 5, y_der))
                
                # Click para editar
                if input_rect.collidepoint(mx, my) and click:
                    # Guardar cantidad anterior si existía
                    if self.editando_cantidad and self.input_cantidad:
                        tipo_anterior, item_anterior = self.editando_cantidad
                        try:
                            nueva_cant = int(self.input_cantidad)
                            if nueva_cant > 0:
                                if tipo_anterior == "items":
                                    cofre.items_contenido[item_anterior] = nueva_cant
                                elif tipo_anterior == "equipo":
                                    cofre.equipo_contenido[item_anterior] = nueva_cant
                                elif tipo_anterior == "especiales":
                                    cofre.especiales_contenido[item_anterior] = nueva_cant
                        except ValueError:
                            pass
                    
                    # Iniciar edición del nuevo campo
                    self.editando_cantidad = ("items", item_id)
                    self.input_cantidad = str(cant)
                    pygame.time.wait(150)
                
                # Botón eliminar (X)
                btn_x = pygame.Rect(input_x + 70, y_der - 2, 18, 18)
                pygame.draw.rect(self.screen, (150, 50, 50), btn_x)
                texto_x = self.font_tiny.render("X", True, COLOR_TEXTO)
                self.screen.blit(texto_x, (btn_x.x + 4, btn_x.y))
                
                if btn_x.collidepoint(mx, my) and click:
                    del cofre.items_contenido[item_id]
                    pygame.time.wait(150)
                
                y_der += 20
        else:
            texto = self.font_tiny.render("  (vacío)", True, (100, 100, 100))
            self.screen.blit(texto, (col_der_x + 10, y_der))
            y_der += 20
        
        y_der += 10
        
        # Equipo en el cofre
        texto_equipo = self.font_tiny.render("Equipo:", True, COLOR_TEXTO)
        self.screen.blit(texto_equipo, (col_der_x, y_der))
        y_der += 20
        if cofre.equipo_contenido:
            for equipo_id, cant in list(cofre.equipo_contenido.items())[:12]:
                nombre = self.equipo_db.get(equipo_id, {}).get("nombre", equipo_id)[:20]
                
                # Nombre del item
                texto = self.font_tiny.render(f"  • {nombre}", True, COLOR_TEXTO)
                self.screen.blit(texto, (col_der_x + 10, y_der))
                
                # Input de cantidad
                input_x = col_der_x + 250
                input_rect = pygame.Rect(input_x, y_der - 2, 60, 18)
                pygame.draw.rect(self.screen, (60, 60, 60), input_rect)
                pygame.draw.rect(self.screen, (100, 100, 100), input_rect, 1)
                
                # Mostrar cantidad o input
                if self.editando_cantidad == ("equipo", equipo_id):
                    texto_cant = self.font_tiny.render(self.input_cantidad + "_", True, (255, 255, 100))
                else:
                    texto_cant = self.font_tiny.render(f"x {cant}", True, COLOR_TEXTO)
                
                self.screen.blit(texto_cant, (input_x + 5, y_der))
                
                # Click para editar
                if input_rect.collidepoint(mx, my) and click:
                    # Guardar cantidad anterior si existía
                    if self.editando_cantidad and self.input_cantidad:
                        tipo_anterior, item_anterior = self.editando_cantidad
                        try:
                            nueva_cant = int(self.input_cantidad)
                            if nueva_cant > 0:
                                if tipo_anterior == "items":
                                    cofre.items_contenido[item_anterior] = nueva_cant
                                elif tipo_anterior == "equipo":
                                    cofre.equipo_contenido[item_anterior] = nueva_cant
                                elif tipo_anterior == "especiales":
                                    cofre.especiales_contenido[item_anterior] = nueva_cant
                        except ValueError:
                            pass
                    
                    # Iniciar edición del nuevo campo
                    self.editando_cantidad = ("equipo", equipo_id)
                    self.input_cantidad = str(cant)
                    pygame.time.wait(150)
                
                # Botón eliminar (X)
                btn_x = pygame.Rect(input_x + 70, y_der - 2, 18, 18)
                pygame.draw.rect(self.screen, (150, 50, 50), btn_x)
                texto_x = self.font_tiny.render("X", True, COLOR_TEXTO)
                self.screen.blit(texto_x, (btn_x.x + 4, btn_x.y))
                
                if btn_x.collidepoint(mx, my) and click:
                    del cofre.equipo_contenido[equipo_id]
                    pygame.time.wait(150)
                
                y_der += 20
        else:
            texto = self.font_tiny.render("  (vacío)", True, (100, 100, 100))
            self.screen.blit(texto, (col_der_x + 10, y_der))
            y_der += 20
        
        y_der += 10
        
        # Especiales en el cofre
        texto_esp = self.font_tiny.render("Items Especiales:", True, COLOR_TEXTO)
        self.screen.blit(texto_esp, (col_der_x, y_der))
        y_der += 20
        if cofre.especiales_contenido:
            for esp_id, cant in list(cofre.especiales_contenido.items())[:12]:
                nombre = self.especiales_db.get(esp_id, {}).get("nombre", esp_id)[:20]
                
                # Nombre del item
                texto = self.font_tiny.render(f"  • {nombre}", True, COLOR_TEXTO)
                self.screen.blit(texto, (col_der_x + 10, y_der))
                
                # Input de cantidad
                input_x = col_der_x + 250
                input_rect = pygame.Rect(input_x, y_der - 2, 60, 18)
                pygame.draw.rect(self.screen, (60, 60, 60), input_rect)
                pygame.draw.rect(self.screen, (100, 100, 100), input_rect, 1)
                
                # Mostrar cantidad o input
                if self.editando_cantidad == ("especiales", esp_id):
                    texto_cant = self.font_tiny.render(self.input_cantidad + "_", True, (255, 255, 100))
                else:
                    texto_cant = self.font_tiny.render(f"x {cant}", True, COLOR_TEXTO)
                
                self.screen.blit(texto_cant, (input_x + 5, y_der))
                
                # Click para editar
                if input_rect.collidepoint(mx, my) and click:
                    # Guardar cantidad anterior si existía
                    if self.editando_cantidad and self.input_cantidad:
                        tipo_anterior, item_anterior = self.editando_cantidad
                        try:
                            nueva_cant = int(self.input_cantidad)
                            if nueva_cant > 0:
                                if tipo_anterior == "items":
                                    cofre.items_contenido[item_anterior] = nueva_cant
                                elif tipo_anterior == "equipo":
                                    cofre.equipo_contenido[item_anterior] = nueva_cant
                                elif tipo_anterior == "especiales":
                                    cofre.especiales_contenido[item_anterior] = nueva_cant
                        except ValueError:
                            pass
                    
                    # Iniciar edición del nuevo campo
                    self.editando_cantidad = ("especiales", esp_id)
                    self.input_cantidad = str(cant)
                    pygame.time.wait(150)
                
                # Botón eliminar (X)
                btn_x = pygame.Rect(input_x + 70, y_der - 2, 18, 18)
                pygame.draw.rect(self.screen, (150, 50, 50), btn_x)
                texto_x = self.font_tiny.render("X", True, COLOR_TEXTO)
                self.screen.blit(texto_x, (btn_x.x + 4, btn_x.y))
                
                if btn_x.collidepoint(mx, my) and click:
                    del cofre.especiales_contenido[esp_id]
                    pygame.time.wait(150)
                
                y_der += 20
        else:
            texto = self.font_tiny.render("  (vacío)", True, (100, 100, 100))
            self.screen.blit(texto, (col_der_x + 10, y_der))
            y_der += 20
        
        # === BOTONES ===
        # Botón generar loot random
        btn_random = pygame.Rect(modal_x + 20, modal_y + modal_alto - 80, 200, 40)
        pygame.draw.rect(self.screen, (50, 150, 50), btn_random)
        pygame.draw.rect(self.screen, COLOR_BORDE, btn_random, 2)
        texto_random = self.font_small.render("Generar Loot Random", True, COLOR_TEXTO)
        texto_rect = texto_random.get_rect(center=btn_random.center)
        self.screen.blit(texto_random, texto_rect)
        
        if btn_random.collidepoint(mx, my) and pygame.mouse.get_pressed()[0]:
            self._generar_loot_random(cofre)
        
        # Botón limpiar contenido
        btn_limpiar = pygame.Rect(modal_x + 240, modal_y + modal_alto - 80, 150, 40)
        pygame.draw.rect(self.screen, (150, 100, 50), btn_limpiar)
        pygame.draw.rect(self.screen, COLOR_BORDE, btn_limpiar, 2)
        texto_limpiar = self.font_small.render("Limpiar Cofre", True, COLOR_TEXTO)
        texto_rect = texto_limpiar.get_rect(center=btn_limpiar.center)
        self.screen.blit(texto_limpiar, texto_rect)
        
        if btn_limpiar.collidepoint(mx, my) and pygame.mouse.get_pressed()[0]:
            cofre.items_contenido = {}
            cofre.equipo_contenido = {}
            cofre.especiales_contenido = {}
            cofre.oro = 0
        
        # Botón cerrar
        btn_cerrar = pygame.Rect(modal_x + modal_ancho - 120, modal_y + modal_alto - 60, 100, 40)
        pygame.draw.rect(self.screen, (150, 50, 50), btn_cerrar)
        pygame.draw.rect(self.screen, COLOR_BORDE, btn_cerrar, 2)
        texto_cerrar = self.font_small.render("Cerrar", True, COLOR_TEXTO)
        texto_rect = texto_cerrar.get_rect(center=btn_cerrar.center)
        self.screen.blit(texto_cerrar, texto_rect)
        
        if btn_cerrar.collidepoint(mx, my) and pygame.mouse.get_pressed()[0]:
            # Guardar cantidad antes de cerrar
            if self.editando_cantidad and self.input_cantidad:
                tipo, item_id = self.editando_cantidad
                try:
                    nueva_cant = int(self.input_cantidad)
                    if tipo == "oro":
                        if nueva_cant >= 0:
                            cofre.oro = nueva_cant
                    elif nueva_cant > 0:
                        if tipo == "items":
                            cofre.items_contenido[item_id] = nueva_cant
                        elif tipo == "equipo":
                            cofre.equipo_contenido[item_id] = nueva_cant
                        elif tipo == "especiales":
                            cofre.especiales_contenido[item_id] = nueva_cant
                except ValueError:
                    pass
            
            self.editando_cantidad = None
            self.input_cantidad = ""
            self.modal_abierto = False
            self.modal_cofre = None
        
        # Detectar click fuera de inputs para guardar y deseleccionar
        if click and self.editando_cantidad:
            # Si el click no fue dentro del modal, guardar
            if not modal_rect.collidepoint(mx, my):
                tipo, item_id = self.editando_cantidad
                try:
                    nueva_cant = int(self.input_cantidad)
                    if tipo == "oro":
                        if nueva_cant >= 0:
                            cofre.oro = nueva_cant
                    elif nueva_cant > 0:
                        if tipo == "items":
                            cofre.items_contenido[item_id] = nueva_cant
                        elif tipo == "equipo":
                            cofre.equipo_contenido[item_id] = nueva_cant
                        elif tipo == "especiales":
                            cofre.especiales_contenido[item_id] = nueva_cant
                except ValueError:
                    pass
                self.editando_cantidad = None
                self.input_cantidad = ""
    
    def _draw_ayuda(self):
        """Dibuja ventana de ayuda"""
        ayuda_ancho, ayuda_alto = 600, 500
        x = (ANCHO - ayuda_ancho) // 2
        y = (ALTO - ayuda_alto) // 2
        
        pygame.draw.rect(self.screen, COLOR_PANEL, (x, y, ayuda_ancho, ayuda_alto))
        pygame.draw.rect(self.screen, COLOR_BORDE, (x, y, ayuda_ancho, ayuda_alto), 3)
        
        titulo = self.font.render("Controles", True, COLOR_TEXTO)
        self.screen.blit(titulo, (x + 20, y + 20))
        
        controles = [
            "Click Izq: Colocar/Seleccionar cofre",
            "Click Der: Abrir modal de edición",
            "Arrastrar borde: Redimensionar cofre",
            "Click Der + Arrastrar: Mover mapa (pan)",
            "Rueda: Zoom",
            "DEL: Eliminar cofre seleccionado",
            "Ctrl+C: Copiar cofre seleccionado",
            "Ctrl+V: Pegar cofre en posición del mouse",
            "G: Guardar mapa",
            "H: Mostrar/Ocultar ayuda",
            "ESC: Salir",
            "",
            "En Modal:",
            "- Click en tipo: Cambiar tipo de cofre",
            "- Random Oro: Generar oro aleatorio",
            "- Generar Loot Random: Llenar cofre",
            "- Checkboxes: Seleccionar items",
            "- AGREGAR: Añadir items al cofre",
            "- Click cantidad: Editar (auto-guarda)",
        ]
        
        y_texto = y + 60
        for linea in controles:
            texto = self.font_tiny.render(linea, True, COLOR_TEXTO)
            self.screen.blit(texto, (x + 20, y_texto))
            y_texto += 25
    
    def _draw_overlay(self):
        """Dibuja información en pantalla"""
        if self.mapa_actual:
            texto = self.font_small.render(f"Mapa: {self.mapa_actual.nombre} | Cofres: {len(self.cofres)} | Zoom: {self.mapa_zoom:.2f}x", True, COLOR_TEXTO)
            self.screen.blit(texto, (PANEL_ANCHO + 10, 10))
        
        if self.cofre_seleccionado:
            texto = self.font_small.render(f"Seleccionado: {self.cofre_seleccionado.nombre} ({self.cofre_seleccionado.ancho}x{self.cofre_seleccionado.alto})", True, COLOR_SELECCION)
            self.screen.blit(texto, (PANEL_ANCHO + 10, 40))
        
        # Indicador de cofre copiado
        if self.cofre_copiado:
            texto = self.font_tiny.render(f"[Portapapeles: {self.cofre_copiado.nombre}] Ctrl+V para pegar", True, (150, 255, 150))
            self.screen.blit(texto, (PANEL_ANCHO + 10, 70))
        
        # Indicador de drag & drop
        if self.arrastrando_mapa and self.mapa_arrastrado:
            mx, my = pygame.mouse.get_pos()
            if mx > PANEL_ANCHO:
                texto = self.font.render(f"Soltar para cargar: {self.mapa_arrastrado.nombre}", True, COLOR_SELECCION)
                rect_texto = texto.get_rect(center=(ANCHO // 2, ALTO // 2))
                # Fondo semi-transparente
                fondo = pygame.Surface((rect_texto.width + 40, rect_texto.height + 20), pygame.SRCALPHA)
                fondo.fill((0, 0, 0, 200))
                self.screen.blit(fondo, (rect_texto.x - 20, rect_texto.y - 10))
                self.screen.blit(texto, rect_texto)

# === MAIN ===
if __name__ == "__main__":
    editor = EditorCofres()
    editor.run()
