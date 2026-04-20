# Guía de Inicio Rápido - Code Verso RPG

## 🎯 Inicio en 3 Pasos

### Paso 1: Crear Estructura (5 minutos)

```bash
# Ejecutar script de setup
python setup_structure.py

# Reemplazar archivo de configuración
# Windows:
del settings.json
ren settings_nuevo.json settings.json

# Linux/Mac:
# rm settings.json
# mv settings_nuevo.json settings.json
```

### Paso 2: Instalar Dependencias (2 minutos)

```bash
pip install -r requirements.txt
```

### Paso 3: Probar Juego Actual (1 minuto)

```bash
python main.py
```

El juego funcional actual debería iniciar correctamente.

---

## 📚 Documentación Disponible

### Para Desarrolladores

1. **ARQUITECTURA.md** (12 KB)
   - Estructura completa del sistema
   - Patrones de diseño
   - Flujo de datos
   - **Tiempo de lectura:** 20-30 minutos

2. **REFACTORIZACION.md** (17 KB)
   - Plan paso a paso de refactorización
   - Código de ejemplo
   - Checklist completa
   - **Tiempo de lectura:** 30-40 minutos

### Para Diseñadores de Contenido

1. **DATABASE.md** (18 KB)
   - Documentación de todos los JSON
   - Cómo agregar contenido
   - Relaciones entre datos
   - **Tiempo de lectura:** 25-35 minutos

### Para Todos

1. **README.md** (8 KB)
   - Instalación y configuración
   - Controles del juego
   - Solución de problemas
   - **Tiempo de lectura:** 15-20 minutos

2. **RESUMEN_CAMBIOS.md** (13 KB)
   - Qué se ha hecho
   - Qué falta por hacer
   - Beneficios de los cambios
   - **Tiempo de lectura:** 15-20 minutos

---

## 🔧 Errores Corregidos

### Error 1: RUTA_ITEMS_DB no definida ✅

**Archivo:** `main.py` línea 30  
**Estado:** Corregido

### Error 2: self.magias no inicializada ✅

**Archivo:** `src/heroe.py` línea 35  
**Estado:** Corregido

---

## 📋 Orden de Lectura Recomendado

### Si eres desarrollador:

1. **README.md** - Entender el proyecto
2. **RESUMEN_CAMBIOS.md** - Ver qué se ha hecho
3. **ARQUITECTURA.md** - Entender la arquitectura
4. **REFACTORIZACION.md** - Plan de trabajo
5. **DATABASE.md** - Estructura de datos

**Tiempo total:** ~2 horas

### Si eres diseñador de contenido:

1. **README.md** - Configuración básica
2. **DATABASE.md** - Cómo trabajar con datos
3. **RESUMEN_CAMBIOS.md** - Contexto general

**Tiempo total:** ~1 hora

### Si solo quieres jugar:

1. **README.md** - Sección "Instalación" y "Controles"

**Tiempo total:** 5 minutos

---

## 🚀 Comenzar Refactorización

### Opción A: Desarrollo Completo (55-71 horas)

Seguir todas las fases en **REFACTORIZACION.md**:

1. Core del motor (8-10h)
2. Entidades (4-6h)
3. Sistemas (8-10h)
4. Estados (10-12h)
5. UI (8-10h)
6. Validación (4-6h)
7. Testing (10-12h)
8. Migración final (2-4h)

### Opción B: Desarrollo Incremental (Por módulos)

Puedes refactorizar módulo por módulo:

**Semana 1:** Core
- Implementar logging
- Implementar resource manager
- Mantener código antiguo funcionando

**Semana 2:** Entidades
- Refactorizar Heroe
- Refactorizar Monstruo
- Crear Grupo

**Semana 3:** Sistemas
- Sistema de batalla
- Sistema de guardado
- etc.

### Opción C: Solo Mejoras Críticas (10-15 horas)

Si no tienes mucho tiempo, prioriza:

1. **Implementar logging** (2h)
   - Sistema de logs robusto
   - Facilita debugging

2. **Centralizar constantes** (2h)
   - Usar constants.py
   - Eliminar números mágicos

3. **Validar datos JSON** (3h)
   - Evitar crashes por datos incorrectos
   - Mensajes de error claros

4. **Limpiar chilenismos** (3h)
   - Español neutro profesional
   - Mejora legibilidad

5. **Agregar docstrings** (2h)
   - Documentar funciones clave
   - Facilita mantenimiento

---

## 🛠️ Herramientas Útiles

### Editor Recomendado

**Visual Studio Code** con extensiones:
- Python
- Pylance (Type hints)
- GitLens (Control de versiones)
- Better Comments (Resaltar comentarios)

### Testing

```bash
# Ejecutar todos los tests
python -m pytest tests/

# Con cobertura
python -m pytest --cov=src tests/

# Un test específico
python -m pytest tests/test_heroe.py
```

### Linting (Opcional)

```bash
# Instalar
pip install pylint black

# Usar
pylint src/
black src/
```

---

## 📁 Estructura de Archivos

