from fastapi import FastAPI, Depends
from checkin import GenrativeCheckIn
from reflections import MoodReflectionAgent
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from schema.reflection import ReflectionPerTopic, Reflection
from endpoints import login
from deps import get_db, connection_string

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


@app.get("/reflection_topics")
async def get_topics_of_reflection(currentUser = Depends(login.get_current_user)): 
    return reflection_agent.get_topics_of_reflection(str(currentUser.id), connection_string)

@app.post("/reflection_heading")
async def get_reflection_heading(data: dict): 
    return reflection_agent.get_heading(topics=data['topics'])

@app.post("/mood_reflection")
async def mood_reflection(data: dict, db = Depends(get_db), currentUser = Depends(login.get_current_user), response_model=Reflection): 
    reflection_per_topic = reflection_agent.reflect(topics=data['topics'], user_reflections=data['user_reflections'], session_id=str(currentUser.id), postgres_connection=connection_string)
    # print("heading: ", data['heading'])
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
