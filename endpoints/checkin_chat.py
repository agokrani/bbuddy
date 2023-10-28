from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from lanarky.schemas import Message, MessageType, Sender, WebsocketResponse
from fastapi import Query
from langchain import ConversationChain, LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from custom_websockets.custom import CheckinWebsocketConnection
from endpoints import login
from checkins import generative_check_in
from lanarky.callbacks.llm import AsyncLLMChainWebsocketCallback
checkin_router = APIRouter()

def create_chain():
    # return ConversationChain(
    #     llm=ChatOpenAI(
    #         temperature=0,
    #         streaming=True,
    #         callbacks=[StreamingStdOutCallbackHandler()]
    #     ),
    #     verbose=True,
    # )
    template = """Tell me a {adjective} joke about {subject}."""
    prompt = PromptTemplate(template=template, input_variables=["adjective", "subject"])
    llm_chain = LLMChain(prompt=prompt, llm=ChatOpenAI(
            temperature=0,
            streaming=True,
            callbacks=[StreamingStdOutCallbackHandler()]
        ))
    return llm_chain
chain = create_chain()

@checkin_router.websocket("/checkin")
async def checkin_chat_endpoint(websocket: WebSocket, authorization: str = Query(..., alias="authorization")): 
    user_id = login.get_firebase_user(token=authorization)
    
    connection = CheckinWebsocketConnection.from_chain(chain=generative_check_in.chain(), websocket=websocket, callback=AsyncLLMChainWebsocketCallback)
    
    await connection.connect(json2query = generative_check_in.get_query)
    