from typing import List, Optional
from pydantic import BaseModel

class Neighbors(BaseModel):
    code: str
    name: str
    capital: Optional[List[str]] = None
    population: Optional[int] = None

class Shared_Language(BaseModel):
    Code: str
    name: str
    languages: List[str]

class Neighbors_Response(BaseModel):
    countries: Neighbors
    list_Neighbors: List[Neighbors]
    total_Population: int
    list_Shared_Language: List[Shared_Language]

