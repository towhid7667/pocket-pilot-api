from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.database import Base, engine
from app.controllers.user import router
from app.utils.telegram import send_telegram_message
import traceback

app = FastAPI(
    title="Pocket Pilot API",
    description="API for managing expenses with user authentication",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)
app.include_router(router)
Base.metadata.create_all(bind=engine)

@app.get("/", response_model=dict)
async def root():
    return {"message": "Pocket Pilot API is running"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handles all uncaught exceptions and sends them to Telegram."""
    error_message = (
        f"Exception occurred:\n"
        f"*URL*: {request.url}\n"
        f"*Method*: {request.method}\n"
        f"*Error*: {str(exc)}\n"
        f"*Traceback*: ```\n{traceback.format_exc()}\n```"
    )
    send_telegram_message(error_message)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. The admin has been notified."}
    )