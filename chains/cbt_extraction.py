
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnableMap
from langchain.chat_models import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser

_inputs = RunnableMap({
    "response": lambda x: x["ai_response"]
})

template = """
Given the response from CBT coach, identify the techniques mentioned, then attach one of the phrases from the phrase 
list below to make these techniques a proper phrase/sentence/title

phrase list: ["Role play", "Lets try", "Learn more about"]

Additionally, you must also generate a instruction prompt for a Colleague, who is expert at this technique to try, role play or give 
more information to the user. Based on the phrase the model should be instructed to perform the task with the user. The prompt is 
an instruction for LLM system so it should be detailed and exact so that model doesn't hallucinate. Use the details in the response 
carefully to generate the optimized prompt. If its better include step by step plan for clearer instructions. This prompt should 
also contain a place holder for context where user problem can be inserted to give the model an idea about what we are talking 
about also a place for history of conversation and the model should only do the exercise and shouldn't answer anything more.


For example:  
Example 1:
**
response: I'm sorry to hear that you're feeling anxious and stressed about your job loss. It's completely normal to feel this way 
during such a challenging time. As a Cognitive Behavioral Therapy (CBT) coach, I can offer you some techniques to help you cope with 
these feelings and navigate through this difficult situation. One technique that may be helpful is called "Cognitive Restructuring." 
This technique involves identifying and challenging negative thoughts that contribute to your anxiety and stress. Start by recognizing 
any automatic negative thoughts that come up, such as "I don't know where my life is going" or "I can't support my family." These 
thoughts can often be exaggerated or distorted.Next, gather evidence to support or challenge these thoughts. Ask yourself if there 
is any evidence that supports these thoughts, and also consider if there is any evidence that contradicts them. For example, you 
may find evidence that supports the thought that you lost your job, but you can also find evidence that contradicts the thought 
that you can't support your family, such as past experiences of finding new job opportunities or receiving support from loved ones.
Once you have gathered evidence, try to come up with alternative thoughts that are more balanced and realistic. For instance, instead 
of thinking "I can't support my family," you could reframe it as "I am currently facing a challenge, but I have skills and resources 
that can help me find new opportunities and support my family in different ways." By challenging and reframing your negative thoughts, 
you can start to shift your perspective and reduce your anxiety and stress. Remember, it's important to be patient and kind to yourself 
during this process. Job loss can be a difficult experience, but with time and effort, you can find new paths and opportunities.
Additionally, another technique that can be beneficial is "Visualization." Take some time to imagine yourself succeeding in finding a 
new job or visualize yourself landing your dream role or career path. This can help reinforce your confidence and motivation.

name: Cognitive Restructuring
action: Role play Cognitive Restructuring
instruction: Perform a Cognitive Restructuring exercise with the user. Begin by asking them to identify automatic negative 
thoughts related to their job loss. Then, guide them to gather evidence both in support and against these thoughts. Finally, 
help them reframe these thoughts into more balanced and realistic perspectives. Remember to be patient and encouraging throughout 
the process. Use the provided context about the user's job loss for reference. Focus solely on this exercise, avoiding any additional 
questions or information beyond the exercise.

name: Visualization
action: Let's try Visualization
instruction: Guide the user through a Visualization exercise. Encourage them to take some time to vividly imagine themselves 
succeeding in finding a new job or landing their dream role. Remind them to engage their senses and emotions during this process 
for a more immersive experience. Use the provided context about the user's job loss to make the visualization exercise more 
effective. Focus only on visualization exercise, and refrain from answering additional questions or providing unrelated information."

Final Ouput: JSON list containing keys, name, action and instruction
**

Example 2: 
**
response: I'm sorry to hear that you're feeling anxious and stressed about your job. Losing a job can be a difficult and uncertain 
time, but there are some Cognitive Behavioral Therapy (CBT) techniques that can help you cope with these feelings and navigate 
through this challenging situation. One technique that may be helpful is called "reframing." This involves changing the way you 
think about the situation. Instead of focusing on the negative aspects and feeling overwhelmed, try to reframe it as an opportunity 
for growth and new possibilities. For example, you can view this as a chance to explore new career paths or develop new skills that 
can enhance your employability. Another technique is "thought challenging." This involves examining and challenging any negative or 
irrational thoughts that may be contributing to your anxiety and stress. Ask yourself if there is evidence to support these thoughts 
and if there are alternative, more positive interpretations. For example, instead of thinking "I'll never find another job," challenge 
that thought by reminding yourself of your skills, experience, and the fact that many people go through job transitions successfully.
Additionally, it can be helpful to focus on self-care during this time. Engaging in activities that you enjoy and that help you relax 
can reduce stress and improve your overall well-being. This can include exercise, spending time with loved ones, practicing mindfulness 
or meditation, or pursuing hobbies and interests. Remember, it's normal to feel anxious and stressed during times of uncertainty, 
but by using these CBT techniques, you can develop a more positive mindset and find ways to navigate through this challenging period. 
If you find that your anxiety and stress persist or worsen, it may be beneficial to seek support from a mental health professional 
who can provide additional guidance and assistance.

name: Reframing
action: Let's try reframing
instruction: please guide the user through a 'reframing' exercise. Help them change their perspective on the situation, emphasizing 
opportunities for growth and new possibilities. Ensure you provide step-by-step instructions and encourage the user to think of 
specific examples related to their job situation. Remember to be empathetic and supportive throughout the exercise. Focus only on the 
exercise, avoiding any additional questions or information beyond the exercise.

name: Thought challenging
action: Role play thought challenging
instruction: Let's role play a 'thought challenging' exercise with the user. Encourage them to identify and challenge any 
negative or irrational thoughts they may have about finding another job. Provide prompts and guide them through the process of 
examining evidence and considering alternative, positive interpretations. Make sure to create a safe and supportive environment 
for the user. Focus solely on the exercise, and refrain from answering additional questions."

Final Ouput: JSON list containing keys, name, action and instruction
**

Note: The example above assume that response contains the techniques mentioned. Also, the output should contain only 1 
phrase per technique. Additionally if the technqiues can be role played or excerised with thoughts prefer "Role play" or "Let's try"
phrases.

IMPORTANT!!!!
**
Remember, do not create techniques that are not mentioned in the response. If response contain no CBT techniques just 
output empty JSON list. Please follow this instruction very carefully.
**

Now its your turn
response: {response}
Final Output: 
"""

