from typing import Any, Dict

from lanarky.register import (
    register_streaming_callback,
    register_streaming_json_callback,
    register_websocket_callback,
)
from lanarky.schemas import StreamingJSONResponse, MessageType

from lanarky.callbacks.base import AsyncLanarkyCallback
from lanarky.callbacks.llm import (
    AsyncLLMChainStreamingCallback,
    AsyncLLMChainStreamingJSONCallback,
    AsyncLLMChainWebsocketCallback,
)
from lanarky.callbacks.agents import AsyncAgentsLanarkyCallback
from langchain.schema import AgentFinish
from langchain.chains.base import Chain
from pydantic import BaseModel, Field


@register_websocket_callback("CutomAgentExecutor")
class CustomAsyncAgentsWebsocketCallback(
    AsyncAgentsLanarkyCallback, AsyncLLMChainWebsocketCallback
):
    """AsyncWebsocketCallback handler for AgentExecutor."""
    agent: Chain = Field(None)

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Run on new LLM token. Only available when streaming is enabled."""
        if self._check_if_answer_reached(token):
            message = self._construct_message(token)
            await self.websocket.send_json(message)
    
    # async def on_agent_finish(self, finish: AgentFinish, **kwargs) -> None:
    #     print(self.agent.__dict__);
    #     message = {**self.response.dict(), **{"message": finish.return_values["output"], "message_type": MessageType.INFO}}
    #     await self.websocket.send_json(message)