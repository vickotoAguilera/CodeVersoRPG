# Guía de Refactorización - Code Verso RPG

Este documento explica el proceso de refactorización del proyecto y los pasos para completarlo.

---

## Estado Actual

### ✅ Completado

1. **Documentación**
   - ✅ ARQUITECTURA.md - Arquitectura completa del sistema
   - ✅ DATABASE.md - Documentación de base de datos
   - ✅ README.md - Documentación de usuario
   - ✅ Este archivo (REFACTORIZACION.md)

2. **Configuración**
   - ✅ constants.py - Todas las constantes centralizadas
   - ✅ requirements.txt - Dependencias del proyecto
   - ✅ settings_nuevo.json - Configuración completa
   - ✅ setup_structure.py - Script para crear directorios

3. **Limpieza**
   - ✅ Identificados archivos con chilenismos
   - ✅ Identificados archivos a refactorizar
   - ✅ Plan de migración creado

### 🔄 En Progreso

- Creación de estructura de directorios
- Implementación del core del motor
- Refactorización de archivos existentes

### ⏳ Pendiente

- Migración completa de código antiguo
- Tests unitarios
- Validación de JSON schemas

---

## Plan de Refactorización

### Fase 1: Preparación (ACTUAL)

**Objetivo:** Crear la infraestructura y documentación

#### Pasos:

1. **Crear estructura de directorios**
   ```bash
   python setup_structure.py
   ```
   
   Esto creará:
   - src/core/
   - src/states/
   - src/entities/
   - src/systems/
   - src/ui/
   - src/world/
   - src/data/
   - src/utils/
   - database/schemas/
   - logs/
   - tests/

