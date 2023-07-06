from __future__ import annotations

import re
from typing import Union

from langchain.agents.agent import AgentOutputParser
#from agents.goal_chat.prompt import FORMAT_INSTRUCTIONS
from langchain.agents.conversational.prompt import FORMAT_INSTRUCTIONS
from langchain.output_parsers.json import parse_json_markdown
from langchain.schema import AgentAction, AgentFinish, OutputParserException
import json

class GoalConvoOutputParser(AgentOutputParser):
    ai_prefix: str = "Final Answer"


    def parse_to_json(self, text):
        text = text.split(f"{self.ai_prefix}:")[-1].strip()
        
        lines = text.split('\n')  # split the text into lines
        json_array = []
        prefix_end = False
        is_sublist = False
        prefix = ""
        suffix = ""
        
        for line in lines:
            stripped_line = line.strip()  # remove leading/trailing white spaces
            if stripped_line:  # if the line is not empty
                if stripped_line[0].isdigit():  # if the line starts with a digit
                    is_sublist = True
                    prefix_end  = True
                    json_obj = {"content": stripped_line.split('. ', 1)[1], "tasks": []}  # create a new json object with the title
                    json_array.append(json_obj)  # append the new json object to the json array
                elif stripped_line[0] == '-':  # if the line starts with a '-'
                    prefix_end  = True
                    if is_sublist: 
                        json_obj = {"content": stripped_line[2:], "tasks": []}
                        json_array[-1]["tasks"].append(json_obj)  # append the step to the last json object in the json array
                    else: 
                        json_obj = {"content": stripped_line[2:], "tasks": []}
                        json_array.append(json_obj)
                else: 
                    if not prefix_end: 
                        prefix += stripped_line + "\n"
                    else: 
                        suffix += stripped_line + "\n"
            else: 
                if not prefix_end: 
                    prefix += "\n"
                else: 
                    suffix += "\n"
        formatted_list = json.dumps(json_array, indent=4)
        
        if formatted_list != "[]" or "": 
            return prefix.strip() + "\n\n" + formatted_list + "\n\n" + suffix.strip()   
        else:
            return prefix.strip() + suffix.strip()

    def get_format_instructions(self) -> str:
        return FORMAT_INSTRUCTIONS

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        if f"{self.ai_prefix}:" in text:
            return AgentFinish(
                {"output": self.parse_to_json(text)}, text
            )
        regex = r"Action: (.*?)[\n]*Action Input: (.*)"
        match = re.search(regex, text)
        if not match:
            raise OutputParserException(f"Could not parse LLM output: `{text}`")
        action = match.group(1)
        action_input = match.group(2)
        return AgentAction(action.strip(), action_input.strip(" ").strip('"'), text)

    @property
    def _type(self) -> str:
        return "conversational"
    
