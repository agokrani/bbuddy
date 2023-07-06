"""An agent designed to hold a conversation regarding goal and milestones in addition to using tools."""
from __future__ import annotations

from typing import Any, List, Optional, Sequence

from pydantic import Field
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import StdOutCallbackHandler
from langchain.agents import Tool, AgentExecutor, load_tools, ConversationalAgent
from langchain.agents.agent import Agent, AgentOutputParser
from langchain.agents.agent_types import AgentType
from agents.goal_chat.output_parser import GoalConvoOutputParser
from langchain.agents.utils import validate_tools_single_input
from langchain.base_language import BaseLanguageModel
from langchain.callbacks.base import BaseCallbackManager
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate, MessagesPlaceholder
from langchain.tools.base import BaseTool
from langchain.memory import (
    ConversationBufferMemory, 
    CombinedMemory, 
    ConversationSummaryMemory, 
    PostgresChatMessageHistory, 
    ConversationBufferWindowMemory,
    ConversationSummaryBufferMemory
)
from db.goal_chat_history_manager import GoalChatHistoryManager
from agents.goal_chat.prompt import (
    FORMAT_INSTRUCTIONS,
    system_template, 
    SUFFIX
)
# from agents.goal_chat.prompt import (
#     FORMAT_INSTRUCTIONS,
#     SYSTEM_MESSAGE_PREFIX, 
#     SYSTEM_MESSAGE_SUFFIX, 
#     HUMAN_MESSAGE
# )
from schema.goal import GoalInDB
from chains.formatter_chain.base import FormatterChain
from langchain.chains import SequentialChain


class GoalConversationalAgent:
    llm = ChatOpenAI(temperature=0.5, model="gpt-3.5-turbo-0613", streaming=True, verbose=True, callbacks=[StdOutCallbackHandler()])
    
    formatter_chain = FormatterChain.from_llm(llm=llm, verbose=True)
    
    tools = load_tools(["google-serper"], llm=llm)
   
    def get_agent(self, goal: GoalInDB, connection_string: str): 
        milestone_strings = "\n".join([f"-> {milestone.content}" for milestone in goal.milestones])    
        system_message = system_template.format(goal_description=goal.description, milestones=milestone_strings)
        
        # TODO: Fix this message history
        message_history = GoalChatHistoryManager(session_id=str(goal.id), connection_string=connection_string, table_name="test_store")
        
        memory = ConversationSummaryBufferMemory(llm=self.llm, memory_key="chat_history", max_token_limit=1000, chat_memory=message_history)
        
        agent = ConversationalAgent.from_llm_and_tools(llm=self.llm, tools=self.tools, prefix=system_message, suffix=SUFFIX, format_instructions=FORMAT_INSTRUCTIONS, output_parser=GoalConvoOutputParser(), ai_prefix="Final Answer")
        agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=self.tools, verbose=True, memory=memory, handle_parsing_errors="Check your output and make sure it conforms!", max_iterations=4)
       
        return agent_executor