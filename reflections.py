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

    def get_topics_of_reflection(self, last_k: int = 5): 
        pass

    def _get_mood_observations(self, postgres_connection, session_id, last_k: int = 5): 
        history = PostgresChatMessageHistory(
            connection_string=postgres_connection,
            session_id = session_id
        )
        human_messages = list(filter(lambda message: isinstance(message, HumanMessage), history.messages))
        print(human_messages)