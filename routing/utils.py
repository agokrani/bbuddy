from fastapi import Depends, WebSocket, params
from deps import get_db


def create_db_dependency() -> params.Depends:
    
    #@lru_cache(maxsize=1)
    #def dependency() -> Chain:
    #    return langchain_object

    return Depends(get_db)