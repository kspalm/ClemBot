import typing as t
from datetime import datetime

from bot.api.api_client import ApiClient
from bot.api.base_route import BaseRoute
from bot.models.message_models import Message, SingleBatchMessage, SingleBatchMessageEdit


class MessageRoute(BaseRoute):
    def __init__(self, api_client: ApiClient):
        super().__init__(api_client)

    async def create_message(
        self,
        message_id: int,
        content: str,
        guild_id: int,
        author_id: int,
        channel_id: int,
        time: datetime,
        **kwargs: t.Any,
    ) -> None:
        json = {
            "Messages": [
                {
                    "Id": message_id,
                    "Content": content,
                    "GuildId": guild_id,
                    "UserId": author_id,
                    "ChannelId": channel_id,
                    "Time": time.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                }
            ]
        }

        await self._client.post("bot/messages", data=json, **kwargs)

    async def batch_create_message(
        self, messages: list[SingleBatchMessage], **kwargs: t.Any
    ) -> None:
        json = {
            "Messages": [
                {
                    "Id": m.id,
                    "Content": m.content,
                    "GuildId": m.guild,
                    "UserId": m.author,
                    "ChannelId": m.channel,
                    "Time": m.time.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                }
                for m in messages
            ]
        }

        await self._client.post("bot/messages", data=json, **kwargs)

    async def edit_message(self, message_id: int, content: str) -> None:
        json = {
            "Messages": [
                {
                    "Id": message_id,
                    "Content": content,
                }
            ]
        }

        await self._client.patch("bot/messages", data=json)

    async def batch_edit_message(
        self, messages: list[SingleBatchMessageEdit], **kwargs: t.Any
    ) -> None:
        json = {
            "Messages": [
                {"Id": m.id, "Content": m.content, "Time": m.time.strftime("%Y-%m-%dT%H:%M:%S.%f")}
                for m in messages
            ]
        }

        await self._client.patch("bot/messages", data=json, **kwargs)

    async def get_message(self, message_id: int) -> Message | None:
        resp = await self._client.get(f"bot/messages/{message_id}")

        if not resp:
            return None

        return Message(**resp)

    async def range_count_messages(self, user_id: int, guild_id: int, days: int) -> int:
        json = {"UserId": user_id, "GuildId": guild_id, "Days": days}
        resp = await self._client.get("bot/messages/Count", data=json)

        if not resp:
            return 0

        return t.cast(int, resp["messageCount"])
