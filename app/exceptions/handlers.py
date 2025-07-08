from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.status import *

def register_exception_handlers(app):

  @app.exception_handler(RequestValidationError)
  async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_detail = exc.errors()[0]
    return JSONResponse(
      status_code=HTTP_422_UNPROCESSABLE_ENTITY,
      content={
        "message": "Faltan datos o hay errores de validación.",
        "error": f"{error_detail['loc'][-1]}:{error_detail['msg']}"
      })

  @app.exception_handler(ValueError)
  async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
      status_code=HTTP_400_BAD_REQUEST,
      content={"message": str(exc)})

  @app.exception_handler(PermissionError)
  async def unauthorized_exception_handler(request: Request, exc: PermissionError):
    return JSONResponse(
      status_code=HTTP_401_UNAUTHORIZED,
      content={"message": str(exc)})

  @app.exception_handler(Exception)
  async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
      status_code=HTTP_500_INTERNAL_SERVER_ERROR,
      content={"message": "Ocurrió un error inesperado.", "detail": str(exc)})
