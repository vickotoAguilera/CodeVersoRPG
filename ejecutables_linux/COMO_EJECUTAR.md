# 🖱️ Cómo Ejecutar Scripts en Linux

## ❌ Problema: Doble Click No Funciona

En Linux, los archivos `.sh` no se ejecutan automáticamente con doble click como los `.bat` en Windows.

## ✅ Soluciones

### **Opción 1: Usar Terminal (Recomendado)**

Abre una terminal en la carpeta del proyecto y ejecuta:

```bash
cd ~/Documentos/CodeVersoRPG-main
./ejecutables_linux/git_status.sh
```

O directamente:
```bash
bash ~/Documentos/CodeVersoRPG-main/ejecutables_linux/git_status.sh
```

### **Opción 2: Crear Lanzadores .desktop (Doble Click)**

He creado archivos `.desktop` en la carpeta `lanzadores_linux/` que SÍ se pueden ejecutar con doble click.

**Pasos:**
1. Ve a la carpeta `lanzadores_linux/`
2. Haz doble click en cualquier archivo `.desktop`
3. Si te pregunta, selecciona **"Ejecutar"** o **"Confiar y ejecutar"**

### **Opción 3: Configurar Nautilus/Nemo (Gestor de Archivos)**

Para que los `.sh` se ejecuten con doble click:

1. Abre el gestor de archivos (Nemo/Nautilus)
2. Ve a **Editar** → **Preferencias**
3. Busca la pestaña **"Comportamiento"**
4. En **"Archivos de texto ejecutables"** selecciona:
   - **"Preguntar cada vez"** o
   - **"Ejecutar archivos de texto ejecutables al abrirlos"**

### **Opción 4: Desde el Menú Contextual**

1. Click derecho en el archivo `.sh`
2. Selecciona **"Ejecutar como programa"** o **"Abrir en terminal"**

---

## 🎯 Recomendación

**Usa los archivos `.desktop` de la carpeta `lanzadores_linux/`** - funcionan exactamente como los `.bat` en Windows (doble click y listo).

---

## 📁 Estructura de Carpetas

```
CodeVersoRPG-main/
├── ejecutables_linux/     ← Scripts .sh (para terminal)
└── lanzadores_linux/      ← Lanzadores .desktop (para doble click)
```

**Usa `lanzadores_linux/` para doble click en Linux** (equivalente a los `.bat` en Windows)
