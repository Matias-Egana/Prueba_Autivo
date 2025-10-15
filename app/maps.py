

def map_countries(c: dict[str, object]) -> dict[str, object]:
    name = (c.get("name") or {}).get("common") or (c.get("name") or {}).get("official")
    return {
        "code": c.get("cca3") or c.get("cca2"),
        "name": name,
        "region": c.get("region"),
        "population": c.get("population"),
        "capital": c.get("capital"),
        "borders": c.get("borders", []),
    }
def map_name(d: dict[str, object]) -> str:
    n = d.get("name") or {}
    return n.get("common") or n.get("official") or ""

def map_neighbors(d: dict[str, object]) -> dict[str, object]:
    return{
        "code":d.get("cca3") or d.get("cca2"),
        "name": map_name(d),
        "capital": d.get("capital"),
        "population": d.get("population")
    }

def map_languages(d: dict[str, object]) -> set[str]:
    languages = d.get("languages") or {}
    return set(languages.values())