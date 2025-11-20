# 🎮 GUÍA DE INICIO RÁPIDO - RPG Project

## 📦 INSTALACIÓN Y EJECUCIÓN

### 1. Verificar Python
```bash
python --version
```
Debe ser Python 3.8+

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Ejecutar el juego
```bash
python main.py
```

---

## 🎯 SISTEMA ACTUAL (Fase 7 - 90% Completo)

### ✅ Lo que está funcionando:

#### Sistema de Habilidades
- 10 habilidades únicas por héroe
- Sistema de ranuras activas (4 base)
- Equipar/desequipar habilidades
- Navegación completa por teclado
- Scroll visual en todas las ventanas
- Botón "Volver" funcional

#### Sistema de Batalla
- Menú de habilidades en batalla
- DOT (Damage Over Time) - Quemadura
- HOT (Heal Over Time) - Revitalizar, Éter
- Habilidades AoE (ataque a todos)
- Scroll en ventana de habilidades
- Navegación fluida entre menús

#### Interfaz de Usuario
- Scroll visual con barra lateral
- Descripciones scrolleables
- Navegación con flechas en todos los paneles
- Prevención de duplicación de habilidades

---

## 🔧 LO QUE FALTA PROBAR

### 1. Sistema de Expansor de Ranuras (IMPLEMENTADO - NECESITA PRUEBA)

**Cómo probar:**
1. Iniciar el juego
2. Ir a **Menú de Pausa** (ESC)
3. Seleccionar **Objetos**
4. Buscar **"Expansor de Ranuras"** (los héroes tienen 2 en inventario)
5. Usar en un héroe
6. Verificar que las ranuras aumentan de 4 a 6
7. Ir a **Habilidades** y verificar que ahora hay 6 ranuras disponibles

**Qué debe pasar:**
- El expansor se consume (-1 del inventario)
- Las ranuras del héroe aumentan +2
- El cambio es permanente (se guarda)
- Se pueden usar múltiples expansores (acumulativo)

---

## 📋 PRÓXIMOS PASOS

### Paso 1: Probar Expansor de Ranuras
```
1. Ejecutar: python main.py
2. Crear nueva partida o cargar existente
3. Ir a Objetos → Usar Expansor en Cloud
4. Ir a Habilidades → Verificar 6 ranuras
5. Equipar más habilidades
6. Guardar partida
7. Cargar partida → Verificar que persisten las 6 ranuras
```

### Paso 2: Organizar Inventario por Categorías
**Objetivo:** Separar objetos en pestañas
- Consumibles
- Equipo
- Especiales
- Varios

### Paso 3: Mejorar Scroll Visual
**Objetivo:** Agregar scroll a pantallas faltantes
- Pantalla de objetos
- Pantalla de equipo
- Lista de héroes

---

## 🎮 CONTROLES

### Navegación General
- **↑↓←→**: Mover entre opciones/paneles
- **ENTER**: Confirmar/Seleccionar
- **ESC**: Volver/Cancelar

### En Batalla
- **↑↓**: Seleccionar acción/objetivo
- **ENTER**: Confirmar acción
- **ESC**: Volver al menú anterior

### En Pantalla de Habilidades
- **↑↓**: Navegar en panel actual
- **←→**: Cambiar entre paneles
- **ENTER**: Equipar/Desequipar habilidad
- **ESC o Botón Volver**: Regresar al menú de pausa

---

## 📁 ESTRUCTURA DEL PROYECTO

```
RPG/
├── main.py                          # Punto de entrada principal
├── requirements.txt                 # Dependencias (pygame)
│
├── src/                             # Código fuente
│   ├── database/                    # Bases de datos JSON
│   │   ├── heroes_db.json          # Datos de héroes
│   │   ├── items_db.json           # Datos de ítems
│   │   ├── habilidades_db.json     # Datos de habilidades
│   │   ├── enemigos_db.json        # Datos de enemigos
│   │   └── mapas_db.json           # Datos de mapas
│   │
│   ├── heroe.py                     # Clase Heroe
│   ├── enemigo.py                   # Clase Enemigo
│   ├── mapa.py                      # Gestión de mapas
│   │
│   ├── menu_pausa.py                # Menú de pausa
│   ├── pantalla_inventario.py       # Pantalla de objetos
│   ├── pantalla_equipo.py           # Pantalla de equipo
│   ├── pantalla_habilidades.py      # Pantalla de habilidades ⭐
│   ├── pantalla_estado.py           # Pantalla de estado
│   ├── pantalla_batalla.py          # Sistema de batalla
│   └── menu_batalla.py              # Menú de combate
│
├── assets/                          # Recursos gráficos
│   ├── sprites/                     # Sprites de personajes
│   └── tilesets/                    # Tiles de mapas
│
├── saves/                           # Archivos de guardado
│
└── docs/                            # Documentación
    ├── TAREAS_PENDIENTES.md        # Lista de tareas
    ├── GUIA_INICIO_RAPIDO.md       # Esta guía
    └── INDICE_ARCHIVOS.md          # Índice detallado
```

---

## 🐛 TROUBLESHOOTING

### El juego no inicia
```bash
# Verificar instalación de pygame
pip install pygame

# Ejecutar con verbose
python main.py
```

### Error "RUTA_ITEMS_DB not defined"
- Ya está arreglado en la última versión
- Si persiste, verificar que `main.py` tenga las rutas correctas

### Las ranuras no se expanden
- Verificar que estás usando el expansor desde **Objetos** (no desde Habilidades)
- El expansor debe seleccionarse y aplicarse a un héroe específico

### El scroll no funciona
- Verificar que usas ↑↓ para navegar
- Algunas pantallas requieren más de 6 elementos para mostrar scroll

---

## 💡 CONSEJOS

### Para Desarrolladores
- El código está comentado y bien estructurado
- Cada pantalla es independiente y modular
- Las bases de datos JSON son fáciles de modificar
- El sistema de scroll es reutilizable

### Para Jugadores
- Experimenta con diferentes combinaciones de habilidades
- Los expansores de ranuras son valiosos - úsalos sabiamente
- Las habilidades DOT/HOT son muy útiles en batallas largas
- Guarda frecuentemente (el sistema funciona bien)

---

## 📞 SOPORTE

Si encuentras bugs o tienes sugerencias:
1. Anota los pasos para reproducir el error
2. Captura de pantalla si es posible
3. Verifica la versión de Python y Pygame

---

**Última actualización:** 2025-11-15
**Versión:** Fase 7 - v0.9 (Beta)
**Estado:** Estable - Listo para pruebas
