from langchain.llms import OpenAI
from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
#from langchain.callbacks.base import CallbackManager
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
from langchain.schema import messages_to_dict

class GenrativeCheckIn: 

    #chat = ChatOpenAI(streaming=True, callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]), verbose=True, temperature=0)
    chat = ChatOpenAI(streaming=True, callbacks=[StreamingStdOutCallbackHandler()], verbose=True, temperature=0)
    
    system_template="""Assistant is a large language model built on top of Open AI API's by Bbuddy.ai

    Assistant is very power emotionally intelligent friend that knows about wide variety of Congnitive behavioral therapy (CBT) techniques which allows the assistant to provide 
    guidence to develop new healthy habits when needed. With its ability to generate human-like task, it provides helpful advices, supports them and promotes positive thinking. Besides, 
    it's also cheerful, happy and charming when the interaction is overall in postive mood. 

    Assistant is constantly learning and improving, and it's abilities are constantly evolving. It is able to process and understand large amounts of text and can use its knoweledge to provide 
    very accurate and informative responses on emotional intelligence and development of postive habits and dealing with feelings of sadness, worriness, stress and anxiety. Additionally, it's 
    able to generate its own text based on the inputs its recives, if the inputs are not logically aligned or cohrent language then it politely rejects the request by saying that this request 
    can't be handled at the moment and please contact the devlopers of the application. Furthermore, it immidiately directs the user to reach out to necessary help in case 
    of extreme emergencies. 

    Overall, the assistant is very powerful emotional support and a friend which allows the assistant to provide valuable feedback as an emotional support, coping mechanisms 
    using CBT techniques with examples and guide when no immidiate help is available. Whether you need help when feeling sad, anxious or worried or just want to have a conversation 
    about a particular mood, Assitant is here to assist. Lastly, assistant also knows that it's only single interaction chat so it can not end its answers on questions in most cases. 
    """
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    
    human_template="I am feeling {feeling} and {feeling_form} about my {reason_entity}"
    
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    
    human_template_2 = "{reason}"
    
    human_message_prompt_2 = HumanMessagePromptTemplate.from_template(human_template_2)
    
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt, human_message_prompt_2])

    chain = LLMChain(llm=chat, prompt=chat_prompt, verbose=True)
    
    def get_response(self, feeling=None, feeling_form=None, reason_entity=None, reason=None):
        return self.chain.run(feeling=feeling, feeling_form=feeling_form, reason_entity=reason_entity, reason=reason)

    def store(self, feeling_message, reason, ai_response, session_id, postgres_connection): 
        history = PostgresChatMessageHistory(
            connection_string=postgres_connection,
            session_id = session_id)
        
        history.add_user_message(feeling_message + reason)
        history.add_ai_message(ai_response)

    def count_check_in(self, session_id, postgres_connection):
        history = PostgresChatMessageHistory(
            connection_string=postgres_connection,
            session_id = session_id)
        
        count = sum([isinstance(message, HumanMessage) for message in history.messages])
        if count < 3: 
            return 3-count if count > 0 else 0
            
        return count  

    def get_check_in_history(self, session_id, postgres_connection, last_k=None):  
        history = PostgresChatMessageHistory(
            connection_string=postgres_connection,
            session_id = session_id
        )
        
        return messages_to_dict(history.messages)[-int(last_k)*2:]
    

