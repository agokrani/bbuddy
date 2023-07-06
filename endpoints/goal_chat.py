import datetime
from fastapi import APIRouter, WebSocket, Depends
from langchain import ConversationChain
from lanarky import LangchainRouter
from lanarky.routing.utils import create_langchain_dependency, create_langchain_websocket_endpoint
from lanarky.websockets.base import WebsocketConnection
from routing.custom_langchain import CustomLangchainRouter
from schema.goal import Goal, Milestone, GoalInDB
from db.goal_history_manager import GoalHistoryManager
from deps import get_db, connection_string
from langchain.agents import AgentExecutor
from agents.goal_chat.base import GoalConversationalAgent
from callbacks.agents import CustomAsyncAgentsWebsocketCallback
from db.goal_chat_history_manager import GoalChatHistoryManager
from langchain.schema import _message_from_dict
from custom_websockets import CustomWebsocketConnection

langchain_router = APIRouter()

@langchain_router.websocket("/ws/{goal_id}")
async def goal_chat_endpoint(goal_id: int, websocket: WebSocket, db=Depends(get_db)):
    
    goal = GoalHistoryManager.get_goal_by_id(db, goal_id) 
    
    agent_executor = GoalConversationalAgent().get_agent(goal, connection_string)
        
    connection = CustomWebsocketConnection.from_chain(
            chain=agent_executor, websocket=websocket, callback=CustomAsyncAgentsWebsocketCallback, callback_kwargs={"agent": agent_executor}
    )
    await connection.connect()

@langchain_router.post("/message_id/{goal_id}")
async def get_id_from_db(goal_id: int, data: dict): 
        manager = GoalChatHistoryManager(
                        session_id=str(goal_id),
                        connection_string=connection_string
                )
        
        return manager.get_message_id(_message_from_dict(data))

