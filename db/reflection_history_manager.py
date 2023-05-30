import json
import logging
import datetime
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
    
    # def reflection_history(self, db, start_date=None, end_date=None):
    #     cursor = db.cursor(row_factory=dict_row) 
    #     if start_date is not None and end_date is not None: 
    #         query = f"SELECT reflection FROM {self.table_name} WHERE session_id = %s AND create_time BETWEEN %s AND %s ORDER BY create_time DESC;"
    #         cursor.execute(query, (self.session_id, start_date, end_date))
    #     else: 
    #         query = f"SELECT reflection FROM {self.table_name} where session_id = %s order by create_time desc;"
    #         cursor.execute(query, (self.session_id,))
        
    #     items = [record["reflection"] for record in cursor.fetchall()]
        
    #     reflection_history = reflections_from_dict(items)
        
    #     return reflection_history


    def reflection_history(self, db, start_date=None, end_date=None):
        cursor = db.cursor(row_factory=dict_row)
        #print("start_date: ", start_date)
        #print("end_date: ", end_date)
        #import pdb; pdb.set_trace()
        if (start_date is not None and start_date != '') and (end_date is not None and end_date != ''):
            # Extract date and time components from the start_date and end_date strings
            start_date_str, start_time_str = start_date.split("T")
            end_date_str, end_time_str = end_date.split("T")
        
            # Combine date and time components into a single string
            start_datetime_str = f"{start_date_str} {start_time_str[:-5]}"
            end_datetime_str = f"{end_date_str} {end_time_str[:-5]}"
        
            # Convert combined strings to datetime objects
            start_datetime = datetime.datetime.strptime(start_datetime_str, "%Y-%m-%d %H:%M:%S")
            end_datetime = datetime.datetime.strptime(end_datetime_str, "%Y-%m-%d %H:%M:%S")
            
            query = f"SELECT reflection FROM {self.table_name} WHERE session_id = %s AND create_time BETWEEN %s AND %s ORDER BY create_time DESC;"
            cursor.execute(query, (self.session_id, start_datetime, end_datetime))
        else:
            query = f"SELECT reflection FROM {self.table_name} WHERE session_id = %s ORDER BY create_time DESC;"
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