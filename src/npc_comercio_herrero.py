from __future__ import annotations

from typing import Dict, List


PRECIOS_COMPRA_CONSUMIBLES = {
    "POCION_BASICA": 40,
    "ETER_BASICO": 55,
    "POCION_INTERMEDIA": 90,
    "ETER_INTERMEDIO": 105,
    "ANTIDOTO": 35,
    "POCION_GRANDE": 180,
    "ETER_GRANDE": 210,
    "ELIXIR": 420,
}

RECETAS_FORJA = [
    {
        "id": "forja_mandoble_hierro",
        "resultado": "MANDOBLE_HIERRO",
        "materiales": {"ESPADA_COBRE": 1, "ESCUDO_MADERA": 1},
        "costo_oro": 180,
    },
    {
        "id": "forja_collar_salud",
        "resultado": "COLLAR_SALUD",
        "materiales": {"POCION_INTERMEDIA": 2, "ETER_INTERMEDIO": 1},
        "costo_oro": 140,
    },
    {
        "id": "forja_anillo_agilidad",
        "resultado": "ANILLO_AGILIDAD",
        "materiales": {"ETER_BASICO": 2, "ANTIDOTO": 1},
        "costo_oro": 120,
    },
]


def opciones_panel_por_modo(modo_npc: str) -> List[str]:
    modo = str(modo_npc or "npc").lower()
    if modo == "venta":
        return ["Comprar", "Vender", "Hablar", "Salir"]
    if modo == "herrero":
        return ["Mejorar", "Forjar", "Hablar", "Salir"]
    return ["Hablar", "Salir"]


def _precio_compra_item(id_item: str, items_db: Dict[str, dict]) -> int:
    if id_item in PRECIOS_COMPRA_CONSUMIBLES:
        return int(PRECIOS_COMPRA_CONSUMIBLES[id_item])
    data = items_db.get(id_item, {})
    poder = int(data.get("poder", 0) or 0)
    return max(30, poder * 2)


