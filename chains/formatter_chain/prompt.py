from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.prompts.prompt import PromptTemplate


templ1 = """
"""
# templ1 = """You are a smart assistant designed to assistant format its output before giving out the Final Answer. 
# Given a piece of text, your task is to identify if the text contains a list or not. 
# If it does contain a list, you should format the list as a Python list. In the case of sub-lists, 
# they should be formatted as dictionaries, effectively transforming the entire structure into a JSON array object. 
# It's important to note that the text preceding and trailing the list should remain unchanged and unformatted.

# Here are few examples that you can use for reference: 
# ```
# EXAMPLE 1: 
# "output":"The milestones for setting a daily limit for social media using and sticking to it are as follows:\n\n [
#     "Set a specific time limit for social meida usage each day.",
#     "Create a reminder to alert when the time limit is reached.",
#     "Disable notifications for social media apps.",
#     "Uninstall social media apps from your phone.",
#     "Find an accountability partner to help you stay on track."
# ]"

# EXAMPLE 2: 
# "output":"These milestones will help you establish a clear plan and take actionable steps towards achieving your goal. Let's break down each milestone 
# further and create smaller sub-milestones or tasks to make it more managable.\n\n [
#     {"set a specific time limit for social media usage per day": [
#         "Determine how much time you want to allocate for social media usage daily.",
#         "Consider your priorties and schedule to decide on reasonable limit."
#     ]},
#     {"create a reminder to alert when time limit is reached": [
#         "Use your phone's built-in alarm or time feature to set reminder",
#         "Choose a notification sound or vibration pattern that will grab your attention"
#     ]}
# ]"
# ```
# Remember the examples are just formatting reference examples!!! 
# """

templ2 = """Please format the following text:
----------------
{text}"""

PROMPT = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(templ1),
        HumanMessagePromptTemplate.from_template(templ2),
    ]
)