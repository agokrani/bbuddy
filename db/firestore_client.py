from __future__ import annotations

import logging
from typing import TYPE_CHECKING, List, Optional, Dict, Any
import firebase_admin
from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from google.cloud.firestore import DocumentReference


class FirestoreClient:
    def __init__(self, collection_name: str, user_id: str = None):
        self.collection_name = collection_name
        self.user_id = user_id
        try:
            firebase_admin.get_app()
        except ValueError as e:
            logger.debug("Initializing Firebase app: %s", e)
            firebase_admin.initialize_app()
        
        self.firestore_client = firestore.Client()
        self.collection = self.firestore_client.collection(
            self.collection_name
        )
    
    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        try:
            doc_ref = self.collection.document(document_id)
            doc = doc_ref.get()
            if doc.exists:
                return {"id": doc.id, **doc.to_dict()}
            else:
                logger.warning("Document %s/%s does not exist.", self.collection_name, document_id)
        except Exception as e:
            logger.error("Error retrieving document: %s", str(e))
        return None
        
    def get_documents(self, where=None) -> List[Dict[str, Any]]:
        try:
            query = self.collection
            if self.user_id is not None:
                query = query.where("user_id", "==", self.user_id)
            if where is not None:
                query = query.where(*where)
            docs = query.stream()
            documents = [{"id": doc.id, **doc.to_dict()} for doc in docs]
            return documents
        except Exception as e:
            logger.error("Error retrieving documents: %s", str(e))
            return []

        
    def set_document(self, data: Dict[str, Any]) -> Optional[str]:
        try:
            doc_ref = self.collection.document()
            doc_ref.set(data)
            
            return doc_ref.id
        except Exception as e:
            logger.error("Error setting document: %s", str(e))
            return None
        

    def update_document(self, document_id: str, data: Dict[str, Any]) -> bool:
        try:
            doc_ref = self.collection.document(document_id)
            doc_ref.update(data)
            
            return True
        except Exception as e:
            logger.error("Error updating document: %s", str(e))
            return False
    
    def delete_document(self, document_id: str) -> bool:
        try:
            doc_ref = self.collection.document(document_id)
            doc_ref.delete()
            return True
        except Exception as e:
            logger.error("Error deleting document: %s", str(e))
            return False