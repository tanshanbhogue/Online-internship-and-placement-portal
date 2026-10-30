"""Sprint 2 extension point (owner: Tanmayi).

Every module in this package that defines ``install(app: FastAPI) -> None`` is called once by
app.main.create_app(), in alphabetical order; the last one installed is the outermost middleware.
"""
