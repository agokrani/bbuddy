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
from schema.reflection import AIInsight, HumanInsight, ReflectionPerTopic

class MoodReflectionAgent: 
    llm = OpenAI(temperature=0)
    verbose = True
    
    def chain(self, prompt):
        return LLMChain(llm=self.llm, prompt=prompt, verbose=self.verbose)

    def get_heading(self, topics): 
        prompt = PromptTemplate.from_template(
            "{topics}\n\n"
            + "From the statement above, generate a title for the reflection post\n"
            + "Output should be around 4 words max\n\n"
            + "Output format JSON with \"heading\" key"
        )

        topics_str = "\n".join([t for t in topics]) 
        
        response = self.chain(prompt).run(topics=topics_str)
        
        return json.loads(response)


    def get_topics_of_reflection(self, session_id, postgres_connection, last_k = 3): 
        observations = self._get_mood_observations(session_id, postgres_connection)
        
        prompt = PromptTemplate.from_template(
            "{observations}\n\n"
            + "Given only the information above, what are the two most salient"
            + " high-level questions we can ask about the human in"
            + " the statements to let him reflect back on his day? The question should be deep and reflective"
            + "Ouput should contain two questions and only questions"
            + "Output Format: JSON with key questions containing list of questions"
        )
        response = self.chain(prompt).run(observations=observations)

        return json.loads(response)


    def _get_mood_observations(self, session_id, postgres_connection, last_k = 3):  
        history = PostgresChatMessageHistory(
            connection_string=postgres_connection,
            session_id = session_id
        )

        human_messages = list(filter(lambda message: isinstance(message, HumanMessage), history.messages))[-last_k:]
        mood_observations = "\n".join([message.content for message in human_messages]) 
        
        return mood_observations

    def _get_insights_on_topic(self, topic, session_id, postgres_connection, user_reflection='', last_k = 3): 
        related_statements = self._get_mood_observations(session_id, postgres_connection)
        
        prompt = PromptTemplate.from_template(
            "Statements about {topic}\n"
            + "{related_statements}\n\n"
            + "What are the 2 most high-level insights can you infer from the above statements?\n\n"
            + "Each insight should use second-person point of view tone\n\n"
            + "Pay extra attention to politeness \n\n"
            + "Output Format: JSON with key \"insights\" containing list of insights"
        )
        response = self.chain(prompt).run(topic=topic, related_statements=related_statements)
        
        response_json = json.loads(response)
        
        ai_insights = [AIInsight(content=insight) for insight in response_json["insights"]]
        
        human_insight = HumanInsight(content=user_reflection)
        
        topic_reflection = ReflectionPerTopic(
            topic = topic, 
            human_insight = human_insight, 
            ai_insights = ai_insights
        )
        
        return topic_reflection

    def reflect(self, topics, session_id, postgres_connection, last_k = 3):
        reflections = []
        
        for topic in topics: 
            reflections.append(self._get_insights_on_topic(topic, session_id, postgres_connection))
        
        return reflections
            
    def store_reflection(self, db, session_id, reflection_to_add: List[ReflectionPerTopic]): 
        history = ReflectionHistoryManager(
            session_id = session_id
        )

        history.add_reflection(db, reflection_to_add)

    def get_reflection_history(self, db, session_id: str):
        history = ReflectionHistoryManager(
            session_id = session_id
        )
        return history.reflection_history(db)