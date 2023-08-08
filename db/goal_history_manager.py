import json
import logging
from typing import List
from db.manager import DatabaseManager
import psycopg
from psycopg import sql
from psycopg.rows import dict_row
from schema.goal import Goal, goals_from_dict, goal_to_dict, goal_from_dict

logger = logging.getLogger(__name__)


class GoalHistoryManager: 
    def __init__(
        self, 
        session_id: str, 
        table_name: str = "goal_store"
    ): 
        self.session_id = session_id
        self.table_name = table_name

        #self._create_table_if_not_exists()

    def _create_table_if_not_exists(self, db):
        cursor = db.cursor(row_factory=dict_row)
        create_table_query = f"""CREATE TABLE IF NOT EXISTS {self.table_name} (
            id SERIAL PRIMARY KEY,
            session_id TEXT NOT NULL,
            goal JSONB NOT NULL,
            create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );"""
        cursor.execute(create_table_query)
        db.commit()

    def goal_history(self, db):
        cursor = db.cursor(row_factory=dict_row) 
        query = f"SELECT id, goal, create_time FROM {self.table_name} where session_id = %s order by create_time desc;"
        cursor.execute(query, (self.session_id,))
        
        goal_history = goals_from_dict(cursor.fetchall())
        
        return goal_history

    def add_goal(self, db, goal_to_add: Goal): 
        return self.append(db, goal_to_add)

    def append(self, db, goal_to_add: Goal) -> None:
        """Append the reflection to the record in PostgreSQL"""
        cursor = db.cursor(row_factory=dict_row)
        query = sql.SQL("INSERT INTO {} (session_id, goal) VALUES (%s, %s);").format(
            sql.Identifier(self.table_name)
        )
        cursor.execute(
            query, (self.session_id, json.dumps(goal_to_dict(goal_to_add)))
        )
        cursor.execute('SELECT LASTVAL()')
        gid = cursor.fetchone()['lastval']
        
        db.commit()
        
        return gid

    @classmethod
    def get_goal_by_id(cls, db, id:int): 
        cursor = db.cursor(row_factory=dict_row) 
        query = f"SELECT id, goal, create_time FROM goal_store where id = %s;"
        cursor.execute(query, (id,))
        
        goal = goal_from_dict(cursor.fetchone())
        
        return goal
    

    def update_goal(self, db, goal_to_update): 
        goal_type = None
        try:
            goal_type = goal_to_update["type"]
        except: 
            goal_type = "generated"

        cursor = db.cursor()
        query = f"UPDATE {self.table_name} SET goal = %s WHERE  id = %s;"
        cursor.execute(query, (json.dumps({"description": goal_to_update["description"], "type": goal_type, "milestones": goal_to_update["milestones"]}), 
                               goal_to_update["id"],))
        
        db.commit()

    def delete_goal(self, db, id:int):
        cursor = db.cursor()
        
        query = f"DELETE FROM {self.table_name} WHERE id = %s;"
        cursor.execute(query, (id,))

        db.commit()
