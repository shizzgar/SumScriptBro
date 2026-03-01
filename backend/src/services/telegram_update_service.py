from __future__ import annotations

from dataclasses import dataclass

from fastapi import HTTPException, status

from core.config import Settings
from schemas.telegram import TelegramMediaType, TelegramWebhookAck, TelegramUpdate


@dataclass(slots=True)
class NormalizedMediaRef:
    media_type: TelegramMediaType
    file_id: str
    file_unique_id: str
    file_size: int
    duration: int | None
    storage_object_key: str | None


class TelegramUpdateService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def process(self, update: TelegramUpdate) -> TelegramWebhookAck:
        if update.message is None:
            return TelegramWebhookAck(accepted=True, reason="No message payload")

        command = self._extract_command(update)
        if command is not None:
            return self._route_command(command)

        media = update.message.normalized_media()
        if media is None:
            return TelegramWebhookAck(accepted=False, reason="Unsupported update type")

        self._validate_media_limits(media.file_size, media.duration)

        storage_object_key = None
        if media.file_size >= self._settings.telegram_large_file_threshold_bytes:
            storage_object_key = self._make_storage_object_key(update.update_id, media.file_unique_id)

        normalized_ref = NormalizedMediaRef(
            media_type=media.media_type,
            file_id=media.file_id,
            file_unique_id=media.file_unique_id,
            file_size=media.file_size,
            duration=media.duration,
            storage_object_key=storage_object_key,
        )

        _ = normalized_ref

        return TelegramWebhookAck(
            accepted=True,
            reason="Media accepted for async processing",
            media_type=media.media_type,
            file_size=media.file_size,
            storage_object_key=storage_object_key,
        )

    def _extract_command(self, update: TelegramUpdate) -> str | None:
        message = update.message
        if message is None or message.text is None:
            return None

        text = message.text.strip()
        if not text.startswith("/"):
            return None

        command = text.split(maxsplit=1)[0].split("@", maxsplit=1)[0].lower()
        return command

    def _route_command(self, command: str) -> TelegramWebhookAck:
        command_handlers = {
            "/start": "Welcome! Send voice/audio/video/document and I will transcribe and summarize it.",
            "/help": "Available commands: /start, /help, /transcribe, /summarize.",
            "/transcribe": "Send media after /transcribe to start transcript pipeline.",
            "/summarize": "Send /summarize with your preferences after transcript is ready.",
        }
        if command not in command_handlers:
            return TelegramWebhookAck(accepted=False, reason="Unsupported command", command=command)

        return TelegramWebhookAck(accepted=True, reason=command_handlers[command], command=command)

    def _validate_media_limits(self, file_size: int, duration: int | None) -> None:
        if file_size > self._settings.telegram_max_media_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Media file exceeds size limit",
            )

        if duration is not None and duration > self._settings.telegram_max_media_duration_seconds:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Media duration exceeds limit",
            )

    @staticmethod
    def _make_storage_object_key(update_id: int, file_unique_id: str) -> str:
        return f"telegram/{update_id}/{file_unique_id}"
