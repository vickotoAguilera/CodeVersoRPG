from __future__ import annotations

from typing import Dict, List


def opciones_panel_por_modo(modo_npc: str) -> List[str]:
    modo = str(modo_npc or "npc").lower()
    if modo == "venta":
        return ["Comprar", "Vender", "Hablar", "Salir"]
    if modo == "herrero":
        return ["Mejorar", "Forjar", "Hablar", "Salir"]
    return ["Hablar", "Salir"]


def ejecutar_accion_panel(modo_npc: str, accion: str, npc_id: int) -> Dict[str, object]:
    """Hook base para comercio/herrero. La logica completa se implementa despues."""
    modo = str(modo_npc or "npc").lower()
    a = str(accion or "").lower()

    if modo == "venta":
        if a == "comprar":
            return {"ok": True, "abrir_submenu": "comprar", "mensaje": f"NPC {npc_id}: submenu Comprar (pendiente)."}
        if a == "vender":
            return {"ok": True, "abrir_submenu": "vender", "mensaje": f"NPC {npc_id}: submenu Vender (pendiente)."}
        if a == "hablar":
            return {"ok": True, "reabrir_dialogo": True, "mensaje": f"NPC {npc_id}: volver a dialogo."}
        return {"ok": True, "cerrar_panel": True, "mensaje": "Panel cerrado."}

    if modo == "herrero":
        if a in ("mejorar", "forjar"):
            return {"ok": True, "abrir_submenu": a, "mensaje": f"NPC {npc_id}: submenu {a.title()} (pendiente)."}
        if a == "hablar":
            return {"ok": True, "reabrir_dialogo": True, "mensaje": f"NPC {npc_id}: volver a dialogo."}
        return {"ok": True, "cerrar_panel": True, "mensaje": "Panel cerrado."}

    if a == "hablar":
        return {"ok": True, "reabrir_dialogo": True, "mensaje": f"NPC {npc_id}: volver a dialogo."}
    return {"ok": True, "cerrar_panel": True, "mensaje": "Panel cerrado."}
