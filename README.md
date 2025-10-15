
# API de Análisis Geográfico (FastAPI + REST Countries)

Esta es una prueba técnica para Autivo que consta de la creación una API REST en Python (FastAPI) que consume REST Countries, para el
análisis e información procesada sobre países.

---

## Requisitos previos

Este proyecto fue desarrollado utilizando:

- Python `v3.13.5`
- Pip `25.2`    

Es necesario tener ambos instalados en el sistema. Puedes descargarlos/actualizarlos desde los sitios oficiales:

https://www.python.org/downloads/

https://pip.pypa.io/en/stable/installation/

#### Nota: pip se instala junto con Python. Si usas otra versión de Python (3.8+), asegúrate de que pip esté actualizado.
```sh
python -m pip install --upgrade pip
```
#### Recomendado (opcional): crear un entorno virtual antes de instalar dependencias.
```sh
python -m venv .venv
```
---

#### Linux/MacOS

```sh
source .venv/bin/activate
```
---

#### Windows (PowerShell)
```sh
.\.venv\Scripts\Activate.ps1
```
---

## Instalación

1. Clona el repositorio desde GitHub. Puedes hacerlo con HTTPS o SSH:

**HTTPS**
```sh
git clone https://github.com/Matias-Egana/Prueba_Autivo.git
```
**SSH**
```sh
git clone git@github.com:Matias-Egana/Prueba_Autivo.git
```
2. Dentro del proyecto, dirígete a requirements.txt

3. Instala las dependencias:
```sh
pip install -r requirements.txt
```

## Ejecutar el proyecto
1. Inicia el servidor desde la carpeta Backend:
```sh
python -m uvicorn app.main:app --reload
```
2. Abre el siguiente enlace en tu navegador (Recomendado):
```sh
http://localhost:8000
```
## Variables de entorno

En `.env` se encuentra las variables de entorno:
- COUNTRIES_BASE (por defecto: `https://restcountries.com/v3.1`)

## Estructura del proyecto
```sh
Prueba_Autivo/
├─ app/          
│  ├─ main.py              # Principal
│  ├─ maps.py              # Mapeos
│  ├─ models.py            # Modelos 
│  └─ routes.py            # Rutas de los endpoints
├─ .env                    # Variables de entorno
├─ dockerfile              
├─ docker-compose.yml      
├─ README.md            
└─ requirements.txt   

```
## Endpoints
1) Análisis de Vecindad - `GET /countries/{code}/neighbors` 

- Dado un país por códigos (Ejemplo: CHL, USA, DEU), retorna:
- Lista de vecinos con frontera terrestre (nombre, capital, población).
- Población total de la región fronteriza: suma del país + todos sus vecinos.
- Vecinos con idiomas compartidos: lista de códigos con los que comparte al menos un idioma.

2) Rutas Terrestres - `GET /route?from={code}&to={code}`
- Determina si existe una ruta terrestre entre dos países y retorna el camino más corto por fronteras. Si no existe, lo indica explícitamente.

3) Estadísticas Regionales - `GET /regions/{region}/stats`
- Regiones válidas: Americas, Europe, Africa, Asia, Oceania. Retorna:
- Cantidad total de países en la región
- Población total y promedio
- Cantidad de idiomas únicos hablados
- Top 5 países por población (nombre y población)

4) Búsqueda Avanzada - `POST /countries/search`
- Permite buscar países aplicando múltiples filtros simultáneamente. Body
esperado (todos los campos son opcionales):
```sh
{
"minPopulation": 10000000,
"maxPopulation": 100000000,
"languages": ["Spanish", "English"],
"region": "Americas"
}
```
- Response body

```sh
{
  "total": 11,
  "results": [
    {
      "code": "ARG",
      "name": "Argentina"
    },
    {
      "code": "BOL",
      "name": "Bolivia"
    },
    {
      "code": "CAN",
      "name": "Canada"
    },
    {
      "code": "CHL",
      "name": "Chile"
    },
    {
      "code": "COL",
      "name": "Colombia"
    },
    {
      "code": "CUB",
      "name": "Cuba"
    },
    {
      "code": "DOM",
      "name": "Dominican Republic"
    },
    {
      "code": "ECU",
      "name": "Ecuador"
    },
    {
      "code": "GTM",
      "name": "Guatemala"
    },
    {
      "code": "PER",
      "name": "Peru"
    },
    {
      "code": "VEN",
      "name": "Venezuela"
    }
  ]
}
```
## Docker (bonus)
#### Build & Run
```sh
docker-compose build
```
```sh
docker-compose up
```
#### Test (Recomendado)

```sh
http://localhost:8000
```

## Consideraciones

Agradecer la oportunidad de participar en esta selección.

Espero poder trabajar con ustedes.
   
