# 🖱️ Lanzadores para Linux (Doble Click)

Esta carpeta contiene **lanzadores .desktop** que funcionan con **doble click** en Linux, igual que los archivos `.bat` en Windows.

## 🎯 Cómo Usar

### **Método Simple (Doble Click):**
1. Abre esta carpeta en tu gestor de archivos
2. Haz **doble click** en cualquier archivo `.desktop`
3. Si te pregunta, selecciona **"Ejecutar"** o **"Confiar y ejecutar"**

¡Eso es todo! Se abrirá una terminal y ejecutará el programa.

---

## 📋 Lanzadores Disponibles

### Git (5 lanzadores)
- **Git_Status.desktop** - Ver estado del repositorio
- **Git_Pull.desktop** - Descargar desde GitHub
- **Git_Push.desktop** - Subir a GitHub (pide mensaje)
- **Git_Push_Rapido.desktop** - Push rápido (mensaje automático) ⭐ **Recomendado**
- **Git_Push_Total.desktop** - Push total con merge

### Editores (7 lanzadores)
- **Editor_Unificado.desktop** - Editor unificado
- **Editor_Batallas.desktop** - Editor de batallas
- **Editor_Muros.desktop** - Editor de muros
- **Editor_Mapas_Avanzado.desktop** - Editor de mapas avanzado
- **Editor_Portales.desktop** - Editor de portales
- **Editor_Cofres.desktop** - Editor de cofres
- **Sprite_Editor.desktop** - Editor de sprites

### Juego (1 lanzador)
- **Jugar.desktop** - Iniciar el juego

---

## 💡 Equivalencia con Windows

| Windows (PC de casa) | Linux (este PC) |
|---------------------|-----------------|
| Doble click en `git_push_rapido.bat` | Doble click en `Git_Push_Rapido.desktop` |
| Doble click en `ejecutar_editor_unificado.bat` | Doble click en `Editor_Unificado.desktop` |
| Doble click en `main.py` | Doble click en `Jugar.desktop` |

**Funcionan exactamente igual**, solo cambia el tipo de archivo.

---

## ⚙️ Si No Funciona el Doble Click

### Primera vez:
Cuando hagas doble click por primera vez, puede que te pregunte:
- **"¿Confiar en este lanzador?"** → Click en **"Confiar y ejecutar"**
- **"¿Ejecutar o editar?"** → Selecciona **"Ejecutar"**

### Si sigue sin funcionar:
1. Click derecho en el archivo `.desktop`
2. Selecciona **"Permitir ejecutar"** o **"Propiedades"**
3. Marca la casilla **"Permitir ejecutar como programa"**
4. Intenta doble click de nuevo

---

## 🎨 Personalizar Iconos

Los lanzadores usan iconos del sistema. Si quieres cambiarlos:
1. Click derecho → **"Propiedades"**
2. Click en el icono
3. Selecciona un nuevo icono

---

## ✅ Ventajas de los .desktop

- ✅ Doble click funciona (como .bat en Windows)
- ✅ Se pueden agregar al escritorio
- ✅ Se pueden agregar al menú de aplicaciones
- ✅ Tienen iconos bonitos
- ✅ Funcionan en todos los gestores de archivos de Linux

---

## 🚀 Uso Recomendado

**Para uso diario:**
- **Git_Push_Rapido.desktop** - Para subir cambios rápido
- **Git_Pull.desktop** - Para descargar cambios
- **Jugar.desktop** - Para probar el juego
- **Editor_Unificado.desktop** - Para editar el juego

**Arrastra estos 4 al escritorio** para tenerlos siempre a mano.

---

## 📁 Estructura del Proyecto

```
CodeVersoRPG-main/
├── ejecutables_linux/     ← Scripts .sh (para terminal)
└── lanzadores_linux/      ← Lanzadores .desktop (para doble click) ⭐ USA ESTOS
```

**Usa esta carpeta (`lanzadores_linux/`) para trabajar con doble click**, igual que en Windows.