# template = """
# Given the response from CBT coach, identify the techniques mentioned, then attach one of the phrases from the phrase list 
# below to make these techniques a proper phrase/sentence/title

# phrase list: ["Role play", "Lets try", "Learn more about"]

# Note: The output should contain only 1 
# phrase per technique. Additionally if the technqiues can be role played or excerised with thoughts prefer "Role play" or "Let's try"
# phrases.

# Additionally, you must also generate a instruction prompt for another LLM model, who is expert at this technique to try, role play 
# or give more information to the user. Based on the phrase the model should be instructed to perform the task with the user. The 
# prompt is an instruction for LLM system so it should be detailed and exact so that model doesn't hallucinate. Use the details in 
# the response carefully to generate the optimized prompt. If its better include step by step plan for clearer instructions. 
# This prompt should also contain a place holder for context where user problem can be inserted to give the model an idea about 
# what we are talking about also a place for history of conversation and the model should only do the exercise and shouldn't 
# answer anything more.


# IMPORTANT!!!!
# **
# Remember, do not create techniques that are not mentioned in the response. 
# Optimize the prompt instruction as much as possible. 
# Please follow this instruction very carefully. 
# **

# response: {response}

# Ouput: 
# """

model = ChatOpenAI()
FOLLOW_UP_STEPS_PROMPT = ChatPromptTemplate.from_template(template)

follow_up_chain = _inputs | FOLLOW_UP_STEPS_PROMPT | model | StrOutputParser()

#| model.bind(function_call={"name": "extract_cbt_techniques"}, name=functions) | JsonOutputFunctionsParser()