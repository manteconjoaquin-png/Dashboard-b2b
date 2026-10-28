> [!WARNING]
> Este proyecto es un caso de estudio estrictamente académico, educativo y demostrativo desarrollado con datos, inventarios y pedidos 100% simulados. No guarda ninguna relación comercial, oficial, operativa ni contractual con la empresa Milky Way Ediciones ni ninguna de sus filiales

# Dashboard de Inventario B2B

## Descripción

Dashboard de gestión logística B2B orientado a la distribución de mangas a librerías. El sistema organiza el catálogo, las existencias, los costes, los precios mayoristas, los plazos de reposición y los pedidos de clientes.

El análisis de inventario contempla indicadores de cadena de suministro como:

- **Rotación de inventario:** relación entre el consumo o las ventas del periodo y el inventario medio.
- **Días de inventario:** estimación de cuántos días puede cubrir el stock actual según la demanda diaria promedio.
- **Fill Rate:** proporción de las unidades solicitadas que se sirven.
- **Stock de seguridad:** unidades de reserva para amortiguar variaciones de demanda o reposición.
- **Punto de reorden:** nivel de existencias a partir del cual conviene reponer.

La API pública de **Jikan**, que proporciona datos de MyAnimeList, sirve como fuente de apoyo para información del catálogo, como identificadores, títulos e imágenes. Los datos comerciales, inventarios y pedidos de este caso de estudio son simulados; no representan operaciones reales.

## Arquitectura

El proyecto sigue una separación por responsabilidades de estilo MVC:

- **Modelo:** SQLAlchemy define las entidades relacionales `Manga` y `B2BOrder`, así como su relación y cascada de borrado.
- **Esquemas:** Pydantic v2 valida datos de entrada y salida, incluidos importes y métricas representados con `Decimal` en los esquemas.
- **Controlador/API:** FastAPI expone los endpoints y coordina las operaciones entre los modelos, la lógica de negocio y las respuestas.
- **Persistencia:** SQLite almacena los datos localmente mediante SQLAlchemy. Los importes `cost` y `price_b2b` usan `Numeric(10, 2)` para conservar precisión monetaria decimal.
- **Datos de catálogo:** Jikan se consume como fuente pública complementaria; sus datos no sustituyen la información operativa simulada del inventario.

Estructura actual de los módulos principales:

```text
.
├── config/
│   └── database.py
├── models/
│   ├── db_models.py
│   └── schemas.py
├── requirements.txt
└── README.md
```

La configuración local apunta a `sqlite:///./inventory.db`. Para crear automáticamente las tablas al iniciar la aplicación, el punto de entrada debe importar los modelos y ejecutar `Base.metadata.create_all(bind=engine)` durante la inicialización de FastAPI.

## Guía de Despliegue Local

### Requisitos

- Python 3.10 o posterior.
- `pip`.
- Windows PowerShell, macOS o Linux.

### Instalación

Desde la raíz del proyecto, crea el entorno virtual si aún no existe y actívalo.

**Windows PowerShell:**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS o Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instala las dependencias:

```bash
pip install -r requirements.txt
```

### Inicio del servidor

Desde la raíz del proyecto, inicia FastAPI en modo desarrollo:

```bash
fastapi dev main.py
```

Como alternativa, inicia Uvicorn directamente:

```bash
python -m uvicorn main:app --reload
```

Ambos comandos presuponen que existe `main.py` y que contiene una instancia de FastAPI llamada `app`. En la estructura actual del repositorio ese archivo todavía no está incluido, por lo que debe añadirse antes de poder ejecutar el servidor con estos comandos.

### Base de datos local

La primera conexión a `sqlite:///./inventory.db` crea el archivo `inventory.db` en el directorio desde el que se inicia la aplicación, si todavía no existe. Para que las tablas se creen también automáticamente en el primer arranque, `main.py` debe importar `Base`, `engine` y los modelos, y ejecutar `Base.metadata.create_all(bind=engine)`. Sin esa inicialización, SQLite puede crear el archivo al conectarse, pero las tablas no se generan por sí solas.