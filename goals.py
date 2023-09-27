import json
from datetime import datetime
from langchain.llms import OpenAI
from langchain import LLMChain
#from langchain.callbacks.base import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.prompts import (
    PromptTemplate,
)
from db.firestore_client import FirestoreClient
from schema.goal import Milestone, Goal, GoalType, goal_to_dict, goals_from_dict
from db.goal_history_manager import GoalHistoryManager

class GoalAgent: 
    verbose = True
    llm = OpenAI(streaming=True, temperature=0, callbacks=[StreamingStdOutCallbackHandler()], verbose=verbose)
    collection_name = "goals"
    
    def chain(self, prompt):
        return LLMChain(llm=self.llm, prompt=prompt, verbose=self.verbose)

    # def get_goal_history(self, db, session_id: str): 
    #     history = GoalHistoryManager(
    #         session_id = session_id
    #     )
    #     return history.goal_history(db)
    
    def get_history(self, user_id:str): 
        client = FirestoreClient(collection_name=self.collection_name, user_id=user_id)
        
        documents = sorted(client.get_documents(), key=lambda doc: doc.get('create_time', datetime.min), reverse=True)
        history = goals_from_dict(documents)
        
        return history
    
    def get_reflection_observations(self, user_id: str, reflection_agent, start_date=None, end_date=None, last_k=3): 
        reflection_history = reflection_agent.get_history(user_id=user_id, start_date=start_date, end_date=end_date)
        
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

    def set_new_goal(self, user_id:str, reflection_agent, start_date=None, end_date=None):
        reflection_observations = self.get_reflection_observations(user_id, reflection_agent, start_date=start_date, end_date=end_date)
        
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
        
        milestones = self.get_milestones(description=description)
        
        return Goal(description=description, type=GoalType.GENERATED, milestones=milestones)
    
    def get_milestones(self, description): 
        milestone_prompt = PromptTemplate.from_template(
            "Goal: {goal}\n\n\n"
            + "Given the goal above what are the 5 milestones that I can set to make this a SMART goal\n\n"
            + "Output Format: JSON with key \"milestones\" containing list of milestones\n\n"
            + "Be precise and don't hallucinate. All milestones should be something people do in real life\n\n"
        )
        response = self.chain(milestone_prompt).run(goal=description)
        
        milestones = [Milestone(content=milestone)for milestone in json.loads(response)["milestones"]]
        
        return milestones
    
    # def store_goal(self, db, session_id:str, goal_to_add: Goal):
    #     history = GoalHistoryManager(
    #         session_id = session_id
    #     )
    #     return history.add_goal(db, goal_to_add)
    
    def store(self, goal_to_add: Goal, user_id: str):
        client = FirestoreClient(collection_name=self.collection_name)
        return client.set_document({
                "user_id": user_id,
                "goal": goal_to_dict(goal_to_add),
                "create_time": datetime.now(),
        })

    # def update_goal(self, db, session_id: str, goal_to_update):
    #     history = GoalHistoryManager(
    #         session_id = session_id
    #     )
    #     history.update_goal(db, goal_to_update)
    
    def update(self, goal_to_update, user_id: str): 
        client = FirestoreClient(collection_name=self.collection_name)
        client.update_document(document_id=goal_to_update.id, data={
            "goal":goal_to_dict(goal_to_update)
        })

    def delete(self, goal_id: str, user_id: str): 
        client = FirestoreClient(collection_name=self.collection_name)
        client.delete_document(document_id=goal_id)

    # def delete_goal(self, db, session_id: str, goal_id: int): 
    #     history = GoalHistoryManager(
    #         session_id=session_id
    #     )
    #     history.delete_goal(db, id=goal_id)
