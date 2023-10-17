from fastapi import APIRouter, WebSocket
from custom_websockets.custom import CustomWebsocketConnection
from langchain.memory.chat_message_histories import FirestoreChatMessageHistory
from agents import GoalConversationAgent
from lanarky.callbacks import AsyncLLMChainWebsocketCallback
from langchain.schema import messages_to_dict
from fastapi import Query
from endpoints import login
from goals import goal_agent
langchain_router = APIRouter()


@langchain_router.websocket("/ws/{goal_id}")
async def goal_chat_endpoint(goal_id: str, websocket: WebSocket, authorization: str = Query(..., alias="authorization")):
    user_id = login.get_firebase_user(token=authorization)
    goal = goal_agent.get_by_id(goal_id=goal_id)
    chain = GoalConversationAgent().get_agent(goal, user_id=user_id)
    
    connection = CustomWebsocketConnection.from_chain(chain=chain, websocket=websocket, callback=AsyncLLMChainWebsocketCallback)
    await connection.connect()


@langchain_router.get("/chat_history/{goal_id}")
async def get_chat_history(goal_id: str, page: int, page_size: int):

    history = FirestoreChatMessageHistory(session_id=str(goal_id), user_id=str(goal_id), collection_name="test_store")

    async def chat_message_generator():
       all_messages = history.messages[::-1]
       total_messages = len(all_messages)  
       start_index = (page - 1) * page_size  
       end_index = start_index + page_size

       if end_index > total_messages:
               # Adjust the end index to the last available message
               end_index = total_messages


       for message in all_messages[start_index:end_index]:
          yield message
    messages = []
    async for message in chat_message_generator():  
       messages.append(message)
    return messages_to_dict(messages)