def _precio_venta_item(id_item: str, items_db: Dict[str, dict], equipo_db: Dict[str, dict]) -> int:
    if id_item in items_db:
        return max(1, _precio_compra_item(id_item, items_db) // 2)

    eq = equipo_db.get(id_item, {})
    stats = eq.get("stats", {})
    puntaje = (
        int(stats.get("fuerza", 0))
        + int(stats.get("defensa", 0))
        + int(stats.get("inteligencia", 0))
        + int(stats.get("espiritu", 0))
        + int(stats.get("velocidad", 0))
        + int(stats.get("suerte", 0))
        + max(0, int(stats.get("hp_max", 0)) // 5)
        + max(0, int(stats.get("mp_max", 0)) // 5)
    )
    return max(20, puntaje * 12)


def _costo_mejora_equipo(item_data: Dict[str, object]) -> int:
    nivel = int(item_data.get("nivel_mejora", 0) or 0)
    return 120 + (nivel * 70)


def _stat_principal_equipo(item_data: Dict[str, object]) -> str:
    stats = item_data.get("stats", {}) or {}
    candidatos = ["fuerza", "defensa", "inteligencia", "espiritu", "velocidad", "suerte"]
    mejor = "fuerza"
    mejor_valor = -999
    for nombre in candidatos:
        valor = int(stats.get(nombre, 0) or 0)
        if valor > mejor_valor:
            mejor_valor = valor
            mejor = nombre
    return mejor


def _formatear_materiales(materiales: Dict[str, int], items_db: Dict[str, dict], equipo_db: Dict[str, dict]) -> str:
    partes = []
    for id_item, cantidad in materiales.items():
        nombre = items_db.get(id_item, {}).get("nombre") or equipo_db.get(id_item, {}).get("nombre") or id_item
        partes.append(f"{nombre} x{cantidad}")
    return ", ".join(partes)


def construir_submenu(
    modo_npc: str,
    accion: str,
    heroe,
    items_db: Dict[str, dict],
    equipo_db: Dict[str, dict],
) -> Dict[str, object]:
    """Genera opciones del submenu solicitado para vendedor/herrero."""
    modo = str(modo_npc or "npc").lower()
    a = str(accion or "").lower()

    if modo == "venta" and a == "comprar":
        stock = [
            "POCION_BASICA",
            "ETER_BASICO",
            "POCION_INTERMEDIA",
            "ETER_INTERMEDIO",
            "ANTIDOTO",
            "POCION_GRANDE",
            "ETER_GRANDE",
            "ELIXIR",
        ]
        opciones = []
        for id_item in stock:
            if id_item not in items_db:
                continue
            nombre = items_db[id_item].get("nombre", id_item)
            precio = _precio_compra_item(id_item, items_db)
            opciones.append(
                {
                    "accion": "comprar_item",
                    "id_item": id_item,
                    "precio": precio,
                    "texto": f"{nombre} - {precio}G",
                }
            )

        opciones.append({"accion": "volver", "texto": "Volver"})
        return {
            "ok": True,
            "submenu": "comprar",
            "titulo": "Tienda - Comprar",
            "opciones": opciones,
            "mensaje": "Selecciona item para comprar.",
        }

    if modo == "venta" and a == "vender":
        opciones = []
        for id_item, cantidad in sorted(heroe.inventario.items()):
            if cantidad <= 0:
                continue
            precio = _precio_venta_item(id_item, items_db, equipo_db)
            nombre = items_db.get(id_item, {}).get("nombre") or equipo_db.get(id_item, {}).get("nombre") or id_item
            opciones.append(
                {
                    "accion": "vender_item",
                    "id_item": id_item,
                    "precio": precio,
                    "texto": f"{nombre} x{cantidad} - {precio}G",
                }
            )

        if not opciones:
            opciones.append({"accion": "sin_items", "texto": "No tienes items para vender"})
        opciones.append({"accion": "volver", "texto": "Volver"})

        return {
            "ok": True,
            "submenu": "vender",
            "titulo": "Tienda - Vender",
            "opciones": opciones,
            "mensaje": "Selecciona item para vender.",
        }

    if modo == "herrero" and a == "mejorar":
        opciones = []
        ids_vistos = set()
        for _, id_equipo in heroe.equipo.items():
            if not id_equipo or id_equipo in ids_vistos:
                continue
            ids_vistos.add(id_equipo)
            data = equipo_db.get(id_equipo)
            if not data:
                continue
            costo = _costo_mejora_equipo(data)
            nivel = int(data.get("nivel_mejora", 0) or 0)
            nombre = data.get("nombre", id_equipo)
            opciones.append(
                {
                    "accion": "mejorar_equipo",
                    "id_equipo": id_equipo,
                    "costo": costo,
                    "texto": f"{nombre} Nv.{nivel} - Mejorar ({costo}G)",
                }
            )

        if not opciones:
            opciones.append({"accion": "sin_equipo", "texto": "No hay equipo equipado para mejorar"})
        opciones.append({"accion": "volver", "texto": "Volver"})

        return {
            "ok": True,
            "submenu": "mejorar",
            "titulo": "Herrero - Mejorar",
            "opciones": opciones,
            "mensaje": "Selecciona equipo para mejorar.",
        }

    if modo == "herrero" and a == "forjar":
        opciones = []
        for receta in RECETAS_FORJA:
            id_resultado = receta["resultado"]
            data_eq = equipo_db.get(id_resultado, {})
            nombre_resultado = data_eq.get("nombre", id_resultado)
            costo = int(receta.get("costo_oro", 0) or 0)
            materiales = receta.get("materiales", {})
            txt_mat = _formatear_materiales(materiales, items_db, equipo_db)
            opciones.append(
                {
                    "accion": "forjar_receta",
                    "id_receta": receta.get("id"),
                    "resultado": id_resultado,
                    "costo": costo,
                    "materiales": materiales,
                    "texto": f"{nombre_resultado} - {costo}G | {txt_mat}",
                }
            )

        if not opciones:
            opciones.append({"accion": "sin_recetas", "texto": "No hay recetas disponibles"})
        opciones.append({"accion": "volver", "texto": "Volver"})

        return {
            "ok": True,
            "submenu": "forjar",
            "titulo": "Herrero - Forjar",
            "opciones": opciones,
            "mensaje": "Selecciona una receta.",
        }

    return {"ok": False, "mensaje": "Submenu no disponible."}


def ejecutar_accion_panel(modo_npc: str, accion: str, npc_id: int) -> Dict[str, object]:
    """Resuelve acciones del panel principal NPC."""
    modo = str(modo_npc or "npc").lower()
    a = str(accion or "").lower()

    if modo == "venta":
        if a == "comprar":
            return {"ok": True, "abrir_submenu": "comprar", "mensaje": f"NPC {npc_id}: abre tienda."}
        if a == "vender":
            return {"ok": True, "abrir_submenu": "vender", "mensaje": f"NPC {npc_id}: revisa tu inventario."}
        if a == "hablar":
            return {"ok": True, "reabrir_dialogo": True, "mensaje": f"NPC {npc_id}: volver a dialogo."}
        return {"ok": True, "cerrar_panel": True, "mensaje": "Panel cerrado."}

    if modo == "herrero":
        if a in ("mejorar", "forjar"):
            return {"ok": True, "abrir_submenu": a, "mensaje": f"NPC {npc_id}: abre {a}."}
        if a == "hablar":
            return {"ok": True, "reabrir_dialogo": True, "mensaje": f"NPC {npc_id}: volver a dialogo."}
        return {"ok": True, "cerrar_panel": True, "mensaje": "Panel cerrado."}

    if a == "hablar":
        return {"ok": True, "reabrir_dialogo": True, "mensaje": f"NPC {npc_id}: volver a dialogo."}
    return {"ok": True, "cerrar_panel": True, "mensaje": "Panel cerrado."}


def ejecutar_accion_submenu(
    modo_npc: str,
    submenu_tipo: str,
    opcion: Dict[str, object],
    heroe,
    items_db: Dict[str, dict],
    equipo_db: Dict[str, dict],
) -> Dict[str, object]:
    """Aplica accion real de un submenu (comprar, vender, mejorar, forjar)."""
    accion = str(opcion.get("accion", "")).lower()
    modo = str(modo_npc or "npc").lower()
    submenu = str(submenu_tipo or "").lower()

    if accion in ("volver", "sin_items", "sin_equipo", "sin_recetas"):
        return {"ok": True, "cerrar_submenu": True, "mensaje": "Volviendo al menu principal."}

    if modo == "venta" and submenu == "comprar" and accion == "comprar_item":
        id_item = str(opcion.get("id_item", ""))
        precio = int(opcion.get("precio", 0) or 0)
        if precio <= 0 or not id_item:
            return {"ok": False, "mensaje": "Item invalido."}
        if heroe.oro < precio:
            return {"ok": False, "mensaje": f"No tienes oro suficiente ({heroe.oro}G)."}

        heroe.oro -= precio
        heroe.agregar_item(id_item, 1)
        nombre = items_db.get(id_item, {}).get("nombre", id_item)
        return {
            "ok": True,
            "mensaje": f"Compraste {nombre} por {precio}G. Oro restante: {heroe.oro}G.",
            "refrescar_submenu": True,
        }

    if modo == "venta" and submenu == "vender" and accion == "vender_item":
        id_item = str(opcion.get("id_item", ""))
        precio = int(opcion.get("precio", 0) or 0)
        if not id_item:
            return {"ok": False, "mensaje": "Item invalido."}
        if not heroe.tiene_item(id_item, 1):
            return {"ok": False, "mensaje": "Ya no tienes ese item."}

        heroe.usar_item(id_item, 1)
        heroe.oro += precio
        nombre = items_db.get(id_item, {}).get("nombre") or equipo_db.get(id_item, {}).get("nombre") or id_item
        return {
            "ok": True,
            "mensaje": f"Vendiste {nombre} por {precio}G. Oro actual: {heroe.oro}G.",
            "refrescar_submenu": True,
        }

    if modo == "herrero" and submenu == "mejorar" and accion == "mejorar_equipo":
        id_equipo = str(opcion.get("id_equipo", ""))
        item_data = equipo_db.get(id_equipo)
        if not item_data:
            return {"ok": False, "mensaje": "Equipo invalido."}

        costo = int(opcion.get("costo", 0) or 0)
        if heroe.oro < costo:
            return {"ok": False, "mensaje": f"No tienes oro para mejorar ({costo}G)."}

        heroe.oro -= costo
        item_data.setdefault("stats", {})
        stat_mejora = _stat_principal_equipo(item_data)
        item_data["stats"][stat_mejora] = int(item_data["stats"].get(stat_mejora, 0) or 0) + 1
        item_data["nivel_mejora"] = int(item_data.get("nivel_mejora", 0) or 0) + 1
        nombre = item_data.get("nombre", id_equipo)

        return {
            "ok": True,
            "mensaje": f"{nombre} mejorado (+1 {stat_mejora}). Oro restante: {heroe.oro}G.",
            "refrescar_submenu": True,
        }

    if modo == "herrero" and submenu == "forjar" and accion == "forjar_receta":
        id_resultado = str(opcion.get("resultado", ""))
        costo = int(opcion.get("costo", 0) or 0)
        materiales = opcion.get("materiales", {}) or {}

        if heroe.oro < costo:
            return {"ok": False, "mensaje": f"No tienes oro suficiente ({costo}G)."}

        faltantes = []
        for id_item, cantidad in materiales.items():
            if not heroe.tiene_item(id_item, int(cantidad)):
                nombre = items_db.get(id_item, {}).get("nombre") or equipo_db.get(id_item, {}).get("nombre") or id_item
                faltantes.append(f"{nombre} x{cantidad}")

        if faltantes:
            return {"ok": False, "mensaje": f"Faltan materiales: {', '.join(faltantes)}."}

        heroe.oro -= costo
        for id_item, cantidad in materiales.items():
            heroe.usar_item(id_item, int(cantidad))
        heroe.agregar_item(id_resultado, 1)

        nombre_res = equipo_db.get(id_resultado, {}).get("nombre") or items_db.get(id_resultado, {}).get("nombre") or id_resultado
        return {
            "ok": True,
            "mensaje": f"Forja exitosa: {nombre_res}. Oro restante: {heroe.oro}G.",
            "refrescar_submenu": True,
        }

    return {"ok": False, "mensaje": "Accion no disponible."}
