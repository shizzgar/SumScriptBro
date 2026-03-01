from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TelegramChat(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    type: str


class TelegramUser(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    is_bot: bool = False
    first_name: str | None = None
    username: str | None = None


class TelegramMediaType(StrEnum):
    VOICE = "voice"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"


class TelegramMedia(BaseModel):
    model_config = ConfigDict(extra="ignore")

    media_type: TelegramMediaType
    file_id: str
    file_unique_id: str
    duration: int | None = None
    file_name: str | None = None
    mime_type: str | None = None
    file_size: int = 0


class TelegramMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")

    message_id: int
    date: int
    text: str | None = None
    from_user: TelegramUser | None = Field(default=None, alias="from")
    chat: TelegramChat

    voice: dict[str, object] | None = None
    audio: dict[str, object] | None = None
    video: dict[str, object] | None = None
    document: dict[str, object] | None = None

    @model_validator(mode="after")
    def single_media_type(self) -> TelegramMessage:
        media_count = sum(
            media is not None for media in (self.voice, self.audio, self.video, self.document)
        )
        if media_count > 1:
            raise ValueError("Message contains more than one media payload")
        return self

    def normalized_media(self) -> TelegramMedia | None:
        payloads: list[tuple[TelegramMediaType, dict[str, object] | None]] = [
            (TelegramMediaType.VOICE, self.voice),
            (TelegramMediaType.AUDIO, self.audio),
            (TelegramMediaType.VIDEO, self.video),
            (TelegramMediaType.DOCUMENT, self.document),
        ]

        for media_type, payload in payloads:
            if payload is None:
                continue

            return TelegramMedia(
                media_type=media_type,
                file_id=str(payload.get("file_id", "")),
                file_unique_id=str(payload.get("file_unique_id", "")),
                duration=_to_int(payload.get("duration")),
                file_name=_to_str(payload.get("file_name")),
                mime_type=_to_str(payload.get("mime_type")),
                file_size=max(0, _to_int(payload.get("file_size"))),
            )

        return None


class TelegramUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    update_id: int
    message: TelegramMessage | None = None


class TelegramWebhookAck(BaseModel):
    accepted: bool
    reason: str
    command: str | None = None
    media_type: TelegramMediaType | None = None
    file_size: int | None = None
    storage_object_key: str | None = None


def _to_int(value: object | None) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return 0


def _to_str(value: object | None) -> str | None:
    return value if isinstance(value, str) else None
