from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Milestone(BaseModel): 
    content: str
    
    def to_dict(self):
        return self.dict()

class Goal(BaseModel):
    create_time: Optional[datetime]
    description: str
    milestones: List[Milestone]

def goal_to_dict(goal):
    return {"description": goal.description, "milestones": [m.to_dict() for m in goal.milestones]}

def goal_from_dict(goal_dict):
    create_time = goal_dict.get("create_time")  # Get the value of "create_time" from the dictionary
    g = goal_dict.get("goal")
    if create_time is not None:
        return Goal(create_time=create_time, description=g["description"], milestones=g["milestones"])
    else:
        return Goal(description=g["description"], milestones=g["milestones"])

def goals_from_dict(goals): 
    return [goal_from_dict(g) for g in goals]