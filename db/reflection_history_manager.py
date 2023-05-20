import json
import logging
from typing import List
from db.manager import DatabaseManager
from schema.reflection import ReflectionPerTopic, reflection_to_dict, reflections_from_dict
import psycopg
from psycopg import sql
from psycopg.rows import dict_row

logger = logging.getLogger(__name__)

class ReflectionHistoryManager: 
    def __init__(
        self, 
        session_id: str, 
        table_name: str = "reflection_store"
    ): 
        self.session_id = session_id
        self.table_name = table_name

        #self._create_table_if_not_exists()

    def _create_table_if_not_exists(self, db):
        cursor = db.cursor(row_factory=dict_row)
        create_table_query = f"""CREATE TABLE IF NOT EXISTS {self.table_name} (
            id SERIAL PRIMARY KEY,
            session_id TEXT NOT NULL,
            reflection JSONB NOT NULL,
            create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );"""
        cursor.execute(create_table_query)
        db.commit()
    
    def reflection_history(self, db):
        cursor = db.cursor(row_factory=dict_row) 
        query = f"SELECT reflection FROM {self.table_name} where session_id = %s order by create_time desc;"
        cursor.execute(query, (self.session_id,))
        
        items = [record["reflection"] for record in cursor.fetchall()]
        
        reflection_history = reflections_from_dict(items)
        
        return reflection_history

    def add_reflection(self, db, reflection_to_add: List[ReflectionPerTopic]): 
        self.append(db, reflection_to_add)

    def append(self, db, reflection_to_add: List[ReflectionPerTopic]) -> None:
        """Append the reflection to the record in PostgreSQL"""
        cursor = db.cursor(row_factory=dict_row)
        query = sql.SQL("INSERT INTO {} (session_id, reflection) VALUES (%s, %s);").format(
            sql.Identifier(self.table_name)
        )
        cursor.execute(
            query, (self.session_id, json.dumps(reflection_to_dict(reflection_to_add)))
        )
        db.commit()