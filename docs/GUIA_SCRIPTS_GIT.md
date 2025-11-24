# 🚀 Guía de Scripts Git

**Fecha:** 16 Noviembre 2025

---

## 📁 Scripts Disponibles

### 1. `git_push.bat` - Push Completo (Recomendado)

**Uso:** Doble click en el archivo

**Lo que hace:**
1. ✅ Organiza documentación (`organizar_docs.py`)
2. ✅ Muestra archivos modificados
3. ✅ Agrega todos los cambios
4. ✅ Te pide un mensaje de commit
5. ✅ Hace commit con tu mensaje
6. ✅ Sube a GitHub

**Cuándo usarlo:**
- ✅ Al final de cada sesión de trabajo
- ✅ Cuando quieras control sobre el mensaje de commit
- ✅ Para commits importantes y descriptivos

**Ejemplo de uso:**
```
Doble click en git_push.bat
→ Te pregunta: "Escribe el mensaje del commit"
→ Escribes: feat: Implementar sistema de buffs
→ Enter y listo!
```

---

### 2. `git_push_rapido.bat` - Push Automático Rápido

**Uso:** Doble click en el archivo

**Lo que hace:**
1. ✅ Organiza documentación
2. ✅ Agrega cambios
3. ✅ Commit automático con fecha/hora
4. ✅ Push a GitHub

**Mensaje automático:**
```
update: Cambios del 16/11/2025 14:30
```

**Cuándo usarlo:**
- ✅ Guardados rápidos mientras trabajas
- ✅ Cuando no importa el mensaje específico
- ✅ Para backups frecuentes

---

### 3. `git_status.bat` - Ver Estado

**Uso:** Doble click en el archivo

**Lo que muestra:**
- 📋 Archivos modificados
- 📋 Últimos 5 commits
- 📋 Configuración de usuario
- 📋 URL del repositorio remoto

**Cuándo usarlo:**
- ✅ Para ver qué cambió
- ✅ Verificar configuración
- ✅ Ver historial reciente

---

### 4. `git_pull.bat` - Actualizar desde GitHub

**Uso:** Doble click en el archivo

**Lo que hace:**
- ⬇️ Descarga cambios desde GitHub
- ⬇️ Actualiza tu copia local

**Cuándo usarlo:**
- ✅ Si trabajas en múltiples computadoras
- ✅ Antes de empezar a trabajar
- ✅ Para sincronizar con GitHub

---

## 🎯 Workflow Recomendado

### Opción A: Trabajo Normal (Más Control)

```
1. Trabajar en el código
2. Probar que funcione
3. Doble click: git_push.bat
4. Escribir mensaje descriptivo
5. ¡Listo!
```

### Opción B: Guardados Frecuentes (Rápido)

```
1. Trabajar en el código
2. Doble click: git_push_rapido.bat cada 30 min
3. Al final del día: git_push.bat con mensaje descriptivo
```

### Opción C: Múltiples Computadoras

```
Computadora A:
1. git_pull.bat (actualizar)
2. Trabajar
3. git_push.bat (subir)

Computadora B:
1. git_pull.bat (descargar cambios de A)
2. Trabajar
3. git_push.bat (subir)
```

---

## 💬 Mensajes de Commit Recomendados

### Con `git_push.bat` escribe mensajes como:

**Nuevas funcionalidades:**
```
feat: Implementar sistema de buffs/debuffs
feat: Agregar 5 nuevas habilidades
feat: Crear sistema de tiendas
```

**Correcciones:**
```
fix: Corregir error en sistema de batalla
fix: Solucionar items invisibles
fix: Arreglar carga de partidas
```

**Documentación:**
```
docs: Actualizar guía de habilidades
docs: Crear documentación de sistema DOT
docs: Agregar ejemplos de uso
```

**Mejoras:**
```
refactor: Optimizar sistema de scroll
refactor: Limpiar código de batalla
style: Formatear archivos
```

**Múltiples cambios:**
```
update: Sistema DOT completo + documentación
update: Correcciones varias y mejoras UI
update: Fin de sesión 16/11/2025
```

