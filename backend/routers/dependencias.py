"""Dependencia de 503 y clase de ruta que responde {"detalle": "cargando"} (esqueleto, compartido).

FastAPI envuelve HTTPException en {"detail": ...}. Para devolver la clave `detalle` sin tocar main.py,
los routers usan `route_class=RutaDetalle`: atrapa DatosNoListos y responde el JSON exacto del contrato.
(Alternativa equivalente, si se prefiere: en main.py registrar un @app.exception_handler(DatosNoListos).)
"""
from fastapi import Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

from ..estado import EQUIPOS, estado


class DatosNoListos(Exception):
    """Los datos aún no terminan de cargar."""


def requiere_datos() -> None:
    if not estado.listo:
        raise DatosNoListos()


def valida_equipo(equipo: str | None) -> str | None:
    if equipo is not None and equipo not in EQUIPOS:
        raise HTTPException(status_code=404, detail=f"Equipo desconocido: {equipo}")
    return equipo


DEP_DATOS = [Depends(requiere_datos)]


class RutaDetalle(APIRoute):
    def get_route_handler(self):
        original = super().get_route_handler()

        async def handler(request: Request):
            try:
                return await original(request)
            except DatosNoListos:
                return JSONResponse(status_code=503, content={"detalle": "cargando"})

        return handler
