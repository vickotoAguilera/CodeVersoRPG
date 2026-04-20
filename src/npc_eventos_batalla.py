from __future__ import annotations

from typing import Dict


def resolver_evento_npc(modo_npc: str, npc_id: int) -> Dict[str, object]:
    """Hook base de eventos. La pelea contra NPC se conecta despues."""
    modo = str(modo_npc or "npc").lower()
    if modo != "evento":
        return {"ok": False, "mensaje": "Sin evento especial."}

    return {
        "ok": True,
        "disparar_evento": "batalla_npc",
        "npc_id": npc_id,
        "mensaje": f"NPC {npc_id}: evento de batalla listo para integrar.",
        "posicion_dialogo_batalla": "arriba",
    }