```
RPG/
├── 📄 main.py                      # Juego actual (funcional)
├── 📄 setup_structure.py           # Script de configuración
├── 📄 requirements.txt             # Dependencias
├── 📄 settings.json                # Configuración del juego
│
├── 📚 Documentación/
│   ├── INICIO_RAPIDO.md           # Este archivo
│   ├── README.md                  # Guía principal
│   ├── ARQUITECTURA.md            # Diseño del sistema
│   ├── DATABASE.md                # Estructura de datos
│   ├── REFACTORIZACION.md         # Plan de trabajo
│   └── RESUMEN_CAMBIOS.md         # Qué se ha hecho
│
├── 🔧 src/
│   ├── constants.py               # Constantes centralizadas
│   ├── config.py                  # Configuración de rutas
│   │
│   ├── core/                      # (A crear)
│   ├── states/                    # (A crear)
│   ├── entities/                  # (A crear)
│   ├── systems/                   # (A crear)
│   ├── ui/                        # (A crear)
│   ├── world/                     # (A crear)
│   ├── data/                      # (A crear)
│   └── utils/                     # (A crear)
│
├── 💾 database/                    # Datos del juego (JSON)
├── 🖼️ assets/                      # Recursos gráficos
├── 💿 saves/                       # Partidas guardadas
├── 📊 logs/                        # Archivos de log
└── 🧪 tests/                       # Tests unitarios (A crear)
```

---

## ⚠️ Problemas Comunes

### Error: "No module named 'pygame'"

```bash
pip install pygame
```

### Error: "No se puede crear directorio"

Ejecutar como administrador o verificar permisos.

### Error: "Archivo JSON malformado"

Verificar sintaxis JSON en:
- https://jsonlint.com/

### El juego va lento

Editar `settings.json`:
```json
{
    "video": {
        "vsync": false,
        "fps": 30
    }
}
```

---

## 📞 Ayuda y Soporte

### Documentación

1. Lee **README.md** para problemas generales
2. Lee **DATABASE.md** para problemas con datos
3. Lee **ARQUITECTURA.md** para entender el código

### Logs

Los logs están en `logs/game_YYYY-MM-DD.log`

Contienen información detallada de errores.

### Debug Mode

En `settings.json`:
```json
{
    "avanzado": {
        "modo_debug": true,
        "mostrar_hitboxes": true
    }
}
```

---

## ✅ Checklist Rápido

### Antes de Empezar

- [ ] Python 3.8+ instalado
- [ ] Pip actualizado
- [ ] Editor de código instalado
- [ ] Git instalado (opcional pero recomendado)

### Configuración Inicial

- [ ] Ejecutado `setup_structure.py`
- [ ] Reemplazado `settings.json`
- [ ] Instaladas dependencias con `pip install -r requirements.txt`
- [ ] Probado juego actual con `python main.py`

### Documentación Leída

- [ ] README.md
- [ ] RESUMEN_CAMBIOS.md
- [ ] Este archivo (INICIO_RAPIDO.md)
- [ ] ARQUITECTURA.md (si eres dev)
- [ ] DATABASE.md (si trabajarás con datos)
- [ ] REFACTORIZACION.md (si harás refactorización)

### Listo para Trabajar

- [ ] Entiendo la estructura del proyecto
- [ ] Sé qué archivos modificar
- [ ] Tengo las herramientas necesarias
- [ ] He leído la documentación relevante

---

## 🎮 Jugar Ahora

Si solo quieres probar el juego:

```bash
python main.py
```

**Controles:**
- Flechas: Movimiento / Menús
- Enter: Confirmar / Interactuar
- ESC: Menú de pausa / Volver
- D: Detalles (en equipo/items)

**Características:**
- Explora el mapa
- Combate por turnos
- Sistema de inventario
- Equipamiento de armas/armaduras
- Habilidades y magia
- Guardar/Cargar partidas
- Autoguardado cada 10 minutos

---

## 📈 Progreso del Proyecto

### Fase Actual: Preparación ✅ 100%

- ✅ Errores críticos corregidos
- ✅ Documentación completa
- ✅ Configuración centralizada
- ✅ Plan de refactorización
- ✅ Scripts de ayuda

### Próxima Fase: Core 🔄 0%

- ⏳ Implementar logging
- ⏳ Implementar resource manager
- ⏳ Implementar input manager
- ⏳ Implementar state machine
- ⏳ Implementar game engine

**Tiempo estimado:** 8-10 horas

---

## 🎯 Objetivos del Proyecto

### A Corto Plazo (1-2 semanas)

- Completar core del motor
- Refactorizar entidades principales
- Implementar sistema de logging

### A Mediano Plazo (1 mes)

- Completar refactorización
- Agregar tests unitarios
- Validación de datos completa

### A Largo Plazo (2-3 meses)

- Sistema de misiones
- NPCs y diálogos
- Más mapas y contenido
- Sistema de audio
- Mejoras visuales

---

## 💡 Tips

### Para Desarrollo

1. **Commits frecuentes** - Guarda cambios constantemente
2. **Tests primero** - Escribe tests antes de refactorizar
3. **Una cosa a la vez** - No cambies múltiples sistemas simultáneamente
4. **Lee los logs** - El sistema de logging es tu amigo

### Para Diseño de Contenido

1. **Valida JSON** - Usa jsonlint.com antes de guardar
2. **Nombres consistentes** - Usa convención de nombrado clara
3. **Documenta cambios** - Anota qué agregaste/modificaste
4. **Prueba en juego** - Siempre verifica que funcione

### Para Testing

1. **Guarda a menudo** - Usa el sistema de guardado
2. **Reporta bugs** - Anota errores con pasos para reproducir
3. **Prueba límites** - Intenta romper el juego
4. **Revisa logs** - Ayudan a identificar problemas

---

## 🚀 ¡Empezar Ya!

```bash
# 1. Setup
python setup_structure.py

# 2. Configurar
del settings.json && ren settings_nuevo.json settings.json

# 3. Instalar
pip install -r requirements.txt

# 4. Jugar
python main.py

# 5. Desarrollar
# Lee REFACTORIZACION.md y comienza con el core
```

---

**¡Éxito con tu proyecto RPG!** 🎮✨