2. **Reemplazar settings.json**
   ```bash
   # En Windows
   del settings.json
   ren settings_nuevo.json settings.json
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

---

### Fase 2: Core del Motor

**Objetivo:** Implementar el núcleo del motor de juego

#### Archivos a crear:

1. **src/core/logger.py**
   - Sistema de logging robusto
   - Ya documentado en ARQUITECTURA.md
   - Implementar según especificaciones

2. **src/core/resource_manager.py**
   - Gestor de recursos singleton
   - Carga y cache de JSON
   - Carga y cache de imágenes
   - Validación de recursos

3. **src/core/input_manager.py**
   - Captura y procesamiento de input
   - Mapeo configurable de teclas
   - Cooldowns de input
   - Soporte para controles

4. **src/core/state_machine.py**
   - Máquina de estados
   - Gestión de transiciones
   - Historial de estados
   - Validación de transiciones

5. **src/core/game_engine.py**
   - Motor principal
   - Bucle de juego
   - Coordinación de componentes
   - Gestión de FPS

#### Código base para logger.py:

```python
"""
Sistema de logging robusto.
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

class GameLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def setup(self, logs_dir='logs', nivel=logging.INFO):
        """Configura el sistema de logging."""
        # Implementación aquí
        pass
    
    def get_logger(self, nombre=None):
        """Obtiene un logger específico."""
        # Implementación aquí
        pass

_game_logger = GameLogger()

def setup_logging(logs_dir='logs', nivel=logging.INFO):
    _game_logger.setup(logs_dir, nivel)

def get_logger(nombre=None):
    return _game_logger.get_logger(nombre)
```

---

### Fase 3: Migración de Entidades

**Objetivo:** Refactorizar clases de entidades existentes

#### Archivos a migrar:

1. **src/heroe.py → src/entities/heroe.py**
   
   Cambios:
   - Eliminar chilenismos de comentarios
   - Usar español neutro
   - Añadir docstrings formales
   - Separar lógica de renderizado (futura mejora)
   - Usar constantes de `constants.py`
   - Añadir type hints
   
   Ejemplo:
   ```python
   """
   Módulo de la entidad Héroe.
   Define la clase Heroe con todas sus propiedades y comportamientos.
   """
   
   from typing import Dict, List, Optional
   import pygame
   from src.constants import VELOCIDAD_ANIM_HEROE_MS
   from src.core.logger import get_logger
   
   logger = get_logger('Heroe')
   
   class Heroe:
       """
       Representa un héroe jugable.
       
       Attributes:
           nombre_en_juego (str): Nombre personalizado del héroe
           nombre_clase (str): Nombre de la clase (ej: Guerrero)
           HP_actual (int): Puntos de vida actuales
           HP_max (int): Puntos de vida máximos
           # ... etc
       """
       
       def __init__(
           self,
           nombre_en_juego: str,
           clase_data: Dict,
           coords_data: Dict,
           equipo_db: Dict,
           habilidades_db: Dict
       ):
           """
           Inicializa un nuevo héroe.
           
           Args:
               nombre_en_juego: Nombre personalizado
               clase_data: Datos de la clase desde heroes_db.json
               coords_data: Coordenadas de sprites
               equipo_db: Base de datos de equipo
               habilidades_db: Base de datos de habilidades
           """
           logger.info(f"Creando héroe: {nombre_en_juego}")
           # Implementación...
   ```

2. **src/monstruo.py → src/entities/monstruo.py**
   
   Similar proceso a Heroe

3. **Crear src/entities/grupo.py**
   
   Nueva clase para gestionar grupo de héroes:
   ```python
   """
   Módulo de gestión de grupos de héroes.
   """
   
   from typing import List
   from src.entities.heroe import Heroe
   from src.constants import MAX_HEROES_GRUPO
   
   class Grupo:
       """
       Gestiona un grupo de héroes.
       
       Attributes:
           heroes (List[Heroe]): Lista de héroes en el grupo
           lider (Heroe): Héroe líder (primero de la lista)
       """
       
       def __init__(self):
           """Inicializa un grupo vacío."""
           self.heroes: List[Heroe] = []
       
       def agregar_heroe(self, heroe: Heroe) -> bool:
           """
           Agrega un héroe al grupo.
           
           Args:
               heroe: Héroe a agregar
               
           Returns:
               True si se agregó exitosamente, False si el grupo está lleno
           """
           if len(self.heroes) >= MAX_HEROES_GRUPO:
               return False
           self.heroes.append(heroe)
           return True
       
       @property
       def lider(self) -> Heroe:
           """Retorna el héroe líder."""
           return self.heroes[0] if self.heroes else None
       
       def todos_vivos(self) -> bool:
           """Verifica si todos los héroes están vivos."""
           return all(not h.esta_muerto() for h in self.heroes)
       
       def curar_todos(self):
           """Cura completamente a todos los héroes vivos."""
           for heroe in self.heroes:
               if not heroe.esta_muerto():
                   heroe.HP_actual = heroe.HP_max
                   heroe.MP_actual = heroe.MP_max
   ```

---

### Fase 4: Sistemas

**Objetivo:** Crear sistemas de juego modulares

#### Archivos a crear:

1. **src/systems/batalla_system.py**
   - Migrar lógica de `src/batalla.py`
   - Limpiar y modularizar
   - Separar UI de lógica

2. **src/systems/guardado_system.py**
   - Migrar de `src/gestor_guardado.py`
   - Añadir validación
   - Mejorar manejo de errores

3. **src/systems/inventario_system.py**
   - Nueva clase para gestionar inventario
   - Separar de Heroe

4. **src/systems/equipo_system.py**
   - Nueva clase para gestionar equipamiento
   - Separar de Heroe

5. **src/systems/progresion_system.py**
   - Nueva clase para XP y niveles
   - Separar de Heroe

---

### Fase 5: Estados

**Objetivo:** Implementar máquina de estados

#### Archivos a crear:

1. **src/states/base_state.py**
   ```python
   """
   Estado base abstracto.
   """
   
   from abc import ABC, abstractmethod
   import pygame
   
   class BaseState(ABC):
       """
       Clase base abstracta para todos los estados del juego.
       """
       
       def __init__(self, game_engine):
           """
           Inicializa el estado.
           
           Args:
               game_engine: Referencia al motor del juego
           """
           self.game_engine = game_engine
           self.next_state = None
       
       @abstractmethod
       def enter(self):
           """Llamado al entrar al estado."""
           pass
       
       @abstractmethod
       def exit(self):
           """Llamado al salir del estado."""
           pass
       
       @abstractmethod
       def update(self, dt: float):
           """
           Actualiza la lógica del estado.
           
           Args:
               dt: Delta time en segundos
           """
           pass
       
       @abstractmethod
       def draw(self, pantalla: pygame.Surface):
           """
           Renderiza el estado.
           
           Args:
               pantalla: Superficie donde dibujar
           """
           pass
       
       @abstractmethod
       def handle_input(self, eventos: list):
           """
           Maneja eventos de entrada.
           
           Args:
               eventos: Lista de eventos de Pygame
           """
           pass
   ```

2. **src/states/titulo_state.py**
3. **src/states/mapa_state.py**
4. **src/states/batalla_state.py**
5. **src/states/menu_pausa_state.py**
6. **src/states/slots_state.py**

---

### Fase 6: UI

**Objetivo:** Refactorizar interfaces de usuario

#### Proceso para cada archivo UI:

1. Copiar de `src/pantalla_*.py` a `src/ui/pantalla_*.py`
2. Eliminar chilenismos
3. Añadir docstrings
4. Usar constantes
5. Mejorar nombres de variables
6. Añadir type hints

#### Ejemplo de transformación:

**Antes:**
```python
# ¡"Recableado" (MODIFICADO) BKN! (Paso 56.7)
# Este es el "Motor" (Engine) de UI BKN

class PantallaMagia:
    def __init__(self, ancho_pantalla, alto_pantalla, heroe_actor, magia_db_completa, cursor_img_bkn):
        print(f"¡Abriendo Pantalla de Magia para {heroe_actor.nombre_clase}!")
        self.ANCHO = ancho_pantalla
        self.ALTO = alto_pantalla
        # ... etc
```

**Después:**
```python
"""
Módulo de la interfaz de selección de magia en batalla.
"""

from typing import Dict, Optional
import pygame
from src.entities.heroe import Heroe
from src.constants import *
from src.core.logger import get_logger

logger = get_logger('PantallaMagia')

class PantallaMagia:
    """
    Interfaz para seleccionar y usar magia durante el combate.
    
    Attributes:
        ancho (int): Ancho de la pantalla
        alto (int): Alto de la pantalla
        heroe_actor (Heroe): Héroe que usa la magia
        magia_db (Dict): Base de datos de magia
        cursor_img (pygame.Surface): Imagen del cursor
    """
    
    def __init__(
        self,
        ancho: int,
        alto: int,
        heroe_actor: Heroe,
        magia_db: Dict,
        cursor_img: Optional[pygame.Surface]
    ):
        """
        Inicializa la pantalla de magia.
        
        Args:
            ancho: Ancho de la pantalla
            alto: Alto de la pantalla
            heroe_actor: Héroe que usará la magia
            magia_db: Diccionario con datos de todas las magias
            cursor_img: Imagen del cursor (None para usar texto)
        """
        logger.info(f"Abriendo pantalla de magia para {heroe_actor.nombre_clase}")
        self.ancho = ancho
        self.alto = alto
        # ... etc
```

---

### Fase 7: Validación

**Objetivo:** Añadir validación de datos

#### Archivos a crear:

1. **src/data/schemas.py**
   ```python
   """
   Schemas de validación para archivos JSON.
   """
   
   HERO_SCHEMA = {
       "required": ["nombre_clase", "hp_max", "mp_max", "fuerza", ...],
       "properties": {
           "nombre_clase": {"type": "string"},
           "hp_max": {"type": "integer", "minimum": 1},
           "mp_max": {"type": "integer", "minimum": 0},
           # ... etc
       }
   }
   
   ITEM_SCHEMA = {
       # ... similar
   }
   ```

2. **src/data/validators.py**
   ```python
   """
   Validadores de datos JSON.
   """
   
   def validar_heroe(data: dict) -> tuple[bool, str]:
       """
       Valida datos de un héroe.
       
       Args:
           data: Diccionario con datos del héroe
           
       Returns:
           (es_valido, mensaje_error)
       """
       # Implementación
       pass
   ```

3. **src/data/database_manager.py**
   - Interfaz única para acceder a todos los datos
   - Carga con validación
   - Cache de datos

---

### Fase 8: Testing

**Objetivo:** Añadir tests unitarios

#### Tests a crear:

1. **tests/test_heroe.py**
   ```python
   """
   Tests para la clase Heroe.
   """
   
   import pytest
   from src.entities.heroe import Heroe
   
   def test_heroe_creacion():
       """Test de creación básica de héroe."""
       # Implementación
       pass
   
   def test_heroe_recibe_daño():
       """Test de recepción de daño."""
       # Implementación
       pass
   ```

2. **tests/test_batalla.py**
3. **tests/test_guardado.py**
4. **tests/test_inventario.py**

---

### Fase 9: Migración Final

**Objetivo:** Reemplazar el main.py antiguo

#### Nuevo main.py:

```python
"""
Punto de entrada del juego Code Verso RPG.
"""

import sys
import logging
from src.core.logger import setup_logging
from src.core.game_engine import GameEngine
from src.constants import VERSION_JUEGO

def main():
    """Función principal del juego."""
    # Configurar logging
    setup_logging(nivel=logging.INFO)
    
    # Crear e iniciar el motor del juego
    try:
        engine = GameEngine()
        engine.run()
    except Exception as e:
        logging.critical(f"Error fatal: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    print(f"Code Verso RPG v{VERSION_JUEGO}")
    print("Iniciando juego...")
    main()
```

---

## Archivos a Eliminar/Archivar

### Después de completar la migración:

1. **Archivos originales** (mantener como backup en carpeta `old/`):
   - main.py (original)
   - src/batalla.py
   - src/heroe.py
   - src/monstruo.py
   - src/gestor_guardado.py
   - src/asset_coords_db.py (migrar a utils/)
   - Todas las pantallas originales

2. **Archivos temporales**:
   - check_errors.py
   - setup_structure.py (después de usar)

---

## Checklist de Tareas

### Preparación
- [ ] Ejecutar `python setup_structure.py`
- [ ] Reemplazar settings.json
- [ ] Instalar dependencias
- [ ] Crear backup del código original

### Core
- [ ] Implementar logger.py
- [ ] Implementar resource_manager.py
- [ ] Implementar input_manager.py
- [ ] Implementar state_machine.py
- [ ] Implementar game_engine.py

### Entidades
- [ ] Refactorizar heroe.py
- [ ] Refactorizar monstruo.py
- [ ] Crear grupo.py

### Sistemas
- [ ] Crear batalla_system.py
- [ ] Crear guardado_system.py
- [ ] Crear inventario_system.py
- [ ] Crear equipo_system.py
- [ ] Crear progresion_system.py

### Estados
- [ ] Crear base_state.py
- [ ] Crear titulo_state.py
- [ ] Crear mapa_state.py
- [ ] Crear batalla_state.py
- [ ] Crear menu_pausa_state.py
- [ ] Crear slots_state.py

### UI
- [ ] Refactorizar pantalla_titulo.py
- [ ] Refactorizar pantalla_slots.py
- [ ] Refactorizar menu_pausa.py
- [ ] Refactorizar pantalla_estado.py
- [ ] Refactorizar pantalla_equipo.py
- [ ] Refactorizar pantalla_inventario.py
- [ ] Refactorizar pantalla_magia.py
- [ ] Refactorizar pantalla_items.py
- [ ] Refactorizar pantalla_victoria.py
- [ ] Refactorizar texto_flotante.py

### World
- [ ] Refactorizar mapa.py
- [ ] Crear zona.py

### Data
- [ ] Crear schemas.py
- [ ] Crear validators.py
- [ ] Crear database_manager.py
- [ ] Refactorizar game_data.py

### Utils
- [ ] Migrar asset_coords_db.py
- [ ] Crear helpers.py

### Testing
- [ ] Crear test_heroe.py
- [ ] Crear test_monstruo.py
- [ ] Crear test_batalla.py
- [ ] Crear test_guardado.py
- [ ] Crear test_inventario.py
- [ ] Crear test_resource_manager.py

### Final
- [ ] Crear nuevo main.py
- [ ] Probar juego completo
- [ ] Archivar código antiguo
- [ ] Actualizar documentación
- [ ] Commit final

---

## Estimación de Tiempo

- **Fase 1 (Preparación):** 1 hora
- **Fase 2 (Core):** 8-10 horas
- **Fase 3 (Entidades):** 4-6 horas
- **Fase 4 (Sistemas):** 8-10 horas
- **Fase 5 (Estados):** 10-12 horas
- **Fase 6 (UI):** 8-10 horas
- **Fase 7 (Validación):** 4-6 horas
- **Fase 8 (Testing):** 10-12 horas
- **Fase 9 (Migración Final):** 2-4 horas

**Total estimado:** 55-71 horas

---

## Siguientes Pasos Inmediatos

1. **Ejecutar setup_structure.py** para crear directorios
2. **Comenzar con Phase 2** - Implementar el core
3. **Probar cada componente** antes de continuar al siguiente
4. **Mantener el código antiguo funcionando** hasta completar la migración

---

## Soporte

Si tienes dudas durante la refactorización:

1. Consulta ARQUITECTURA.md para entender la estructura
2. Consulta DATABASE.md para datos
3. Revisa los ejemplos de código en este documento
4. Usa el sistema de logging para debugging

---

**Última actualización:** 2025-11-15  
**Versión:** 1.0
