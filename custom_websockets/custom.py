import asyncio
from functools import partial
from typing import Any, Awaitable, Callable, Optional

from fastapi import WebSocket, WebSocketDisconnect, BackgroundTasks
from concurrent.futures import ThreadPoolExecutor
from langchain.chains.base import Chain
from pydantic import BaseModel, Field

from lanarky.callbacks import AsyncLanarkyCallback, get_websocket_callback
from lanarky.schemas import Message, MessageType, Sender, WebsocketResponse
from lanarky.websockets import WebsocketConnection
from db.vector_store_client import vClient
import logging 

logger = logging.getLogger(__name__)
executor = ThreadPoolExecutor()


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
                #logger.error(e)
                await self.websocket.send_json(
                    WebsocketResponse(
                        sender=Sender.BOT,
                        message=Message.ERROR,
                        message_type=MessageType.ERROR,
                    ).dict()
                )


class CheckinWebsocketConnection(WebsocketConnection):
    async def connect(self, accept_connection: bool = True, **kwargs):
        if accept_connection and self.connection_accepted:
            raise RuntimeError("Connection already accepted.")

        if accept_connection:
            """Connect to websocket."""
            await self.websocket.accept()
            self.connection_accepted = True

        # TODO: change this prompt w.r.t memory if there is a chat history
        def run_blocking_code(user_message):
            vDb = vClient.get_db()
            context = vDb.query(input_query=user_message, n_results=1, where=None, skip_embedding=False)
            return context

        while True:
            try:
                input_json = await self.websocket.receive_json()
                json2query = kwargs["json2query"]
                user_message = json2query(input_json['feeling'], input_json['feeling_form'], input_json['reason_entity'], input_json['reason'])
                
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
                
                
                context = await asyncio.to_thread(run_blocking_code,user_message)
                await self.chain_executor({"query": user_message, "context": context})
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

    @staticmethod
    def _create_chain_executor(
        chain: Chain,
        websocket: WebSocket,
        response: WebsocketResponse,
        callback: Optional[AsyncLanarkyCallback] = None,
        **callback_kwargs,
    ) -> Callable[[str], Awaitable[Any]]:
        """Creates a function to execute ``chain.acall()``.

        Args:
            chain: langchain chain instance.
            websocket: websocket instance.
            response: WebsocketResponse instance.
            callback_kwargs: keyword arguments fchainor callback function.
        """
        if callback is None:
            callback = partial(get_websocket_callback, chain)

        async def wrapper(user_message: dict):
            return await chain.acall(
                inputs=user_message,
                callbacks=[
                    callback(
                        websocket=websocket,
                        response=response,
                        **callback_kwargs,
                    )
                ],
            )

        return wrapper