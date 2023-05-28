from fastapi import FastAPI, Depends
from checkin import GenrativeCheckIn
from reflections import MoodReflectionAgent
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from schema.reflection import ReflectionPerTopic, Reflection
from endpoints import login
from deps import get_db, connection_string
from schema.goal import Goal
from goals import GoalAgent

app = FastAPI()

app.include_router(login.router)


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
    allow_methods=["POST", "GET"],
		allow_headers=["*"],
    max_age=3600,
)


generative_check_in = GenrativeCheckIn()
reflection_agent = MoodReflectionAgent()
goal_agent = GoalAgent()

@app.post("/mood_check_in")
async def mood_check_in(data: dict):
    """ Get the response from model for daily check in """
    return {"message": 
        generative_check_in.get_response(
            feeling=data['feeling'],
            feeling_form=data['feeling_form'],
            reason_entity=data['reason_entity'], 
            reason=data['reason']
        )
    }

@app.post("/store_mood_check_in")
async def store_mood_check_in(data: dict, currentUser = Depends(login.get_current_user)):
    generative_check_in.store(
        feeling_message=data['feeling_message'], 
        reason=data['reason'], 
        ai_response=data['ai_response'], 
        session_id=str(currentUser.id),
        postgres_connection=connection_string       
    )

@app.get("/count_mood_check_in")
async def count_mood_check_in(currentUser = Depends(login.get_current_user)): 
    return generative_check_in.count_check_in(str(currentUser.id), connection_string)

@app.get("/count_reflections")
async def count_reflections(db = Depends(get_db), currentUser = Depends(login.get_current_user)): 
    return reflection_agent.count_reflections(db=db, session_id=str(currentUser.id))

@app.get("/reflection_topics")
async def get_topics_of_reflection(currentUser = Depends(login.get_current_user)): 
    return reflection_agent.get_topics_of_reflection(str(currentUser.id), connection_string)

@app.post("/reflection_heading")
async def get_reflection_heading(data: dict): 
    return reflection_agent.get_heading(topics=data['topics'])

@app.post("/mood_reflection")
async def mood_reflection(data: dict, db = Depends(get_db), currentUser = Depends(login.get_current_user), response_model=Reflection): 
    reflection_per_topic = reflection_agent.reflect(topics=data['topics'], user_reflections=data['user_reflections'], session_id=str(currentUser.id), postgres_connection=connection_string)
    if data['heading'] == '' or data['heading'] == None: 
        data['heading'] = reflection_agent.get_heading(data['topics'])['heading']
    generated_reflection = Reflection(
        heading=data['heading'],
        topic_reflections = reflection_per_topic
    )
    reflection_agent.store_reflection(db=db, session_id=str(currentUser.id), reflection_to_add=generated_reflection)
    return generated_reflection


@app.get("/reflection_history", response_model=List[Reflection])
async def get_reflection_history(db = Depends(get_db), currentUser = Depends(login.get_current_user)):
    history = reflection_agent.get_reflection_history(db, str(currentUser.id))
    return history

@app.get("/goal_history", response_model=List[Goal])
async def get_goal_history(db = Depends(get_db), currentUser = Depends(login.get_current_user)): 
    history = goal_agent.get_goal_history(db, str(currentUser.id))
    return history

@app.get("/set_new_goal")
async def set_new_goal(db = Depends(get_db), currentUser = Depends(login.get_current_user)): 
    new_goal = goal_agent.set_new_goal(db, str(currentUser.id), reflection_agent)
    goal_agent.store_goal(db=db, session_id=str(currentUser.id), goal_to_add=new_goal)
