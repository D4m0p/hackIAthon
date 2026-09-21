"""Cliente mínimo del CRM en Notion (sección 2 del contrato).

Los nombres de los campos deben coincidir EXACTAMENTE con los de Notion.
"""

import time

import requests

API = "https://api.notion.com/v1"
VERSION = "2022-06-28"


class ErrorCRM(Exception):
    pass


# --- Conversión entre valores de Python y propiedades de Notion -------------

def _titulo(v):
    return {"title": [{"text": {"content": str(v)}}]}


def _texto(v):
    return {"rich_text": [{"text": {"content": str(v)[:2000]}}]}


def _num(v):
    return {"number": v}


def _sel(v):
    return {"select": {"name": str(v)}}


def _leer(prop):
    tipo = prop["type"]
    v = prop[tipo]
    if tipo in ("title", "rich_text"):
        return "".join(t["plain_text"] for t in v)
    if tipo == "select":
        return v["name"] if v else None
    if tipo == "relation":
        return [r["id"] for r in v]
    if tipo == "date":
        return v["start"] if v else None
    return v  # number y otros simples


class CRM:
    def __init__(self, token: str, db_asegurados: str, db_campanas: str, db_chequeos: str):
        self.db = {"asegurados": db_asegurados, "campanas": db_campanas, "chequeos": db_chequeos}
        self.s = requests.Session()
        self.s.headers.update({
            "Authorization": f"Bearer {token}",
            "Notion-Version": VERSION,
            "Content-Type": "application/json",
        })

    def _pedir(self, metodo, ruta, **kw):
        for intento in range(4):
            r = self.s.request(metodo, f"{API}{ruta}", timeout=30, **kw)
            if r.status_code == 429:  # límite de Notion: ~3 peticiones por segundo
                time.sleep(float(r.headers.get("Retry-After", 1)) + intento)
                continue
            if not r.ok:
                raise ErrorCRM(f"Notion {r.status_code}: {r.json().get('message', r.text)}")
            return r.json()
        raise ErrorCRM("Notion rechazó demasiadas peticiones seguidas; intente de nuevo.")

    def _consultar(self, base, filtro=None):
        cuerpo, filas = {"page_size": 100}, []
        if filtro:
            cuerpo["filter"] = filtro
        while True:
            res = self._pedir("POST", f"/databases/{self.db[base]}/query", json=cuerpo)
            filas += res["results"]
            if not res.get("has_more"):
                return filas
            cuerpo["start_cursor"] = res["next_cursor"]

    def _crear(self, base, props):
        return self._pedir("POST", "/pages", json={"parent": {"database_id": self.db[base]}, "properties": props})

    def _actualizar(self, page_id, props):
        return self._pedir("PATCH", f"/pages/{page_id}", json={"properties": props})

    def _archivar(self, page_id):
        return self._pedir("PATCH", f"/pages/{page_id}", json={"archived": True})

    # --- Verificación ----------------------------------------------------------

    def verificar(self) -> list[str]:
        """Revisa que existan los campos del contrato. Devuelve la lista de problemas."""
        esperados = {
            "asegurados": ["Nombre", "Póliza", "Sexo", "Edad", "Prima base", "Puntos", "Nivel", "Descuento %", "Prima final"],
            "campanas": ["Nombre", "Tipo de chequeo", "Diagnóstico que la motiva", "Sexo objetivo",
                         "Edad mínima", "Edad máxima", "Puntos", "Mensaje", "Estado"],
            "chequeos": ["Registro", "ID hospital", "Asegurado", "Campaña", "Fecha", "Puntos otorgados"],
        }
        problemas = []
        for base, campos in esperados.items():
            try:
                props = self._pedir("GET", f"/databases/{self.db[base]}")["properties"]
            except ErrorCRM as e:
                problemas.append(f"Base '{base}': {e}")
                continue
            faltan = [c for c in campos if c not in props]
            if faltan:
                problemas.append(f"Base '{base}': faltan los campos {', '.join(faltan)}")
        return problemas

    # --- Asegurados ------------------------------------------------------------

    def asegurados(self) -> list[dict]:
        salida = []
        for p in self._consultar("asegurados"):
            pr = {k: _leer(v) for k, v in p["properties"].items()}
            salida.append({
                "id": p["id"], "poliza": pr.get("Póliza"), "nombre": pr.get("Nombre"),
                "sexo": pr.get("Sexo"), "edad": pr.get("Edad") or 0,
                "prima_base": pr.get("Prima base") or 0, "puntos": pr.get("Puntos") or 0,
                "nivel": pr.get("Nivel") or "Bronce", "descuento": pr.get("Descuento %") or 0,
                "prima_final": pr.get("Prima final") or pr.get("Prima base") or 0,
            })
        return sorted(salida, key=lambda a: a["poliza"] or "")

    def crear_asegurado(self, a: dict):
        self._crear("asegurados", {
            "Nombre": _titulo(a["nombre"]), "Póliza": _texto(a["poliza"]), "Sexo": _sel(a["sexo"]),
            "Edad": _num(int(a["edad"])), "Prima base": _num(float(a["prima_base"])), "Puntos": _num(0),
            "Nivel": _sel("Bronce"), "Descuento %": _num(0), "Prima final": _num(float(a["prima_base"])),
        })

    def actualizar_asegurado(self, page_id: str, puntos: int, nivel: str, descuento: int, prima_final: float):
        self._actualizar(page_id, {
            "Puntos": _num(puntos), "Nivel": _sel(nivel),
            "Descuento %": _num(descuento), "Prima final": _num(prima_final),
        })

    # --- Campañas --------------------------------------------------------------

    def campanas(self, solo_activas=False) -> list[dict]:
        filtro = {"property": "Estado", "select": {"equals": "Activa"}} if solo_activas else None
        salida = []
        for p in self._consultar("campanas", filtro):
            pr = {k: _leer(v) for k, v in p["properties"].items()}
            salida.append({
                "id": p["id"], "nombre": pr.get("Nombre"), "tipo_chequeo": pr.get("Tipo de chequeo"),
                "diagnostico": pr.get("Diagnóstico que la motiva"), "sexo": pr.get("Sexo objetivo") or "Todos",
                "edad_min": pr.get("Edad mínima") or 0, "edad_max": pr.get("Edad máxima") or 120,
                "puntos": pr.get("Puntos") or 100, "mensaje": pr.get("Mensaje"), "estado": pr.get("Estado"),
            })
        return salida

    def cerrar_campanas_activas(self):
        for c in self.campanas(solo_activas=True):
            self._actualizar(c["id"], {"Estado": _sel("Cerrada")})

    def crear_campana(self, c: dict):
        self._crear("campanas", {
            "Nombre": _titulo(c["nombre"]), "Tipo de chequeo": _sel(c["tipo_chequeo"]),
            "Diagnóstico que la motiva": _texto(c["diagnostico"]), "Sexo objetivo": _sel(c["sexo"]),
            "Edad mínima": _num(c["edad_min"]), "Edad máxima": _num(c["edad_max"]),
            "Puntos": _num(c["puntos"]), "Mensaje": _texto(c["mensaje"]), "Estado": _sel("Activa"),
        })

    # --- Chequeos premiados ----------------------------------------------------

    def ids_premiados(self) -> set[str]:
        return {_leer(p["properties"]["ID hospital"]) for p in self._consultar("chequeos")}

    def registrar_chequeo(self, id_hospital, poliza, tipo, fecha, asegurado_id, campana_id, puntos):
        self._crear("chequeos", {
            "Registro": _titulo(f"{poliza} · {tipo}"), "ID hospital": _texto(id_hospital),
            "Asegurado": {"relation": [{"id": asegurado_id}]}, "Campaña": {"relation": [{"id": campana_id}]},
            "Fecha": {"date": {"start": fecha}}, "Puntos otorgados": _num(puntos),
        })

    # --- Reinicio de la demo ---------------------------------------------------

    def reiniciar(self, asegurados: list[dict]):
        """Borra (archiva) todo y vuelve a cargar los asegurados de prueba."""
        for base in ("chequeos", "campanas", "asegurados"):
            for p in self._consultar(base):
                self._archivar(p["id"])
        for a in asegurados:
            self.crear_asegurado(a)
