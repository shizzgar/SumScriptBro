from fastapi import APIRouter, Depends, Header, HTTPException, status

from core.config import Settings, get_settings
from schemas.telegram import TelegramUpdate, TelegramWebhookAck
from services.telegram_update_service import TelegramUpdateService

router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.post("/webhook", response_model=TelegramWebhookAck, status_code=status.HTTP_202_ACCEPTED)
async def telegram_webhook(
    update: TelegramUpdate,
    settings: Settings = Depends(get_settings),
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
) -> TelegramWebhookAck:
    if settings.telegram_webhook_secret and (
        x_telegram_bot_api_secret_token != settings.telegram_webhook_secret
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook secret")

    service = TelegramUpdateService(settings=settings)
    return service.process(update)
