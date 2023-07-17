from typing import Any, Optional, List
from langchain import LLMChain,  PromptTemplate
from langchain.llms import BaseLLM
from schema.goal import GoalInDB
from chains.goal_conversation_chain.prompt import PREFIX, CONVERSATION, SUFFIX
 
class GoalConversationChain(LLMChain):
    
    
    
    @classmethod
    def create_prompt(
        cls,
        goal: GoalInDB,
        prefix=PREFIX, 
        conversation=CONVERSATION, 
        suffix=SUFFIX,
        coach_name: str = "Hannah",
        user_name: str = "user",
        input_variables: Optional[List[str]] = None,
    ) -> PromptTemplate:
        """Create prompt in the style of Sales GPT agent"""
            
        milestone_strings = "\n".join([f"-> {milestone.content}" for milestone in goal.milestones])
        template = prefix.format(
            coach_name=coach_name, user_name=user_name, goal_description=goal.description, milestones=milestone_strings
        )
        begin = suffix.format(coach_name=coach_name)
        
        prompt = "\n\n".join([template, conversation, begin])
        
        if input_variables is None:
            input_variables = ["input", "conversation_history"]
        
        return PromptTemplate(template=prompt, input_variables=input_variables)
    
    @classmethod
    def from_llm_and_goal(cls, 
                          llm: BaseLLM, 
                          goal: GoalInDB,
                          prefix = PREFIX, 
                          conversation = CONVERSATION, 
                          suffix = SUFFIX,
                          coach_name="Hannah", 
                          user_name="user", 
                          verbose: bool = True, 
                          input_variables: Optional[List[str]] = None,
                          **kwargs: Any) -> LLMChain:
        """Get the response parser."""
        
        prompt = cls.create_prompt(
            goal, 
            prefix=prefix, 
            conversation=conversation,
            suffix=suffix,                       
            coach_name=coach_name,
            user_name=user_name,
            input_variables=input_variables
        )        
        
        return cls(prompt=prompt, llm=llm, verbose=verbose, **kwargs)
    
