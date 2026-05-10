import httpx
from typing import Optional

BASE_URL = "https://api-comexstat.mdic.gov.br"


class ComexStatClient:
    """Cliente sincrono para a API oficial do ComexStat."""

    def __init__(self, timeout=30):
        self.timeout = timeout

    def _query(self, flow: str, ano: int, mes: Optional[int] = None,
               pais: Optional[int] = None, estado: Optional[int] = None,
               ncm: Optional[str] = None, modal: Optional[str] = None) -> list:
        period = {"from": f"{ano}-01", "to": f"{ano}-12"}
        filters = []
        details = ["ncm"]

        if mes:
            period = {"from": f"{ano}-{mes:02d}", "to": f"{ano}-{mes:02d}"}
        if pais:
            filters.append({"filter": "country", "values": [pais]})
            details.append("country")
        if estado:
            filters.append({"filter": "state", "values": [estado]})
            details.append("state")
        if ncm:
            ncm_len = len(ncm)
            if ncm_len == 2:
                filters.append({"filter": "chapter", "values": [ncm]})
            elif ncm_len == 4:
                filters.append({"filter": "heading", "values": [ncm]})
            elif ncm_len == 6:
                filters.append({"filter": "subHeading", "values": [ncm]})
            else:
                filters.append({"filter": "ncm", "values": [ncm]})
        if modal:
            filters.append({"filter": "via", "values": [modal]})
            details.append("via")

        payload = {
            "flow": flow,
            "monthDetail": bool(mes),
            "period": period,
            "metrics": ["metricFOB", "metricKG"],
        }
        if filters:
            payload["filters"] = filters
        if details:
            payload["details"] = details

        with httpx.Client(timeout=self.timeout) as c:
            r = c.post(f"{BASE_URL}/general", json=payload)
            r.raise_for_status()
            data = r.json()
            # API returns: {"data": {"list": [...]}}
            raw_list = data.get("data", {}).get("list", [])
            return raw_list

    def get_countries(self) -> list:
        with httpx.Client(timeout=self.timeout) as c:
            r = c.get(f"{BASE_URL}/tables/countries")
            data = r.json()
            d = data.get("data", {})
            if isinstance(d, dict):
                return d.get("list", [])
            return d if isinstance(d, list) else []

    def get_states(self) -> list:
        with httpx.Client(timeout=self.timeout) as c:
            r = c.get(f"{BASE_URL}/tables/uf")
            data = r.json()
            d = data.get("data", {})
            if isinstance(d, dict):
                return d.get("list", [])
            return d if isinstance(d, list) else []

    def get_last_update(self) -> str:
        with httpx.Client(timeout=self.timeout) as c:
            r = c.get(f"{BASE_URL}/general/dates/updated")
            d = r.json().get("data", {})
            return d.get("updated", "")

    def get_years(self) -> dict:
        with httpx.Client(timeout=self.timeout) as c:
            r = c.get(f"{BASE_URL}/general/dates/years")
            return r.json().get("data", {})
