from pydantic import BaseModel
from typing import List
from utils.encryption import encrypt, decrypt

class BaseInsight(BaseModel):
    content: str

    def type(self) -> str:
        raise NotImplementedError
    
class HumanInsight(BaseInsight):
    def type(self) -> str:
        return "human"
    
    def to_dict(self):
        return self.dict()

class AIInsight(BaseInsight):
    def type(self) -> str:
        return "ai"

    def to_dict(self):
        return self.dict()


class ReflectionPerTopic(BaseModel):
    topic: str
    human_insight: HumanInsight
    ai_insights: List[AIInsight]

    def to_dict(self):
        return {
            'topic': self.topic,
            'human_insight': self.human_insight.to_dict(),
            'ai_insights': [ai_insight.to_dict() for ai_insight in self.ai_insights]
        }

class Reflection(BaseModel): 
    heading: str
    topic_reflections: List[ReflectionPerTopic]


def reflection_to_dict(reflection):
    return {"heading": reflection.heading, "topic_reflections": [tr.to_dict() for tr in reflection.topic_reflections]}

def reflection_from_dict(reflection_dict: dict): 
    topic_reflections = []

    for tr in reflection_dict['topic_reflections']:
        ai_insights = [AIInsight(**insight) for insight in tr['ai_insights']]
        human_insight = HumanInsight(**tr['human_insight'])
        topic_reflections.append(ReflectionPerTopic(topic=tr['topic'], ai_insights=ai_insights, human_insight=human_insight))

    return Reflection(heading=reflection_dict['heading'], topic_reflections=topic_reflections)

def reflections_from_dict(reflections): 
    return [reflection_from_dict(r) for r in reflections]

def encrypt_reflection(reflection): 
    heading = encrypt(reflection.heading)
    topic_reflections = []
    for tr in reflection.topic_reflections: 
        topic = encrypt(tr.topic)
        human_insight = HumanInsight(content=encrypt(tr.human_insight.content))
        ai_insights = []
        for ai_insight in tr.ai_insights: 
            ai_insights.append(AIInsight(content=encrypt(ai_insight.content)))
        topic_reflections.append(ReflectionPerTopic(topic=topic, human_insight=human_insight, ai_insights=ai_insights))
    
    return Reflection(heading=heading, topic_reflections=topic_reflections)


def decrypt_reflection(encrypted_reflection_dict):
    return {
        "heading": decrypt(encrypted_reflection_dict["heading"]),
        "topic_reflections": [
            {
                "ai_insights": [{"content": decrypt(ai["content"])} for ai in tr["ai_insights"]],
                "human_insight": {"content": decrypt(tr["human_insight"]["content"])},
                "topic": decrypt(tr["topic"])
            } for tr in encrypted_reflection_dict["topic_reflections"]
        ]
    }

