from functools import partial
from typing import Any, Awaitable, Callable, Optional

from fastapi import WebSocket, WebSocketDisconnect
from langchain.chains.base import Chain
from pydantic import BaseModel, Field

from lanarky.callbacks import AsyncLanarkyCallback, get_websocket_callback
from lanarky.schemas import Message, MessageType, Sender, WebsocketResponse
from lanarky.websockets import WebsocketConnection

class CustomWebsocketConnection(WebsocketConnection):
    async def connect(self, accept_connection: bool = True, **kwargs):
        if accept_connection and self.connection_accepted:
            raise RuntimeError("Connection already accepted.")

        if accept_connection:
            """Connect to websocket."""
            await self.websocket.accept()
            self.connection_accepted = True

        # TODO: change this prompt w.r.t memory if there is a chat history
        #await self.chain_executor("Introduce yourself and ask thoughtful question help in achieving this goal.")

        while True:
            try:
                user_message = await self.websocket.receive_text()
                print(user_message)
                await self.websocket.send_json(
                    WebsocketResponse(
                        sender=Sender.HUMAN,
                        message=user_message,
                        message_type=MessageType.STREAM,
                    ).dict()
                )
                await self.websocket.send_json(
                    WebsocketResponse(
                        sender=Sender.BOT,
                        message=Message.NULL,
                        message_type=MessageType.START,
                    ).dict()
                )
                await self.chain_executor(user_message)
                await self.websocket.send_json(
                    WebsocketResponse(
                        sender=Sender.BOT,
                        message=Message.NULL,
                        message_type=MessageType.END,
                    ).dict()
                )
            except WebSocketDisconnect:
                #logger.debug("client disconnected.")
                break
            except Exception as e:
                logger.error(e)
                await self.websocket.send_json(
                    WebsocketResponse(
                        sender=Sender.BOT,
                        message=Message.ERROR,
                        message_type=MessageType.ERROR,
                    ).dict()
                )
