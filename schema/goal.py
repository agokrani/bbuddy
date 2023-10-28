from enum import Enum
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from utils.encryption import encrypt, decrypt

class Milestone(BaseModel): 
    content: str
    status: Optional[bool];
    
    def to_dict(self):
        return self.dict()


class GoalType(str, Enum): 
    PERSONAL = "personal",
    GENERATED = "generated"

class Goal(BaseModel):
    create_time: Optional[datetime]
    description: str
    type: Optional[GoalType]
    milestones: List[Milestone]

class GoalInDB(Goal):
    id: str

def goal_to_dict(goal):
    return {"description": goal.description, "type": goal.type, "milestones": [m.to_dict() for m in goal.milestones]}

def goal_from_dict(goal_dict):
    gid = goal_dict.get("id")
    create_time = goal_dict.get("create_time")
    g = goal_dict.get("goal")
    goal_type = g.get("type") if g else None  # Retrieve type key or set it to None
    if gid is not None:
        if create_time is not None:
            return GoalInDB(id=gid, create_time=create_time, type=goal_type, description=g["description"], milestones=g["milestones"])
        else:
            return GoalInDB(id=gid, description=g["description"], type=goal_type, milestones=g["milestones"])
    else:
        if create_time is not None:
            return Goal(create_time=create_time, description=g["description"], type=goal_type, milestones=g["milestones"])
        else:
            return Goal(description=g["description"], type=goal_type, milestones=g["milestones"])

def goals_from_dict(goals): 
    return [goal_from_dict(g) for g in goals]


def encrypt_goal(goal): 
    description = encrypt(goal.description)
    milestones = []
    for milestone in goal.milestones: 
        milestones.append(Milestone(content=encrypt(milestone.content), status=milestone.status))
    if isinstance(goal, GoalInDB): 
        return GoalInDB(id=goal.id, create_time=goal.create_time, description=description, type=goal.type, milestones=milestones)
    return Goal(create_time=goal.create_time, description=description, type=goal.type, milestones=milestones)


def decrypt_goal(encrypted_goal_dict): 
    #print(encrypted_goal_dict)
    decrypted_goal = {
        "create_time": encrypted_goal_dict["create_time"],
        "goal":{ 
            "type": encrypted_goal_dict["goal"]["type"],
            "description": decrypt(encrypted_goal_dict["goal"]["description"]),
            "milestones": [
                {"content": decrypt(milestone["content"]), "status": milestone["status"]} for milestone in encrypted_goal_dict["goal"]["milestones"]  
            ] 
        }
    }

    if "id" in encrypted_goal_dict:
        decrypted_goal["id"] = encrypted_goal_dict["id"]

    return decrypted_goal