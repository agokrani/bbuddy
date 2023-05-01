from fastapi import FastAPI
from checkin import GenrativeCheckIn
from fastapi.middleware.cors import CORSMiddleware

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