from typing import List, Any
from fastapi import APIRouter
import os
from .models import Neighbors, Shared_Language, Neighbors_Response
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Body
from collections import deque
import httpx
from .maps import map_countries,map_languages,map_name,map_neighbors

router = APIRouter()
load_dotenv()

BASE_URL = os.getenv("COUNTRIES_BASE", "https://restcountries.com/v3.1")

def rc_client():
    limits = httpx.Limits(max_connections=20, max_keepalive_connections=10)
    return httpx.AsyncClient(
        base_url=BASE_URL,
        timeout=httpx.Timeout(10.0, connect=5.0),
        limits=limits,
        headers={"User-Agent": "Autivo/1.0 (+fastapi)"},
    )

# Routes
@router.get("/")
def read_root():
    return {"message": "Autivo API"}

@router.get("/countries")
async def get_all_countries(
    limit: int = 250,              
    offset: int = 0,               
    include_borders: bool = False, 
):
    fields = "name,cca3,region,population,capital"
    if include_borders:
        fields += ",borders"      

    async with rc_client() as c:
        r = await c.get("/all", params={"fields": fields})
        r.raise_for_status()
        items = r.json()

    # Ordenado por nombre
    items.sort(key=lambda d: (d.get("name", {}) or {}).get("common") or "")
    page = items[offset: offset + limit]
    return {
        "total": len(items),
        "limit": limit,
        "offset": offset,
        "results": [map_countries(x) for x in page],
    }


# Análisis de vecindad
@router.get("/countries/{code}/neighbors", response_model=Neighbors_Response)
async def get_neighbors(code: str):
    code = code.upper()
    base_fields = "borders,name,capital,population,cca3,cca2,languages"

    async with rc_client() as c:
        r1 = await c.get(f"/alpha/{code}", params={"fields": base_fields})
        if r1.status_code == 404:
            raise HTTPException(404, f"País con código '{code}' no fue encontrado")
        r1.raise_for_status()
        payload = r1.json()
        base: dict[str, object] = payload[0] if isinstance(payload, list) else payload

        borders = base.get("borders") or []
        base_pop = base.get("population") or 0

        if not borders:
            return Neighbors_Response(
                countries=Neighbors(**map_neighbors(base)),
                list_Neighbors=[],
                total_Population=int(base_pop), 
                list_Shared_Language=[],
            )

        neigh_fields = "name,capital,population,cca3,cca2,languages"
        r2 = await c.get("/alpha", params={"codes": ",".join(borders), "fields": neigh_fields})
        r2.raise_for_status()
        neigh_raw: list[dict[str, object]] = r2.json()  

    list_neighbors = [Neighbors(**map_neighbors(n)) for n in neigh_raw]
    total_population = int(base_pop) + sum(int(n.get("population") or 0) for n in neigh_raw)

    base_langs = map_languages(base)
    shared_lang_items: list[Shared_Language] = []
    if base_langs:
        for n in neigh_raw:
            shared = sorted(list(base_langs.intersection(map_languages(n))))
            if shared:
                shared_lang_items.append(
                    Shared_Language(
                        Code=n.get("cca3") or n.get("cca2"), 
                        name=map_name(n),
                        languages=shared, 
                    )
                )
    return Neighbors_Response(
        countries=Neighbors(**map_neighbors(base)),
        list_Neighbors=list_neighbors,
        total_Population=total_population,
        list_Shared_Language=shared_lang_items,
    )

