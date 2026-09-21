"""Paso 3: verificar los chequeos que reporta el hospital y premiar en el CRM.

Es el único paso que cruza el chequeo con la póliza del asegurado.
"""

from dataclasses import dataclass

from agente.gamificacion import aplica_a, premiar


@dataclass
class Decision:
    id_chequeo: str
    poliza: str
    tipo: str
    estado: str  # Premiado | Rechazado | Ya premiado
    motivo: str
    asegurado: dict | None = None
    campana: dict | None = None
    puntos: int = 0
    nivel_nuevo: str | None = None
    subio_de_nivel: bool = False
    prima_antes: float | None = None
    prima_despues: float | None = None


def evaluar(chequeos: list[dict], asegurados: list[dict], campanas: list[dict], ya_premiados: set[str]) -> tuple[list[Decision], dict]:
    """Decide qué chequeos se premian y cómo queda cada asegurado. No escribe nada: es lógica pura."""
    por_poliza = {a["poliza"]: dict(a) for a in asegurados}  # copias: se actualizan en memoria
    procesados = set(ya_premiados)
    decisiones = []
    for ch in chequeos:
        base = dict(id_chequeo=ch["id_chequeo"], poliza=ch["poliza"], tipo=ch["tipo_chequeo"])
        if ch["id_chequeo"] in procesados:
            decisiones.append(Decision(**base, estado="Ya premiado", motivo="Este chequeo ya fue premiado antes."))
            continue
        a = por_poliza.get(ch["poliza"])
        if a is None:
            decisiones.append(Decision(**base, estado="Rechazado", motivo="La póliza no existe en el CRM."))
            continue
        del_tipo = [c for c in campanas if c["tipo_chequeo"] == ch["tipo_chequeo"] and c.get("estado", "Activa") == "Activa"]
        if not del_tipo:
            decisiones.append(Decision(**base, estado="Rechazado", asegurado=a,
                                       motivo="No hay una campaña activa para este chequeo."))
            continue
        campana = next((c for c in del_tipo if aplica_a(c, a["sexo"], a["edad"])), None)
        if campana is None:
            c = del_tipo[0]
            sexo = "" if c["sexo"] == "Todos" else f"{'hombres' if c['sexo'] == 'M' else 'mujeres'} de "
            decisiones.append(Decision(**base, estado="Rechazado", asegurado=a, motivo=(
                f"Fuera de la población objetivo ({sexo}{c['edad_min']}-{c['edad_max']} años; "
                f"el asegurado tiene {a['edad']})."
            )))
            continue
        r = premiar(a["puntos"], a["prima_base"], campana["puntos"])
        decisiones.append(Decision(
            **base, estado="Premiado", asegurado=dict(a), campana=campana, puntos=campana["puntos"],
            motivo=f"+{campana['puntos']} puntos por la campaña «{campana['nombre']}».",
            nivel_nuevo=r.nivel, subio_de_nivel=r.subio_de_nivel,
            prima_antes=a["prima_final"], prima_despues=r.prima_final,
        ))
        a.update(puntos=r.puntos, nivel=r.nivel, descuento=r.descuento, prima_final=r.prima_final)
        procesados.add(ch["id_chequeo"])
    return decisiones, por_poliza


def aplicar(crm, chequeos: list[dict]) -> list[Decision]:
    """Evalúa contra el estado actual de Notion y escribe los premios."""
    decisiones, finales = evaluar(chequeos, crm.asegurados(), crm.campanas(solo_activas=True), crm.ids_premiados())
    tocados = set()
    for d in decisiones:
        if d.estado != "Premiado":
            continue
        crm.registrar_chequeo(d.id_chequeo, d.poliza, d.tipo, next(c["fecha"] for c in chequeos if c["id_chequeo"] == d.id_chequeo),
                              d.asegurado["id"], d.campana["id"], d.puntos)
        tocados.add(d.poliza)
    for poliza in tocados:
        a = finales[poliza]
        crm.actualizar_asegurado(a["id"], a["puntos"], a["nivel"], a["descuento"], a["prima_final"])
    return decisiones
