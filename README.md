> [!WARNING]
> Este proyecto es un caso de estudio estrictamente académico, educativo y demostrativo. Utiliza datos, inventarios y pedidos 100 % simulados. No guarda ninguna relación comercial, oficial, operativa ni contractual con Milky Way Ediciones ni con sus filiales.

# Dashboard de Inventario B2B

Dashboard de gestión logística B2B para la distribución de mangas a librerías. El sistema organiza el catálogo, las existencias, los costes, los precios mayoristas, los plazos de reposición y los pedidos de clientes.

## 📊 Descripción

El análisis de inventario contempla indicadores críticos de la cadena de suministro, calculados dinámicamente:

- **🔄 Rotación de inventario:** relación anualizada entre el ritmo de consumo o la demanda proyectada y las existencias actuales en almacén.
- **📅 Días de inventario:** estimación de cuántos días operativos puede cubrir el stock actual según la demanda diaria promedio antes de sufrir una rotura de stock.
- **📈 Fill Rate:** proporción de las unidades solicitadas por clientes mayoristas que la editorial puede servir de forma inmediata.
- **🛡️ Stock de seguridad:** unidades de reserva para amortiguar retrasos en los plazos de imprenta o picos inesperados de demanda.
- **🚨 Punto de reorden (ROP):** nivel crítico de existencias a partir del cual el sistema activa una alerta visual para solicitar una nueva tirada.

La API pública de **Jikan**, que proporciona datos de MyAnimeList, enriquece la información del catálogo con títulos e imágenes de portada. La integración incluye tolerancia a fallos y semillas locales de contingencia. Los datos comerciales, inventarios y pedidos de este caso de estudio son simulados y no representan operaciones reales.

### 📦 Historial de Pedidos B2B y Suministro

El Dashboard ofrece un historial de pedidos ordenado por fecha y un seguimiento visual de los **Backorders**: unidades que siguen pendientes de stock después de una entrega parcial. Los badges verdes identifican los pedidos completados y los naranjas destacan las unidades pendientes para facilitar su seguimiento por parte de la editorial.

## 🏗️ Arquitectura

El proyecto separa responsabilidades siguiendo el patrón MVC:

- **🗄️ Modelo:** SQLAlchemy define las entidades relacionales `Manga` y `B2BOrder`, sus claves foráneas y la eliminación en cascada (`ON DELETE CASCADE`).
- **✅ Esquemas:** Pydantic v2 valida los datos de entrada y salida. Los importes y métricas usan `Decimal` para conservar precisión y se validan para impedir valores negativos o no finitos (`NaN`).
- **⚙️ Controlador y API:** FastAPI expone los endpoints y coordina las operaciones de inventario, las consultas externas y las agregaciones de base de datos.
- **📦 Pedidos y backorders:** `/api/inventory/dashboard` devuelve el historial completo en orden descendente por fecha y calcula las unidades pendientes de cada entrega parcial.
- **🖥️ Vista:** interfaz responsiva con Bootstrap 5 y JavaScript asíncrono (`fetch`). Presenta KPIs, formularios y estados de suministro con badges verdes para pedidos completados y naranjas para backorders.
- **💾 Persistencia:** SQLite almacena los datos localmente mediante SQLAlchemy. Los campos `cost` y `price_b2b` usan `Numeric(10, 2)` para conservar precisión monetaria.
- **🌐 Catálogo:** Jikan es una fuente pública complementaria; sus datos no sustituyen la información operativa simulada del inventario.

### 🗂️ Estructura del proyecto

```text
.
├── config/
│   └── database.py
├── controllers/
│   └── inventory_controller.py
├── models/
│   ├── db_models.py
│   └── schemas.py
├── views/
│   └── dashboard.html
├── .gitignore
├── inventory.db
├── main.py
├── README.md
└── requirements.txt
```

La configuración local utiliza `sqlite:///./inventory.db`. Durante el primer arranque del servidor se inicializan las tablas relacionales y el archivo de base de datos mediante `Base.metadata.create_all(bind=engine)`.

## 🚀 Guía de despliegue local

### 📋 Requisitos

- Python 3.10 o posterior; el proyecto también está preparado para entornos Python 3.14.
- Gestor de paquetes `pip`.
- Windows PowerShell, macOS o Linux.

### 📥 Instalación

Desde la raíz del proyecto, activa el entorno virtual `.venv`.

**Windows PowerShell**

```powershell
.venv\Scripts\Activate.ps1
```

**macOS o Linux**

```bash
source .venv/bin/activate
```

Instala las dependencias desde el archivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

### ▶️ Inicio del servidor

El servidor se inicia en el puerto `8080` para reducir conflictos con otros servicios locales. Desde la raíz del proyecto, ejecuta FastAPI en modo desarrollo con Uvicorn:

```bash
python -m uvicorn main:app --reload --port 8080
```