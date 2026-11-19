from fastapi import FastAPI
from starlette.middleware.gzip import GZipMiddleware

MIN_SIZE_BYTES = 1024


def install(app: FastAPI) -> None:
    app.add_middleware(GZipMiddleware, minimum_size=MIN_SIZE_BYTES)
