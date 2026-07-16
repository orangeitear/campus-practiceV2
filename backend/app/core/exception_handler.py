from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import BizException
from app.schemas.common import error


async def biz_exception_handler(request: Request, exc: BizException) -> JSONResponse:
    """处理自定义业务异常 BizException"""
    return JSONResponse(
        status_code=exc.code,
        content=error(message=exc.message, code=exc.code)
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """处理参数校验异常 RequestValidationError"""
    errors = []
    for err in exc.errors():
        field = ".".join(str(loc) for loc in err["loc"])
        msg = err["msg"]
        errors.append(f"{field}: {msg}")
    
    message = "; ".join(errors) if errors else "参数校验失败"
    return JSONResponse(
        status_code=400,
        content=error(message=message, code=400)
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """处理 HTTP 异常（如 404、401 等）"""
    return JSONResponse(
        status_code=exc.status_code,
        content=error(message=exc.detail, code=exc.status_code)
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """兜底异常处理器：捕获所有未处理的异常"""
    return JSONResponse(
        status_code=500,
        content=error(message=f"服务器内部错误: {str(exc)}", code=500)
    )