from lanarky import LangchainRouter
from fastapi import Depends
from fastapi import WebSocket
from urllib.parse import urlparse
from db.goal_history_manager import GoalHistoryManager
from deps import get_db
from routing.utils import create_db_dependency

class CustomLangchainRouter(LangchainRouter): 
    def add_langchain_api_websocket_route(self, url: str): 
        parsed_url = urlparse(url)
        path_segments = parsed_url.path.split('/')
        goal_id = None
        
        if len(path_segments) >= 3:
            goal_id = int(path_segments[2])
        else:
            pass
            #raise WebSocketError("Goal ID not found in the URL")
        db_generator = get_db()
        db = next(db_generator)

        goal = GoalHistoryManager.get_goal_by_id(db, goal_id)


        agent_executor = GoalConversationalAgent().get_agent(goal)

        super().add_langchain_api_websocket_route(url, agent_executor)

