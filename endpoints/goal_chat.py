from fastapi import APIRouter, WebSocket, Depends
from custom_websockets.custom import CustomWebsocketConnection
from db.goal_history_manager import GoalHistoryManager
from deps import get_db, connection_string
from db.goal_chat_history_manager import GoalChatHistoryManager
from langchain.schema import _message_from_dict, messages_to_dict
from endpoints import login
from agents import GoalConversationAgent
from lanarky.callbacks import AsyncLLMChainWebsocketCallback

langchain_router = APIRouter()


@langchain_router.websocket("/ws/{goal_id}")
async def goal_chat_endpoint(goal_id: int, websocket: WebSocket, db=Depends(get_db)):
    
    goal = GoalHistoryManager.get_goal_by_id(db, goal_id)
    chain = GoalConversationAgent().get_agent(goal, connection_string)
    
    connection = CustomWebsocketConnection.from_chain(chain=chain, websocket=websocket, callback=AsyncLLMChainWebsocketCallback)
    await connection.connect()


@langchain_router.post("/message_id/{goal_id}")
async def get_id_from_db(goal_id: int, data: dict): 
        manager = GoalChatHistoryManager(
                        session_id=str(goal_id),
                        connection_string=connection_string
                )
        
        return manager.get_message_id(_message_from_dict(data))


@langchain_router.get("/chat_history/{goal_id}")
# async def get_chat_history(goal_id: int, page: int, page_size: int):
#     manager = GoalChatHistoryManager(
#         session_id=str(goal_id),
#         connection_string=connection_string
#     )

#     # Get all messages from the manager
#     all_messages = manager.messages
    
#     # Reverse the order of messages (descending order)
#     all_messages = all_messages[::-1]

#     # Calculate the total number of messages
#     total_messages = len(all_messages)

#     # Calculate the start and end indices for the requested page
#     start_index = (page - 1) * page_size
#     end_index = start_index + page_size

#     # Check if the end index exceeds the total number of messages
#     if end_index > total_messages:
#         # Adjust the end index to the last available message
#         end_index = total_messages

#     # Get the subset of messages for the requested page
#     page_messages = all_messages[start_index:end_index]

#     return messages_to_dict(page_messages)
async def get_chat_history(goal_id: int, page: int, page_size: int):
    manager = GoalChatHistoryManager(
        session_id=str(goal_id),
        connection_string=connection_string
    )

    async def chat_message_generator():
        all_messages = manager.messages[::-1]
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

