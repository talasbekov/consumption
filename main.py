import time
import socket
import logging

# import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.logger import logger as log
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException, JWTDecodeError
from pydantic import ValidationError

from api import router
from core import configs
from services import auth_service

# from ws import notification_manager


# Настройка логирования
logg = logging.getLogger(__name__)

socket.setdefaulttimeout(15)  # TODO: change to configs.SOCKET_TIMEOUT

app = FastAPI(
    title=configs.PROJECT_NAME,
    description=configs.DESCRIPTION,
    version=configs.VERSION,
    openapi_url=f"{configs.API_V1_PREFIX}/openapi.json",
    debug=configs.DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: change to configs.ALLOWED_HOSTS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# sqlalchemy
# app.add_middleware(
#     DebugToolbarMiddleware,
#     panels=[
#         "debug_toolbar.panels.versions.VersionsPanel",
#         "debug_toolbar.panels.timer.TimerPanel",
#         "debug_toolbar.panels.settings.SettingsPanel",
#         "debug_toolbar.panels.headers.HeadersPanel",
#         "debug_toolbar.panels.request.RequestPanel",
#         "debug_toolbar.panels.sqlalchemy.SQLAlchemyPanel",
#     ],
# )

app.include_router(router)

# if configs.SENTRY_ENABLED:
#     sentry_sdk.init(dsn=configs.SENTRY_DSN, traces_sample_rate=1.0)
app.mount("/media", StaticFiles(directory="media"), name="media")
app.mount("/static", StaticFiles(directory="static"), name="static")


@AuthJWT.load_config
def get_config():
    return configs


# Middleware для добавления времени обработки и данных пользователя
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    logg.debug(f"Request: {request.method} {request.url} {request.client.host}")
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    # Проверяем, что ответ является HTMLResponse и нужно добавить информацию о пользователе
    if isinstance(response, HTMLResponse):
        try:
            # Имитация получения данных пользователя
            user_data = (
                auth_service.get_current_user()
            )  # Здесь предполагается синхронный вызов для примера
            # В реальности может потребоваться асинхронный вызов с await
            # Добавляем данные пользователя в контекст шаблона
            new_content = configs.templates.TemplateResponse(
                "base.html",
                {"request": request, **user_data, "content": response.body.decode()},
            )
            response.body = new_content.body
            response.headers.update(new_content.headers)
        except Exception as e:
            log.error(f"Error adding user data to the response: {e}")

    return response


@app.exception_handler(ValidationError)
def validation_error_handler(request: Request, exc: ValidationError):
    return JSONResponse(status_code=400, content={"detail": exc.json()})


@app.exception_handler(JWTDecodeError)
def jwt_decode_error_handler(request: Request, exc: JWTDecodeError):
    return JSONResponse(status_code=401, content={"detail": exc.message})


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url="/api/client/auth")


# @app.websocket("/ws")
# async def websocket_endpoint(
#     websocket: WebSocket,
#     token: str = Query(...),
#     Authorize: AuthJWT = Depends(),
# ):
#     try:
#         Authorize.jwt_required("websocket", token=token)
#         user_id = Authorize.get_jwt_subject()
#         if user_id is None:
#             raise AuthJWTException()
#     except AuthJWTException:
#         await websocket.close()
#
#     await notification_manager.connect(websocket, user_id)
#     try:
#         while True:
#             await websocket.receive_text()
#     except WebSocketDisconnect:
#         notification_manager.disconnect(user_id, websocket)
