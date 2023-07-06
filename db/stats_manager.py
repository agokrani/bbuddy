from psycopg.rows import dict_row
from schema.stats import StatsType, UserStats, user_stats_from_list
class StatsManager: 
    def __init__(self, table_name="user_stats"):
        self.table_name = table_name

    def get_counters(self, db, id: int):
        cursor = db.cursor()

        query = f"SELECT * FROM {self.table_name} WHERE id = %s;"
        cursor.execute(query, (id,))

        counter_stats = cursor.fetchall()
        if len(counter_stats) > 0:
           return user_stats_from_list(counter_stats)
        else:
            return self.insert_stats(db, id)

    def insert_stats(self, db, id: int):
        cursor = db.cursor()

        stats_to_insert = [
            UserStats(id=id, type=stat_type, value="0") for stat_type in StatsType
        ]
        query = f"INSERT INTO {self.table_name} (id, type, value) VALUES (%s, %s, %s);"
        cursor.executemany(query, [(stat.id, stat.type, stat.value) for stat in stats_to_insert])

        db.commit()
        
        return stats_to_insert

    def update_stats(self, stat, db, id:int): 
        cursor = db.cursor()
        
        query = f"UPDATE {self.table_name} SET value = %s WHERE  id = %s AND type = %s;"
        cursor.execute(query, (stat.value, id, stat.type))
        
        db.commit() 

stats_manager = StatsManager();