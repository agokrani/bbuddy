from fastapi import FastAPI, Depends
from checkin import GenrativeCheckIn
from reflections import MoodReflectionAgent
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from schema.reflection import Reflection
from endpoints import login
from deps import get_db, connection_string
from schema.goal import Goal, GoalInDB, GoalType, goal_from_dict
from goals import GoalAgent
from endpoints import goal_chat
from db.stats_manager import stats_manager
from schema.stats import UserStats, user_stat_from_dict

app = FastAPI()

app.include_router(login.router)
app.include_router(goal_chat.langchain_router)

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
@app.get("/mood_check_in_history")
async def mood_check_in_history(last_k = None, currentUser = Depends(login.get_current_user)): 
    return generative_check_in.get_check_in_history(str(currentUser.id), connection_string, last_k)

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
async def get_reflection_history(start_date = None, end_date = None, db = Depends(get_db), currentUser = Depends(login.get_current_user)):
    history = reflection_agent.get_reflection_history(db, str(currentUser.id), start_date=start_date, end_date=end_date)
    return history

@app.get("/goal_history", response_model=List[GoalInDB])
async def get_goal_history(db = Depends(get_db), currentUser = Depends(login.get_current_user)): 
    history = goal_agent.get_goal_history(db, str(currentUser.id))
    return history

@app.get("/set_new_goal", response_model=Goal)
async def set_new_goal(start_date = None, end_date = None, db = Depends(get_db), currentUser = Depends(login.get_current_user)): 
    new_goal = goal_agent.set_new_goal(db, str(currentUser.id), reflection_agent, start_date = start_date, end_date = end_date)
    goal_agent.store_goal(db=db, session_id=str(currentUser.id), goal_to_add=new_goal)
    
    return new_goal

@app.post("/update_goal")
async def update_goal(data: dict, db = Depends(get_db), currentUser = Depends(login.get_current_user)): 
    goal_agent.update_goal(db=db, session_id=str(currentUser.id), goal_to_update=data)
    

@app.get("/counter_stats", response_model=List[UserStats]) 
async def get_counter_stats(db=Depends(get_db), currentUser = Depends(login.get_current_user)): 
    return stats_manager.get_counters(db, currentUser.id)

@app.post("/update_stats", response_model=GoalInDB)
async def update_stats(data: dict, db=Depends(get_db), currentUser = Depends(login.get_current_user)): 
    stats_manager.update_stats(user_stat_from_dict(data), db, currentUser.id)

@app.post("/set_personal_goal")
async def set_personal_goal(data: dict, db=Depends(get_db), currentUser = Depends(login.get_current_user)):
    milestones = goal_agent.get_milestones(data["description"])
    
    goal_to_add = Goal(description=data["description"], type=GoalType(data["type"]), milestones=milestones)
    
    gid = goal_agent.store_goal(db=db, session_id=str(currentUser.id), goal_to_add=goal_to_add)
    newGoal = GoalInDB(id=gid, **goal_to_add.dict())
    
    return newGoal
    