from typing import Optional, List
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import StreamingStdOutCallbackHandler
from agents.cbt_conversation.prompt import PREFIX, SUFFIX
from langchain.prompts.chat import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain import LLMChain
from langchain.memory import ChatMessageHistory, ConversationBufferMemory
from checkins import generative_check_in


class CbtConversationAgent:
    llm = ChatOpenAI(streaming=True, temperature=0, model="gpt-3.5-turbo-16k" , verbose=True, callbacks=[StreamingStdOutCallbackHandler()])
    
    def create_prompt(self, system_message: str = PREFIX, human_message = SUFFIX, input_variables: Optional[List[str]]= None):
        messages = [
            SystemMessagePromptTemplate.from_template(system_message), 
            HumanMessagePromptTemplate.from_template(human_message)
        ]
        if input_variables is None:
            input_variables = ["technique", "username", "instruction", "context", "conversation_history", "input"]
        return ChatPromptTemplate(input_variables=input_variables, messages=messages)

    def get_agent(self, cId):
        prompt = self.create_prompt()
        memory = self.get_memory(cId)
        return LLMChain(llm=self.llm, prompt=prompt, memory=memory, verbose=True)
    
    
    def get_memory(self, cId):
        history = ChatMessageHistory()
        for message in generative_check_in.get_messages(cId): 
            history.add_message(message) 
        memory = ConversationBufferMemory(memory_key="conversation_history", chat_memory=history, input_key="input")
        return memory