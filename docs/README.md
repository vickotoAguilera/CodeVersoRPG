# Code Verso RPG

Un juego de rol (RPG) 2D desarrollado en Python con Pygame.

## Versión

**Versión actual:** 1.0.0  
**Estado:** Refactorización en progreso

---

## Instalación

### Requisitos

- Python 3.8 o superior
- Pygame 2.0 o superior

### Configuración Inicial

1. **Clonar o descargar el proyecto**

2. **Crear entorno virtual (recomendado)**
   ```bash
   python -m venv .venv
   ```

3. **Activar entorno virtual**
   - Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source .venv/bin/activate
     ```

4. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configurar estructura de directorios**
   ```bash
   python setup_structure.py
   ```

---

## Uso

### Ejecutar el juego

```bash
python main.py
```

### Controles

- **Flechas:** Movimiento / Navegación en menús
- **Enter:** Confirmar / Interactuar
- **ESC:** Abrir menú de pausa / Volver
- **D:** Ver detalles (en pantallas de equipo/items)

---

## Estructura del Proyecto

```
RPG/
├── main.py                 # Punto de entrada
├── setup_structure.py      # Script de configuración
├── requirements.txt        # Dependencias
├── settings.json           # Configuración del juego
├── README.md               # Este archivo
├── ARQUITECTURA.md         # Documentación técnica
│
├── src/                    # Código fuente
│   ├── config.py           # Configuración de rutas
│   ├── constants.py        # Constantes del juego
│   ├── core/               # Motor del juego
│   ├── states/             # Estados del juego
│   ├── entities/           # Entidades (Héroe, Monstruo)
│   ├── systems/            # Sistemas (Batalla, Inventario)
│   ├── ui/                 # Interfaz de usuario
│   ├── world/              # Mundo (Mapas, Zonas)
│   ├── data/               # Gestión de datos
│   └── utils/              # Utilidades
│
├── database/               # Base de datos del juego
│   ├── heroes_db.json
│   ├── equipo_db.json
│   ├── items_db.json
│   ├── habilidades_db.json
│   ├── magia_db.json
│   ├── monstruos_db.json
│   ├── grupo_inicial.json
│   ├── mapas/              # Datos de mapas por categoría
│   ├── monstruos/          # Encuentros por zona
│   └── schemas/            # Esquemas de validación
│
├── assets/                 # Recursos gráficos y audio
│   ├── sprites/
│   │   ├── heroes/
│   │   └── monstruos/
│   ├── maps/
│   │   ├── mundo/
│   │   └── pueblo_inicial/
│   ├── backgrounds/
│   ├── ui/
│   └── audio/
│
├── saves/                  # Partidas guardadas
├── logs/                   # Archivos de log
└── tests/                  # Tests unitarios
```

---

## Características

### Implementadas

✅ Sistema de combate por turnos  
✅ Exploración de mapas  
✅ Sistema de guardado/carga  
✅ Inventario y equipamiento  
✅ Sistema de habilidades y magia  
✅ Progresión de personajes (XP y niveles)  
✅ Menú de pausa con múltiples opciones  
✅ Autoguardado periódico  
✅ Portales entre mapas  
✅ Zonas seguras y de combate  

### En Desarrollo

🔄 Sistema de misiones  
🔄 Tiendas y NPCs  
🔄 Sistema de diálogos  
🔄 Más mapas y zonas  
🔄 Animaciones de batalla mejoradas  
🔄 Sistema de audio  

---

## Configuración

### settings.json

El archivo `settings.json` permite configurar:

```json
{
    "video": {
        "ancho": 800,
        "alto": 600,
        "pantalla_completa": false,
        "vsync": true
    },
    "audio": {
        "volumen_musica": 0.7,
        "volumen_efectos": 0.8,
        "silenciado": false
    },
    "juego": {
        "dificultad": "normal",
        "mostrar_fps": false,
        "idioma": "es"
    },
    "controles": {
        "arriba": "UP",
        "abajo": "DOWN",
        "izquierda": "LEFT",
        "derecha": "RIGHT",
        "confirmar": "RETURN",
        "cancelar": "ESCAPE"
    }
}
```

---

## Base de Datos

### Archivos JSON

El juego utiliza archivos JSON para almacenar datos:

- **heroes_db.json:** Definiciones de clases de héroes
- **equipo_db.json:** Armas, armaduras y accesorios
- **items_db.json:** Items consumibles
- **habilidades_db.json:** Habilidades físicas
- **magia_db.json:** Hechizos mágicos
- **monstruos_db.json:** Definiciones de enemigos
- **grupo_inicial.json:** Composición inicial del grupo

### Mapas

Los datos de mapas están organizados por categoría en `database/mapas/`:

- `mundo/` - Mapas del mundo exterior
- `pueblo_inicial/` - Edificios del pueblo inicial
- etc.

Cada mapa tiene:
- Definición de muros (colisiones)
- Portales de teletransporte
- Zonas de batalla

---

## Desarrollo

### Añadir un Nuevo Héroe

1. Editar `database/heroes_db.json`
2. Añadir sprite en `assets/sprites/heroes/`
3. Definir coordenadas en `src/utils/asset_coords_db.py`
4. Actualizar `database/grupo_inicial.json` si es inicial

### Añadir un Nuevo Mapa

1. Crear imagen en `assets/maps/[categoría]/`
2. Crear JSON en `database/mapas/[categoría]/`
3. Definir muros, portales y zonas
4. Actualizar `src/data/game_data.py` con nombre legible

### Añadir Items/Equipo

1. Editar `database/items_db.json` o `database/equipo_db.json`
2. Añadir sprite si es necesario
3. Sistema automáticamente cargará los nuevos items

---

## Testing

### Ejecutar tests

```bash
python -m pytest tests/
```

### Ejecutar tests con cobertura

```bash
python -m pytest --cov=src tests/
```

### Ejecutar un test específico

```bash
python -m pytest tests/test_heroe.py
```

---

## Logging

Los logs se guardan en `logs/game_YYYY-MM-DD.log`

### Niveles de log:

- **DEBUG:** Información detallada para debugging
- **INFO:** Eventos normales del juego
- **WARNING:** Situaciones inesperadas pero manejables
- **ERROR:** Errores que impiden operaciones
- **CRITICAL:** Errores críticos

### Ver logs en tiempo real:

```bash
tail -f logs/game_2025-11-15.log
```

---

## Solución de Problemas

### El juego no inicia

1. Verificar que Python 3.8+ está instalado: `python --version`
2. Verificar que Pygame está instalado: `pip list | grep pygame`
3. Revisar logs en `logs/`

### Error de archivos no encontrados

1. Ejecutar `python setup_structure.py`
2. Verificar que todas las carpetas en `assets/` y `database/` existen
3. Revisar que los paths en `src/config.py` son correctos

### Problemas de guardado

1. Verificar que la carpeta `saves/` existe y tiene permisos de escritura
2. Revisar logs para errores de serialización
3. Borrar saves corruptos si es necesario

### Bajo rendimiento

1. Reducir resolución en `settings.json`
2. Deshabilitar VSync
3. Cerrar otros programas pesados

---

## Contribuir

### Estilo de Código

- **Idioma:** Español neutro (sin regionalismos)
- **Formato:** PEP 8
- **Docstrings:** Google Style
- **Type hints:** Usar donde sea posible

### Proceso

1. Fork del proyecto
2. Crear branch para feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit cambios (`git commit -am 'Añadir nueva característica'`)
4. Push al branch (`git push origin feature/nueva-caracteristica`)
5. Crear Pull Request

---

## Licencia

[Especificar licencia aquí]

---

## Créditos

### Desarrolladores
- [Tu nombre]

### Assets
- Sprites de héroes: [Fuente]
- Sprites de monstruos: [Fuente]
- Tiles de mapas: [Fuente]
- Música: [Fuente]
- Efectos de sonido: [Fuente]

### Herramientas
- Python 3.x
- Pygame 2.x
- [Otras herramientas]

---

## Contacto

- **Email:** [tu-email]
- **GitHub:** [tu-github]
- **Discord:** [tu-discord]

---

## Changelog

### v1.0.0 (2025-11-15)
- Refactorización completa del código
- Implementación de arquitectura robusta
- Sistema de logging
- Validación de datos
- Mejora de manejo de errores
- Documentación completa

### v0.x (versiones anteriores)
- Prototipo inicial
- Sistema de batalla básico
- Sistema de guardado
- Exploración de mapas

---

**¡Disfruta el juego!** 🎮
