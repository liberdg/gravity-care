from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import models  # noqa: F401  (enregistre les tables)
from .api import router
from .sim_routes import router as sim_router
from .database import Base, engine
from .errors import ApiError


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="GRAVITY CARE API",
    description="Prototype de hackathon. Données SIMULÉES. Pas un dispositif médical, aucun diagnostic.",
    lifespan=lifespan,
)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"],
                   allow_methods=["*"], allow_headers=["*"])


@app.exception_handler(ApiError)
def api_error_handler(_: Request, exc: ApiError):
    return JSONResponse(status_code=exc.status_code, content={"code": exc.code, "message": exc.message})


@app.exception_handler(RequestValidationError)
def validation_handler(_: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"code": "validation_error", "message": str(exc.errors())})


@app.get("/api/health")
def health():
    return {"status": "ok", "simulated_data": True}


app.include_router(router)
app.include_router(sim_router)
