from fastapi import FastAPI, Depends, Request
from datetime import datetime
from lanarky import LangchainRouter

from langchain import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from agents.cbt_conversation.base import CbtConversationAgent
from checkins import generative_check_in
from goals import goal_agent
from reflections import MoodReflectionAgent
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from schema.reflection import Reflection
from endpoints import login 
from schema.goal import Goal, GoalInDB, GoalType
from endpoints import goal_chat, checkin_chat
from stats import stats_manager
from schema.stats import UserStats, user_stat_from_dict
from db.vector_store_client import vClient

app = FastAPI()

app.include_router(login.router)
app.include_router(goal_chat.langchain_router)
app.include_router(checkin_chat.checkin_router)
# Add CORS middleware
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:8080",
    "*",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    #allow_methods=["POST", "GET"],
    allow_methods=["*"],
		allow_headers=["*"],
    max_age=3600,
)



reflection_agent = MoodReflectionAgent()

def create_chain():
    return ConversationChain(
        llm=ChatOpenAI(
            temperature=0,
            streaming=True,
            callbacks=[StreamingStdOutCallbackHandler()]
        ),
        verbose=True,
    )
chain = create_chain()

langchain_router = LangchainRouter(
    langchain_url="/chat", langchain_object=chain, streaming_mode=1
)

app.include_router(langchain_router)

def chunk_generator(data, chunk_size):
    for i in range(0, len(data), chunk_size):
        yield data[i:i+chunk_size]

@app.post("/mood_check_in")
async def mood_check_in(request: Request, user_id:str = Depends(login.get_firebase_user)):
    data = await request.json()
    
    message = generative_check_in.get_response(
        feeling=data['feeling'],
        feeling_form=data['feeling_form'],
        reason_entity=data['reason_entity'], 
        reason=data['reason'])
    return {"message": message}
    

@app.post("/store_mood_check_in")
async def store_mood_check_in(request: Request, user_id:str = Depends(login.get_firebase_user)):
    data = await request.json()
    return generative_check_in.store(feeling_message=data['feeling_message'], 
        reason=data['reason'], 
        ai_response=data['ai_response'], 
        user_id=str(user_id))

@app.post("/extract_cbt_techniques")
def extract_cbt_techniques(data: dict):
    #response  = follow_up_chain.invoke(data)
    #print(response)
    response = """[
  {
    "name": "Thought challenging",
    "action": "Role play thought challenging",
    "instruction": "Let's role play a 'thought challenging' exercise with the user. Encourage them to identify and challenge any negative thoughts related to their work. Provide prompts and guide them through the process of examining evidence and considering alternative, more balanced thoughts. Make sure to create a safe and supportive environment for the user. Focus solely on the exercise, avoiding any additional questions or information beyond the exercise."
  },
  {
    "name": "Self-care",
    "action": "Let's try Self-care",
    "instruction": "Guide the user through a Self-care exercise. Encourage them to prioritize their well-being by getting enough rest, eating nutritious meals, and engaging in activities that bring them joy and relaxation. Remind them to take breaks throughout the day and practice deep breathing exercises to reduce stress. Use the provided context about feeling overwhelmed at work to make the exercise more effective. Focus only on the self-care exercise, and refrain from answering additional questions or providing unrelated information."
  }
]
"""
    return response

@app.post("/cbt_chat")
def cbt_chat(data: dict, currentUser = Depends(login.get_current_user)): 
    cbt_technique = data["technique"]
    
    agent = CbtConversationAgent().get_agent(data["cId"])
    
    vDb = vClient.get_db()

    context = vDb.query(input_query=cbt_technique["instruction"], n_results=2, where=None)
    agent.run(technique = cbt_technique["name"], username = currentUser.firstName, 
                instruction=cbt_technique["instruction"], 
                context = context, input=data["user_message"]
            )


@app.get("/mood_check_in_history")
async def mood_check_in_history(last_k = None, user_id = Depends(login.get_firebase_user)):
    if user_id is not None: 
        return generative_check_in.get_history(user_id=user_id, last_k=last_k)
    
@app.get("/count_mood_check_in")
async def count_mood_check_in(user_id = Depends(login.get_firebase_user)): 
    return generative_check_in.get_count(user_id=user_id)
    #return generative_check_in.count_check_in(str(currentUser.id), connection_string)

