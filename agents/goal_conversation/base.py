
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import StdOutCallbackHandler
from langchain.memory import (
    PostgresChatMessageHistory, 
    ConversationSummaryBufferMemory,
    ConversationSummaryMemory,
    ConversationBufferWindowMemory
)
from langchain.memory.chat_message_histories import FirestoreChatMessageHistory
from schema.goal import GoalInDB
from chains import GoalConversationChain

class GoalConversationAgent:
    llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo-16k", streaming=True, verbose=True, callbacks=[StdOutCallbackHandler()])
    
    def get_agent(self, goal: GoalInDB, user_id, user_name="user", coach_name="Hannah"): 
        #message_history = PostgresChatMessageHistory(session_id=str(goal.id), connection_string=connection_string, table_name="test_store")
        #memory = ConversationSummaryBufferMemory(llm=self.llm, ai_prefix=coach_name, human_prefix=user_name, memory_key="conversation_history", max_token_limit=1000, chat_memory=message_history)
        #memory = ConversationSummaryMemory(llm=self.llm, memory_key="conversation_history", summarize_step=5, chat_memory=message_history)
        
        message_history = FirestoreChatMessageHistory(session_id=str(goal.id), user_id=str(user_id), collection_name="test_store")
        memory = ConversationBufferWindowMemory(ai_prefix=coach_name, human_prefix=user_name, memory_key="conversation_history", chat_memory=message_history)
        chain = GoalConversationChain.from_llm_and_goal(llm=self.llm, goal=goal, coach_name=coach_name, user_name=user_name, memory=memory)        
        
        return chain
