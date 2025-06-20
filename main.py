import time
import socket
import logging

# import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.logger import logger as log
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from pydantic import ValidationError

from api import router as main_api_router
from api.v1 import secondment as secondment_api
from api.v1 import report as report_api # Import the new report module
from core import configs
from services import get_current_user

# Настройка логирования
logg = logging.getLogger(__name__)

socket.setdefaulttimeout(15)  # TODO: change to configs.SOCKET_TIMEOUT

app = FastAPI(
    title=configs.PROJECT_NAME,
    description=configs.DESCRIPTION,
    version=configs.VERSION,
    openapi_url=f"{configs.API_V1_PREFIX}/openapi.json",
    debug=configs.DEBUG,
    docs_url=None,
    redoc_url=None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: change to configs.ALLOWED_HOSTS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(main_api_router)
app.include_router(secondment_api.router)
app.include_router(report_api.router) # Include new report router

# if configs.SENTRY_ENABLED:
#     sentry_sdk.init(dsn=configs.SENTRY_DSN, traces_sample_rate=1.0)
app.mount("/media", StaticFiles(directory="media"), name="media")
app.mount("/static", StaticFiles(directory="static"), name="static")


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
                get_current_user()
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

@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url="/api/v1/auth2/login")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="Custom Swagger UI",
        swagger_js_url="/static/swagger-ui/dist/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui/dist/swagger-ui.css",
    )
