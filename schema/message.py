# from langchain.schema import BaseMessage, HumanMessage, SystemMessage, AIMessage, ChatMessage
# from typing import List
# import json


# def convertJsonToList(data): 
#     splitted_string = data["content"].split("\n\n[")
#     if len(splitted_string) <= 1:
#         return data; 
    
#     prefix = splitted_string[0]
#     rest = "".join(splitted_string[1:])
#     items_str, suffix = rest.rsplit("\n]", 1)

#     # Convert items string to a list of dictionaries
#     items = json.loads("[" + items_str + "]")

#     # Convert items to a formatted bullet list
#     bullet_list = ""
#     for i, item in enumerate(items, start=1):
#         content = item["content"]
#         tasks = item["tasks"]
#         bullet_list += f"{i}. {content}\n"
#         if tasks:
#             for task in tasks:
#                 bullet_list += f"- {task}\n"

#     # Print the resulting bullet list
#     data["content"] = f"{prefix}\n\n{bullet_list}{suffix}"
#     return data

# def _message_from_dict(message: dict) -> BaseMessage:
#     _type = message["type"]
#     if _type == "human":
#         return HumanMessage(**message["data"])
#     elif _type == "ai":
#         return AIMessage(**convertJsonToList(message["data"]))
#     elif _type == "system":
#         return SystemMessage(**message["data"])
#     elif _type == "chat":
#         return ChatMessage(**message["data"])
#     else:
#         raise ValueError(f"Got unexpected type: {_type}")

# def messages_from_dict(messages: List[dict]) -> List[BaseMessage]:
#     """Convert a sequence of messages from dicts to Message objects.

#     Args:
#         messages: Sequence of messages (as dicts) to convert.

#     Returns:
#         List of messages (BaseMessages).
#     """
#     return [_message_from_dict(m) for m in messages]