---

## 🔧 Personalización

### Cambiar el Mensaje Automático

Edita `git_push_rapido.bat`, línea 11:

```batch
REM Original:
set mensaje=update: Cambios del %date% %time:~0,5%

REM Personalizado:
set mensaje=work: Progreso del día
```

### Cambiar la Rama

Si usas otra rama que no sea `main`, edita los archivos:

```batch
REM Buscar esta línea:
git push origin main

REM Cambiar a:
git push origin tu-rama
```

### Agregar Comandos Adicionales

Puedes agregar más comandos antes del push:

```batch
REM Ejemplo: Ejecutar tests antes de subir
echo Ejecutando tests...
python -m pytest
if %errorlevel% neq 0 (
    echo Tests fallaron. No se subirán cambios.
    pause
    exit /b 1
)
```

---

## ⚠️ Solución de Problemas

### Error: "git no se reconoce como comando"

**Problema:** Git no está en el PATH de Windows

**Solución:**
1. Instalar Git desde: https://git-scm.com/
2. O agregar Git al PATH manualmente

---

### Error: "Permission denied"

**Problema:** Credenciales incorrectas

**Solución:**
1. Verificar token en: https://github.com/settings/tokens
2. Actualizar remote:
```bash
git remote set-url origin https://vickotoAguilera:TU_TOKEN@github.com/vickotoAguilera/CodeVersoRPG.git
```

---

### Error: "nothing to commit"

**Problema:** No hay cambios para subir

**Solución:** Normal, significa que ya todo está actualizado en GitHub

---

### Script se Cierra Muy Rápido

**Problema:** No puedes ver los mensajes

**Solución:** Ya tienen `pause` al final, pero si se cierra, ejecuta desde CMD:
1. Abrir CMD en la carpeta
2. Escribir: `git_push.bat`

---

## 📊 Atajos de Teclado (Opcional)

Puedes crear accesos directos con atajos:

1. Click derecho en `git_push.bat` → "Crear acceso directo"
2. Click derecho en el acceso directo → "Propiedades"
3. En "Tecla de acceso directo" presiona: `Ctrl + Alt + G`
4. Ahora puedes presionar `Ctrl + Alt + G` desde cualquier lado

---

## 🎓 Comandos Equivalentes

Si prefieres la terminal, estos son los comandos equivalentes:

### git_push.bat
```bash
python organizar_docs.py
git status
git add .
git commit -m "tu mensaje"
git push origin main
```

### git_push_rapido.bat
```bash
python organizar_docs.py
git add .
git commit -m "update: $(date)"
git push origin main
```

### git_status.bat
```bash
git status
git log --oneline -5
git config user.name
git remote get-url origin
```

### git_pull.bat
```bash
git pull origin main
```

---

## 📚 Recursos Adicionales

- **Guía completa de Git:** `docs/GUIA_GITHUB.md`
- **Organización de archivos:** `docs/ORGANIZACION_PROYECTO.md`
- **Documentación oficial:** https://git-scm.com/doc

---

## 🎯 Checklist Diario

Al finalizar tu sesión de trabajo:

- [ ] El código funciona correctamente
- [ ] Ejecutar: `git_push.bat`
- [ ] Escribir mensaje descriptivo
- [ ] Verificar en GitHub que se subió
- [ ] Opcional: Revisar en https://github.com/vickotoAguilera/CodeVersoRPG

---

## 💡 Tips

**Tip 1:** Usa `git_push_rapido.bat` cada 30-60 minutos como "guardado automático"

**Tip 2:** Al final del día, usa `git_push.bat` con un mensaje resumen

**Tip 3:** Ejecuta `git_status.bat` para ver qué cambió antes de subir

**Tip 4:** Si trabajas en otra PC, ejecuta `git_pull.bat` primero

**Tip 5:** Los archivos `.bat` son seguros de compartir (no tienen tu token)

---

**Última actualización:** 16 Nov 2025 - 15:15 UTC
