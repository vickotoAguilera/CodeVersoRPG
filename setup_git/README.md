# 🚀 Configuración Automática de Git

Esta carpeta contiene un script para configurar automáticamente Git en cualquier PC.

## 📋 Contenido

- **CONFIGURAR_GIT.bat** - Script de configuración automática

## 🎯 ¿Para qué sirve?

Este script te permite configurar Git en cualquier PC de forma rápida y automática. Es útil cuando:

- Clonas el proyecto en una nueva computadora
- Trabajas en múltiples PCs
- Necesitas configurar Git desde cero
- Quieres automatizar la configuración inicial

## 🔧 ¿Qué hace el script?

1. ✅ Verifica que Git esté instalado
2. ✅ Inicializa el repositorio Git (si no existe)
3. ✅ Configura tu usuario y email de GitHub
4. ✅ Conecta con el repositorio remoto
5. ✅ Configura la rama principal (main)
6. ✅ Sincroniza con GitHub (opcional)

## 📖 Cómo usar

### Opción 1: En este PC
1. Haz doble clic en `CONFIGURAR_GIT.bat`
2. Sigue las instrucciones en pantalla
3. Ingresa tu nombre de usuario y email de GitHub
4. ¡Listo!

### Opción 2: En otro PC
1. Copia toda la carpeta `setup_git` a la raíz del proyecto en el otro PC
2. Ejecuta `CONFIGURAR_GIT.bat`
3. Sigue las instrucciones

### Opción 3: Proyecto nuevo
1. Descarga el proyecto desde GitHub
2. Copia la carpeta `setup_git` a la raíz del proyecto
3. Ejecuta `CONFIGURAR_GIT.bat`

## ⚠️ Requisitos

- **Git** debe estar instalado en el PC
  - Descarga desde: https://git-scm.com/download/win
  - Durante la instalación, acepta las opciones por defecto

## 💡 Notas Importantes

- El script pedirá confirmación antes de sincronizar con GitHub
- Si hay conflictos, el script te avisará para que los resuelvas manualmente
- Tus credenciales de Git se guardarán solo en este proyecto
- El script detecta si Git ya está configurado y no sobrescribe la configuración

## 🔐 Seguridad

- El script NO guarda tu contraseña de GitHub
- Solo configura tu nombre de usuario y email
- Para hacer push, GitHub te pedirá autenticación la primera vez

## 📞 Soporte

Si tienes problemas:
1. Verifica que Git esté instalado: `git --version`
2. Asegúrate de estar en la carpeta correcta del proyecto
3. Revisa que tengas conexión a Internet para sincronizar con GitHub

---

**Repositorio:** https://github.com/vickotoAguilera/CodeVersoRPG.git
