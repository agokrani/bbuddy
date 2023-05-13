from fastapi import FastAPI
from checkin import GenrativeCheckIn
from reflections import MoodReflectionAgent
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from schema import ReflectionPerTopic, Reflection

app = FastAPI()

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
postgres_connection = "postgresql://bijmbrqw:xnnbF7f-i_X-9uPRnUreaOOJFS-d9oWt@dumbo.db.elephantsql.com/bijmbrqw"

@app.post("/mood_check_in")
async def mood_check_in(data: dict):
    """ Get the response from model for daily check in """
    return {"message": 
        generative_check_in.get_response(
            feeling=data['feeling'], 
            reason_entity=data['reason_entity'], 
            reason=data['reason']
        )
    }

@app.post("/store_mood_check_in")
async def store_mood_check_in(data: dict): 
    generative_check_in.store(
        feeling_message=data['feeling_message'], 
        reason=data['reason'], 
        ai_response=data['ai_response'], 
        session_id=data['session_id'],
        postgres_connection=postgres_connection        
    )

@app.get("/count_mood_check_in")
async def count_mood_check_in(session_id: str): 
    return generative_check_in.count_check_in(session_id, postgres_connection)


@app.get("/reflection_topics")
async def get_topics_of_reflection(session_id: str): 
    return reflection_agent.get_topics_of_reflection(session_id, postgres_connection)

@app.post("/reflection_heading")
async def get_reflection_heading(data: dict): 
    print(data['topics'])
    return reflection_agent.get_heading(topics=data['topics'])

@app.post("/mood_reflection")
async def mood_reflection(data: dict, response_model=Reflection): 
    reflection_per_topic = reflection_agent.reflect(topics=data['topics'], session_id=str(data['session_id']), postgres_connection=postgres_connection)
    print("heading: ", data['heading'])
    if data['heading'] == '' or data['heading'] == None: 
        data['heading'] = reflection_agent.get_heading(data['topics'])['heading']
    generated_reflection = Reflection(
        heading=data['heading'],
        topic_reflections = reflection_per_topic
    )
    reflection_agent.store_reflection(generated_reflection, session_id=str(data['session_id']), postgres_connection=postgres_connection)
    return generated_reflection


@app.get("/reflection_history", response_model=List[Reflection])
async def get_reflection_history(session_id: str): 
    history = reflection_agent.get_reflection_history(session_id, postgres_connection)
    return history
