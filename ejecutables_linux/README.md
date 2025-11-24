# 🐧 Scripts de Git para Linux

Esta carpeta contiene scripts equivalentes a los archivos `.bat` de Windows, pero para Linux.

## 📋 Scripts Disponibles

### Git Básico
- **`git_status.sh`** - Ver estado del repositorio
- **`git_pull.sh`** - Descargar cambios desde GitHub
- **`git_push.sh`** - Subir cambios a GitHub
- **`git_push_rapido.sh`** - Push rápido con mensaje automático
- **`git_push_completo.sh`** - Push con organización de documentación
- **`git_push_total.sh`** - Push total con merge de ramas

### Configuración
- **`conectar_github.sh`** - Conectar con repositorio de GitHub
- **`verificar_git.sh`** - Verificar configuración de Git

### Editores
- **`ejecutar_editor_unificado.sh`** - Editor unificado
- **`ejecutar_editor_batalla.sh`** - Editor de batallas
- **`ejecutar_editor_muros.sh`** - Editor de muros
- **`ejecutar_editor_avanzado.sh`** - Editor de mapas avanzado
- **`ejecutar_sprite_editor.sh`** - Editor de sprites

## 🚀 Cómo Usar

### Primera vez (dar permisos de ejecución):
```bash
chmod +x ejecutables_linux/*.sh
```

### Ejecutar un script:
```bash
./ejecutables_linux/git_status.sh
```

O desde la raíz del proyecto:
```bash
bash ejecutables_linux/git_push.sh
```

## 💡 Diferencias con Windows

| Windows | Linux |
|---------|-------|
| `.bat` | `.sh` |
| Doble click | `./script.sh` o `bash script.sh` |
| `@echo off` | `#!/bin/bash` |
| `pause` | `read -p "Presiona Enter..."` |

## ⚠️ Nota Importante

Estos scripts son equivalentes a los `.bat` de Windows. Si trabajas en ambos sistemas:
- En **Windows**: usa los archivos `.bat`
- En **Linux**: usa los archivos `.sh` de esta carpeta

Ambos hacen exactamente lo mismo, solo cambia la sintaxis.
