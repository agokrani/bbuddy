from langchain.memory import PostgresChatMessageHistory
from typing import List
from langchain.schema import BaseMessage
from schema.message import messages_from_dict


DEFAULT_CONNECTION_STRING = "postgresql://postgres:mypassword@localhost/chat_history"


class GoalChatHistoryManager(PostgresChatMessageHistory): 
    def __init__(
        self,
        session_id: str,
        connection_string: str = DEFAULT_CONNECTION_STRING,
        table_name: str = "test_store",
    ):
        super().__init__(session_id, connection_string, table_name)

    def get_message_id(self, message: BaseMessage): 
        query = (
            f"SELECT id FROM {self.table_name} WHERE (message->'data'->>'content') = %s ORDER BY id desc;"
        )
        self.cursor.execute(query, (message.content,))
        message_id = self.cursor.fetchone()
        
        return message_id
    
    @property
    def messages(self) -> List[BaseMessage]:  # type: ignore
        """Retrieve the messages from PostgreSQL"""
        query = (
            f"SELECT message FROM {self.table_name} WHERE session_id = %s ORDER BY id;"
        )
        self.cursor.execute(query, (self.session_id,))
        items = [record["message"] for record in self.cursor.fetchall()]
        
        messages = messages_from_dict(items)

        return messages
