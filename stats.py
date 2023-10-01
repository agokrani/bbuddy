from psycopg.rows import dict_row
from db.firestore_client import FirestoreClient
from schema.stats import StatsType, UserStats, user_stats_from_list

class StatsManager:
    collection_name = "user_stats"

    def __init__(self, table_name="user_stats"):
        self.table_name = table_name
    
    def get_stats(self, user_id: str): 
        client = FirestoreClient(collection_name=self.collection_name, user_id=user_id)
        stats = client.get_documents()
        if len(stats) > 0: 
            return user_stats_from_list(stats)
        else: 
            return self.store(user_id)
    
    def store(self, user_id: str): 
        client = FirestoreClient(collection_name=self.collection_name)
        stats_to_insert = []
        for stat_type in StatsType: 
            stat = {
                "user_id": user_id,
                "type": stat_type,
                "value": "0"
            }
            client.set_document(stat)
            stats_to_insert(stat)
        return stats_to_insert
    
    
    def update(self, stat, user_id:str):
        client = FirestoreClient(collection_name=self.collection_name, user_id=user_id)
        docs = client.get_documents(where=("type", "==", stat.type))
        
        if len(docs) > 1: 
            raise Exception("Unable to fetch the document. More than one document for the type")
        doc = docs[0]
        client.update_document(document_id=doc["id"], data={
            "value": stat.value
        })
stats_manager = StatsManager();