# Rutas Terrestre
@router.get("/route")
async def get_route(
    from_code: str = Query(..., alias="from", description="Código CCA3 origen"),
    to_code: str   = Query(..., alias="to",   description="Código CCA3 destino"),
):
    src, dst = from_code.upper(), to_code.upper()

    async with rc_client() as c:
        r = await c.get("/all", params={"fields": "cca3,borders"})
        r.raise_for_status()
        items: list[dict[str, object]] = r.json()  

    graph: dict[str, list[str]] = {it["cca3"]: (it.get("borders") or []) for it in items}  

    if src not in graph:
        raise HTTPException(404, f"País de origen '{src}' no encontrado")
    if dst not in graph:
        raise HTTPException(404, f"País de destino '{dst}' no encontrado")
    if src == dst:
        return {"connected": True, "path": [src], "hops": 0}

    q: deque[list[str]] = deque([[src]])
    seen: set[str] = {src}
    while q:
        path = q.popleft()
        last = path[-1]
        for nb in graph.get(last, []):
            if nb in seen:
                continue
            new_path = path + [nb]
            if nb == dst:
                return {"connected": True, "path": new_path, "hops": len(new_path) - 1}
            seen.add(nb)
            q.append(new_path)

    return {"connected": False, "message": f"No existe conexión terrestre entre {src} y {dst}"}

# Estadisticas Regionales
@router.get("/regions/{region}/stats")
async def get_region_stats(
    region: str,
):
    fields = "name,cca3,population,languages"
    async with rc_client() as c:
        r = await c.get(f"/region/{region}", params={"fields": fields})
        if r.status_code == 404:
            raise HTTPException(404, f"La Región '{region}' no encontrada")
        r.raise_for_status()
        data: List[dict[str, object]] = r.json() 

    if not data:
        raise HTTPException(404, f"La Región '{region}' no tiene países")

    countries_count = len(data)
    populations = [int(d.get("population") or 0) for d in data]
    total_population = sum(populations)
    average_population = round(total_population / countries_count, 2) if countries_count else 0.0

    unique_lang_codes: set[str] = set()
    for d in data:
        languages = d.get("languages") or {}
        if isinstance(languages, dict):
            unique_lang_codes.update(str(k).lower() for k in languages.keys())
    unique_languages_count = len(unique_lang_codes)
    top5 = sorted(
        data, key=lambda d: int(d.get("population") or 0), reverse=True
    )[:5]
    top5_by_population = [
        {
            "code": d.get("cca3") or "",
            "name": map_name(d),
            "population": int(d.get("population") or 0),
        }
        for d in top5
    ]

    return {
        "region": region,
        "countries_count": countries_count,
        "total_population": total_population,
        "average_population": average_population,
        "unique_languages_count": unique_languages_count,
        "top5_by_population": top5_by_population,
    }



# Búsqueda Avanzada
@router.post("/countries/search")
async def post_search(payload: dict[str, Any] = Body(...)):
    min_pop = payload.get("minPopulation")
    max_pop = payload.get("maxPopulation")
    region = payload.get("region")
    langs_req = payload.get("languages") or [] 

    langs_req_set = {str(x).lower() for x in langs_req if str(x).strip()} if isinstance(langs_req, list) else set()

    fields = "name,cca3,cca2,region,population,languages"
    
    async with rc_client() as c:
        r = await c.get("/all", params={"fields": fields})
        r.raise_for_status()
        items: list[dict[str, object]] = r.json()  

    def speaks_lang(country: dict[str, object]) -> bool:
        if not langs_req_set:
            return True
        langs = country.get("languages") or {}
        if not isinstance(langs, dict) or not langs:
            return False
        codes = {str(k).lower() for k in langs.keys()}
        names = {str(v).lower() for v in langs.values()}
        return bool(langs_req_set & codes) or bool(langs_req_set & names)

    filtered: list[dict[str, object]] = []
    for it in items:
        if region and str(it.get("region") or "").lower() != str(region).lower():
            continue
        pop = int(it.get("population") or 0)
        if min_pop is not None and pop < int(min_pop):
            continue
        if max_pop is not None and pop > int(max_pop):
            continue
        if not speaks_lang(it):
            continue
        filtered.append(it)

    filtered.sort(key=lambda d: map_name(d) or "")

    results = [
        {
            "code": (it.get("cca3") or it.get("cca2")),
            "name": map_name(it),
        }
        for it in filtered
    ]

    return {"total": len(results), "results": results}

