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

class reflections: 
    llm = OpenAI(temperature=0)
    verbose = True
    
    def chain(self, prompt):
        return LLMChain(llm=self.llm, prompt=prompt, verbose=self.verbose)

    def get_topics_of_reflection(self, session_id, postgres_connection, last_k = 3): 
        observations = self._get_mood_observations(session_id, postgres_connection)
        
        prompt = PromptTemplate.from_template(
            "{observations}\n\n"
            + "Given only the information above, what is the most salient"
            + " high-level questions we can ask about the human in"
            + " the statements to let him reflect back on his day? The question should be deep and reflective"
            + "It should be one question only"
            + "output format JSON with question key"
            #+ " Provide each question on a new line. \n\n"
        )

        return self.chain(prompt).run(observations=observations)


    def _get_mood_observations(self, session_id, postgres_connection, last_k = 3):  
        history = PostgresChatMessageHistory(
            connection_string=postgres_connection,
            session_id = session_id
        )

        human_messages = list(filter(lambda message: isinstance(message, HumanMessage), history.messages))[-last_k:]
        mood_observations = "\n".join([message.content for message in human_messages]) 
        
        return mood_observations