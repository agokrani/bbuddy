"""An agent designed to hold a conversation regarding goal and milestones in addition to using tools."""
from __future__ import annotations


from langchain.chat_models import ChatOpenAI
from langchain.callbacks import StdOutCallbackHandler
from langchain.agents import AgentExecutor, load_tools, ConversationalAgent
from agents.goal_chat.output_parser import GoalConvoOutputParser
from langchain.memory import (
    PostgresChatMessageHistory, 
    ConversationSummaryBufferMemory
)
from agents.goal_chat.prompt import (
    FORMAT_INSTRUCTIONS,
    system_template, 
    SUFFIX
)
from schema.goal import GoalInDB
#from chains.formatter_chain.base import FormatterChain


class GoalConversationalAgent:
    llm = ChatOpenAI(temperature=0.5, model="gpt-3.5-turbo-16k", streaming=True, verbose=True, callbacks=[StdOutCallbackHandler()])
    
    # formatter_chain = FormatterChain.from_llm(llm=llm, verbose=True)
    
    tools = load_tools(["google-serper"], llm=llm)
   
    def get_agent(self, goal: GoalInDB, connection_string: str): 
        milestone_strings = "\n".join([f"-> {milestone.content}" for milestone in goal.milestones])    
        system_message = system_template.format(goal_description=goal.description, milestones=milestone_strings)
        
        # TODO: Fix this message history -> Old comments 
        #message_history = GoalChatHistoryManager(session_id=str(goal.id), connection_string=connection_string, table_name="test_store") -> Old parsing history
        
        message_history = PostgresChatMessageHistory(session_id=str(goal.id), connection_string=connection_string, table_name="test_store")
        memory = ConversationSummaryBufferMemory(llm=self.llm, memory_key="chat_history", max_token_limit=1000, chat_memory=message_history)
        
        agent = ConversationalAgent.from_llm_and_tools(llm=self.llm, tools=self.tools, prefix=system_message, suffix=SUFFIX, format_instructions=FORMAT_INSTRUCTIONS, output_parser=GoalConvoOutputParser(), ai_prefix="Final Answer")
        agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=self.tools, verbose=True, memory=memory, handle_parsing_errors="Check your output and make sure it conforms!", max_iterations=4)
       
        return agent_executor