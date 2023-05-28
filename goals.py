import json 
from typing import List
from langchain.llms import OpenAI
from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.base import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.prompts import (
    ChatPromptTemplate,
    PromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.memory.summary import SummarizerMixin
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
from langchain.memory import PostgresChatMessageHistory
from db.reflection_history_manager import ReflectionHistoryManager
from schema.goal import Milestone, Goal
from db.goal_history_manager import GoalHistoryManager

class GoalAgent: 
    llm = OpenAI(temperature=0)
    verbose = True
    
    def chain(self, prompt):
        return LLMChain(llm=self.llm, prompt=prompt, verbose=self.verbose)

    def get_goal_history(self, db, session_id: str): 
        history = GoalHistoryManager(
            session_id = session_id
        )
        return history.goal_history(db)
    
    def get_reflection_observations(self, db, session_id: str, reflection_agent, last_k=3): 
        reflection_history = reflection_agent.get_reflection_history(db=db, session_id=session_id)
        
        if len(reflection_history) >= 3:
            reflection_history = reflection_history[:last_k]
        
        reflection_observations = ""
        for reflection in reflection_history:
                reflection_observations += f"{reflection.heading}:\n"
                for topic_reflection in reflection.topic_reflections:
                    reflection_observations += f"\t{topic_reflection.topic}\n"
                    reflection_observations += f"\t\tHuman insight: {topic_reflection.human_insight.content}\n"
                    reflection_observations += "\t\tAI insights:\n"
                    for ai_insight in topic_reflection.ai_insights:
                        reflection_observations += f"\t\t\t{ai_insight.content}\n"
        
        return reflection_observations

    def set_new_goal(self, db, session_id:str, reflection_agent): 
        reflections_observations = ""
        goals_history = self.get_goal_history(db, session_id)
        if goals_history: 
            ## need to add more code here
            return
        else: 
            reflection_observations = self.get_reflection_observations(db, session_id, reflection_agent)
        
        goal_generation_prompt = PromptTemplate.from_template(
            "{observations}\n\n\n\n"
            + "Given the information above, what is the one most important goal this person can have\n\n"
            + "Make sure that these goals are specific, achievable and measurable\n\n"
            + "Goal should be suggestive and not recommended \n\n"
            + "Goal should use second-person point of view tone\n\n"
            + "Goal should be around 15 words max\n\n"
            + "Output Format: JSON with key \"goal\""
        )
        response = self.chain(goal_generation_prompt).run(observations=reflection_observations)
        
        description = json.loads(response)["goal"]
        
        milestone_prompt = PromptTemplate.from_template(
            "Goal: {goal}\n\n\n"
            + "Given the goal above what are the 5 milestones that I can set to make this a SMART goal\n\n"
            + "Output Format: JSON with key \"milestones\" containing list of milestones\n\n"
            + "Be precise and don't hallucinate. All milestones should be something people do in real life\n\n"
        )
        response = self.chain(milestone_prompt).run(goal=description)
        
        milestones = [Milestone(content=milestone)for milestone in json.loads(response)["milestones"]]
        
        return Goal(description=description, milestones=milestones)

    def store_goal(self, db, session_id:str, goal_to_add: Goal):
        history = GoalHistoryManager(
            session_id = session_id
        )
        history.add_goal(db, goal_to_add)