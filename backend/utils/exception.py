from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError


logger = logging.getLogger(__name__)


def _error_response(status_code: int, message: str, data: Any = None) -> JSONResponse:
    """统一异常响应结构。"""
    content = {
        "code": status_code,
        "message": message,
        "data": data,
    }
    return JSONResponse(status_code=status_code, content=jsonable_encoder(content))


def _extract_validation_errors(exc: RequestValidationError | ValidationError) -> list[dict[str, Any]]:
    """提取校验错误详情，便于前端定位字段问题。"""
    errors: list[dict[str, Any]] = []
    for error in exc.errors():
        errors.append(
            {
                "field": ".".join(str(item) for item in error.get("loc", [])),
                "message": error.get("msg", "参数校验失败"),
                "type": error.get("type", "validation_error"),
            }
        )
    return errors


def register_exception_handlers(app: FastAPI) -> FastAPI:
    """为 FastAPI 应用注册全局异常处理器。"""

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
        detail = exc.detail if isinstance(exc.detail, str) else "请求处理失败"
        data = None if isinstance(exc.detail, str) else exc.detail
        return _error_response(exc.status_code, detail, data)

    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(
        _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return _error_response(422, "请求参数校验失败", _extract_validation_errors(exc))

    @app.exception_handler(ValidationError)
    async def validation_exception_handler(_: Request, exc: ValidationError) -> JSONResponse:
        return _error_response(422, "数据校验失败", _extract_validation_errors(exc))

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(_: Request, exc: SQLAlchemyError) -> JSONResponse:
        logger.exception("数据库操作异常: %s", exc)
        return _error_response(500, "数据库操作失败")

    @app.exception_handler(Exception)
    async def global_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("未处理异常: %s", exc)
        return _error_response(500, "服务器内部错误")

    return app


__all__ = ["register_exception_handlers"]