@app.get("/count_reflections")
async def count_reflections(user_id = Depends(login.get_firebase_user)): 
    #return reflection_agent.count_reflections(db=db, session_id=str(currentUser.id))
    return reflection_agent.get_count(user_id=user_id)

@app.get("/reflection_topics")
async def get_topics_of_reflection(user_id:str = Depends(login.get_firebase_user)): 
    return reflection_agent.get_topics_of_reflection(user_id=str(user_id))

@app.post("/reflection_heading")
async def get_reflection_heading(data: dict): 
    return reflection_agent.get_heading(topics=data['topics'])

@app.post("/mood_reflection", response_model=Reflection)
async def mood_reflection(request: Request, user_id = Depends(login.get_firebase_user)): 
    data = await request.json()
    reflection_per_topic = reflection_agent.reflect(topics=data['topics'], user_reflections=data['user_reflections'], user_id=user_id)
    if data['heading'] == '' or data['heading'] == None: 
        data['heading'] = reflection_agent.get_heading(data['topics'])['heading']
    generated_reflection = Reflection(
        heading=data['heading'],
        topic_reflections = reflection_per_topic
    )
    reflection_agent.store(reflection_to_add=generated_reflection, user_id=user_id)
    return generated_reflection


@app.get("/reflection_history", response_model=List[Reflection])
async def get_reflection_history(start_date = None, end_date = None, user_id = Depends(login.get_firebase_user)):
    
    history = reflection_agent.get_history(user_id=user_id, start_date=start_date, end_date=end_date)
    return history

@app.get("/goal_history", response_model=List[GoalInDB])
async def get_goal_history(user_id = Depends(login.get_firebase_user)): 
    #history = goal_agent.get_goal_history(db, str(currentUser.id))
    history = goal_agent.get_history(user_id=user_id)
    return history

@app.get("/set_new_goal", response_model=GoalInDB)
async def set_new_goal(start_date = None, end_date = None, user_id = Depends(login.get_firebase_user)): 
    goal = goal_agent.set_new_goal(user_id=user_id, reflection_agent=reflection_agent, start_date = start_date, end_date = end_date)
    
    #goal_agent.store_goal(db=db, session_id=str(currentUser.id), goal_to_add=new_goal)
    create_time = datetime.now()
    gid = goal_agent.store(goal_to_add=goal, user_id=user_id, create_time=create_time)
    goal.create_time = create_time
    new_goal = GoalInDB(id=gid, **goal.dict())

    return new_goal

@app.post("/update_goal")
async def update_goal(request: Request, user_id = Depends(login.get_firebase_user)): 
    data = await request.json()
    #goal_agent.update_goal(db=db, session_id=str(currentUser.id), goal_to_update=data)
    goal_to_update = GoalInDB(**data)
    goal_agent.update(goal_to_update=goal_to_update, user_id=user_id)

@app.get("/counter_stats", response_model=List[UserStats]) 
async def get_counter_stats(user_id = Depends(login.get_firebase_user)): 
    return stats_manager.get_stats(user_id=user_id)

@app.post("/update_stats")
async def update_stats(request: Request, user_id = Depends(login.get_firebase_user)): 
    data = await request.json()
    stats_manager.update(user_stat_from_dict(data), user_id=user_id)

@app.post("/set_personal_goal", response_model=GoalInDB)
async def set_personal_goal(request: Request, user_id = Depends(login.get_firebase_user)):
    data = await request.json()
    milestones = goal_agent.get_milestones(data["description"])
    
    goal_to_add = Goal(description=data["description"], type=GoalType(data["type"]), milestones=milestones)
    
    #gid = goal_agent.store_goal(db=db, session_id=str(currentUser.id), goal_to_add=goal_to_add)
    gid = goal_agent.store(goal_to_add=goal_to_add, user_id=user_id)
    new_goal = GoalInDB(id=gid, **goal_to_add.dict())
    
    return new_goal
    
@app.delete("/delete_goal/{goal_id}")
async def delete_goal(goal_id: str, user_id=Depends(login.get_firebase_user)):
    #goal_agent.delete_goal(db=db, session_id=str(currentUser.id), goal_id=goal_id)
    goal_agent.delete(goal_id=goal_id, user_id=user_id)