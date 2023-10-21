from datetime import datetime
import json 
from langchain.llms import OpenAI
from langchain import LLMChain
from langchain.prompts import (
    PromptTemplate,
)
from langchain.schema import (
    HumanMessage
)
from checkins import GenrativeCheckIn
from db.firestore_client import FirestoreClient
from schema.reflection import AIInsight, HumanInsight, Reflection, ReflectionPerTopic, encrypt_reflection, reflection_to_dict, reflections_from_dict, decrypt_reflection
from langchain.schema import messages_from_dict

class MoodReflectionAgent: 
    llm = OpenAI(temperature=0)
    verbose = True
    collection_name = "reflections"
    
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


    def get_topics_of_reflection(self, user_id:str, last_k = 3): 
        observations = self._get_mood_observations(user_id=user_id, last_k=last_k)
        
        prompt = PromptTemplate.from_template(
            "{observations}\n\n"
            + "Given only the information above, what are the two most salient"
            + " high-level questions we can ask about the human in"
            + " the statements to let him reflect back on his day? The question should be deep and reflective \n\n"
            + "Ouput should contain two questions and only questions\n"
            + "Output Format: JSON with key questions containing list of questions"
        )
        
        response = self.chain(prompt).run(observations=observations)
        
        return json.loads(response)

    # TODO: Change this to firestore with correct dependencies 
    def _get_mood_observations(self, user_id, last_k=3):  
        history = GenrativeCheckIn().get_history(user_id=user_id, last_k=last_k)
        human_messages = []
        for c in history: 
            human_messages.append(list(filter(lambda message: isinstance(message, HumanMessage), messages_from_dict(c.messages)))[0])
        
        mood_observations = "\n".join([message.content for message in human_messages]) 
        
        return mood_observations

    def _get_insights_on_topic(self, topic, user_id, user_reflection='', last_k=3): 
        related_statements = self._get_mood_observations(user_id=user_id, last_k=last_k)
        if (user_reflection is not None) or (user_reflection != ''):
            prompt = PromptTemplate.from_template(
                "Statements about {topic}\n"
                + "{user_reflection}\n"
                + "{related_statements}\n\n"
                + "What are the 2 most high-level insights can you infer from the above statements?\n\n"
                + "Each insight should use second-person point of view tone\n\n"
                + "Pay extra attention to politeness \n\n"
                + "Output Format: JSON with key \"insights\" containing list of insights"
            )
        else: 
            prompt = PromptTemplate.from_template(
                "Statements about {topic}\n"
                + "{related_statements}\n\n"
                + "What are the 2 most high-level insights can you infer from the above statements?\n\n"
                + "Each insight should use second-person point of view tone\n\n"
                + "Pay extra attention to politeness \n\n"
                + "Output Format: JSON with key \"insights\" containing list of insights"
            )
        response = self.chain(prompt).run(topic=topic, related_statements=related_statements, user_reflection=user_reflection)
        
        response_json = json.loads(response)
        
        ai_insights = [AIInsight(content=insight) for insight in response_json["insights"]]
        
        human_insight = HumanInsight(content=user_reflection)
        
        topic_reflection = ReflectionPerTopic(
            topic = topic, 
            human_insight = human_insight, 
            ai_insights = ai_insights
        )
        
        return topic_reflection

    def reflect(self, topics, user_reflections, user_id:str, last_k = 3):
        reflections = []
        
        for topic, user_reflection in zip(topics, user_reflections): 
            reflections.append(self._get_insights_on_topic(topic, user_id, user_reflection, last_k=last_k))
        
        return reflections

    def store(self, reflection_to_add: Reflection, user_id: str):
        client = FirestoreClient(collection_name=self.collection_name)
        encrypted_reflection = encrypt_reflection(reflection_to_add)
        client.set_document({
                "user_id": user_id,
                "reflection": reflection_to_dict(encrypted_reflection),
                "create_time": datetime.now(),
        })
        
    def get_history(self, user_id: str, start_date=None, end_date=None):
        client = FirestoreClient(collection_name=self.collection_name, user_id=user_id)
        documents = client.get_documents()
        
        if start_date is not None and start_date != '':
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date is not None and end_date != '':
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        
        if (start_date is not None and start_date != '') or (end_date is not None and end_date != ''):
            filtered_documents = []
            for doc in documents:
                create_time = doc.get('create_time', datetime.min)
                if (start_date is None or create_time >= start_date) and (end_date is None or create_time <= end_date):
                    filtered_documents.append(doc)

            filtered_documents = sorted(filtered_documents, key=lambda doc: doc.get('create_time', datetime.min), reverse=True)
            history = reflections_from_dict([decrypt_reflection(doc["reflection"]) for doc in filtered_documents])
        else:
            documents = sorted(documents, key=lambda doc: doc.get('create_time', datetime.min), reverse=True)
            history = reflections_from_dict([decrypt_reflection(doc["reflection"]) for doc in documents])
        
        return history
    
    def get_count(self, user_id: str): 
        client = FirestoreClient(collection_name=self.collection_name, user_id=user_id)
        documents = client.get_documents()
        
        return len(documents)