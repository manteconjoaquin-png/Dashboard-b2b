from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from config.database import Base, engine
import models.db_models
from controllers.inventory_controller import router as inventory_router


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Milky Way B2B Distro Dashboard")

app.include_router(inventory_router)
app.mount("/views", StaticFiles(directory="views"), name="views")


@app.get("/")
def serve_dashboard() -> FileResponse:
    return FileResponse("views/dashboard.html")