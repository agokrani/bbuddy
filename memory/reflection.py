import json
import logging
from typing import List
from schema import ReflectionPerTopic, reflection_to_dict, reflections_from_dict

logger = logging.getLogger(__name__)

DEFAULT_CONNECTION_STRING = "postgresql://postgres:mypassword@localhost/chat_history"

class ReflectionHistory: 
    def __init__(
        self, 
        session_id: str, 
        connection_string = DEFAULT_CONNECTION_STRING,
        table_name: str = "reflection_store"
    ): 
        import psycopg
        from psycopg.rows import dict_row

        try:
            self.connection = psycopg.connect(connection_string)
            self.cursor = self.connection.cursor(row_factory=dict_row)
        except psycopg.OperationalError as error:
            logger.error(error)

        self.session_id = session_id
        self.table_name = table_name

        self._create_table_if_not_exists()

    def _create_table_if_not_exists(self) -> None:
        create_table_query = f"""CREATE TABLE IF NOT EXISTS {self.table_name} (
            id SERIAL PRIMARY KEY,
            session_id TEXT NOT NULL,
            reflection JSONB NOT NULL,
            create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );"""
        self.cursor.execute(create_table_query)
        self.connection.commit()
    
    @property
    def reflection_history(self): 
        query = f"SELECT reflection FROM {self.table_name} where session_id = %s order by create_time desc;"
        self.cursor.execute(query, (self.session_id,))
        
        items = [record["reflection"] for record in self.cursor.fetchall()]
        
        reflection_history = reflections_from_dict(items)
        
        return reflection_history

    def add_reflection(self, reflection_to_add: List[ReflectionPerTopic]): 
        self.append(reflection_to_add)

    def append(self, reflection_to_add: List[ReflectionPerTopic]) -> None:
        """Append the reflection to the record in PostgreSQL"""
        from psycopg import sql

        query = sql.SQL("INSERT INTO {} (session_id, reflection) VALUES (%s, %s);").format(
            sql.Identifier(self.table_name)
        )
        self.cursor.execute(
            query, (self.session_id, json.dumps(reflection_to_dict(reflection_to_add)))
        )
        self.connection.commit()

    