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
    # await websocket.accept()
    # while True:
    #     try:
    #         user_message = await websocket.receive_text()
    #         await websocket.send_json(
    #             WebsocketResponse(
    #                 sender=Sender.HUMAN,
    #                 message=user_message,
    #                 message_type=MessageType.STREAM,
    #             ).dict()
    #         )
    #         await websocket.send_json(
    #             WebsocketResponse(
    #                 sender=Sender.BOT,
    #                 message=Message.NULL,
    #                 message_type=MessageType.START,
    #             ).dict()
    #         )
    #         print('here1')
    #         await chain.acall(
    #             inputs=user_message,
    #             callbacks=[
    #                 AsyncLLMChainWebsocketCallback(
    #                     websocket=websocket,
    #                     response=WebsocketResponse(
    #                         sender=Sender.BOT,
    #                         message=Message.NULL,
    #                         MessageType=MessageType.STREAM
    #                     ),
    #                 )
    #             ],
    #         )
            
    #         #await generative_check_in.get_response('Anxious', 'Stressed', 'work')
    #         # await websocket.send_json(WebsocketResponse(
    #         #     sender=Sender.BOT,
    #         #     message=Message.NULL,
    #         #     message_type=MessageType.STREAM
    #         # ))
    #         print('here2')
    #         await websocket.send_json(
    #             WebsocketResponse(
    #                 sender=Sender.BOT,
    #                 message=Message.NULL,
    #                 message_type=MessageType.END,
    #             ).dict()
    #         )
    #     except WebSocketDisconnect:
    #         break
    #     except Exception as e:
    #         await websocket.send_json(
    #             WebsocketResponse(
    #                 sender=Sender.BOT,
    #                 message=Message.ERROR,
    #                 message_type=MessageType.ERROR,
    #             ).dict()
    #         )
