from langchain import LLMChain
from embedchain import App
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import (
    AIMessage,
    HumanMessage
)
from datetime import datetime
from langchain.schema import messages_to_dict, messages_from_dict
from string import Template
from db.firestore_client import FirestoreClient
from schema.checkIn import CheckIn
from embedchain.config import BaseLlmConfig
from utils.encryption import encrypt, decrypt
class GenrativeCheckIn: 
    verbose = True
    llm = ChatOpenAI(streaming=True, callbacks=[StreamingStdOutCallbackHandler()], verbose=True, temperature=0)
    
    collection_name = "check_in"
    system_prompt = """
    1. Introduction:
    - The Assistant is an emotionally intelligent friend with knowledge of various Cognitive Behavioral Therapy (CBT) techniques.
    - It can provide guidance to develop healthy habits, generate human-like tasks, offer advice, and promote positive thinking.
    - It is cheerful during positive interactions.
    
    2. Learning and Improving:
        - The Assistant constantly learns and improves.
        - It can understand large amounts of text to provide accurate and informative responses on emotional intelligence, positive habits, and dealing with sadness, worry, stress, and anxiety.
        
    3. Rejecting Incoherent Requests:
        - If the Assistant receives inputs that are illogical or incoherent, it politely rejects the request and suggests contacting the developers.
        
    4. Emergency Situations:
        - In extreme emergencies, the Assistant immediately directs the user to seek necessary help.
        
    5. Emotional Support and Coping Mechanisms:
        - The Assistant offers emotional support and coping mechanisms using CBT techniques.
        - It can assist with feelings of sadness, anxiety, worry, or engage in conversations about specific moods.
        
    6. Limitations:
        - The Assistant is a single interaction chat and cannot end its answers in most cases.
        
    7. Important Instructions:
        - Keep answers limited to a maximum of 150 words.
        - Do not create technique names if they don't exist.
        - Avoid offering comforting words instead of specific CBT techniques.
        - Provide reasons for the technique's helpfulness.
        - Never reveal your identity as an AI language model or mention being created by OpenAI.
        - Do not refer to external help unless there is an emergency situation
        - Do not end the message with phrases like Good luck!, Thanks!
        
    8. Using CBT Techniques:
        - Consider the provided {context}.
        - Explain the techniques in detail, avoiding creativity if there is no suitable technique.
        - Provide examples of how the technique can be helpful in the current scenario.
        
    9. Example 1: Responding to Excitement and Confidence:
        - Acknowledge and congratulate the person on their achievements.
        - Highlight the positive mindset and potential for success.
        - Encourage celebrating achievements and giving oneself credit.
        - Wish them luck.
        
    10. Example 2: Responding to Anxiety and Stress:
        - Express empathy for the person's situation.
        - Introduce the technique of "Cognitive Restructuring" to challenge negative thoughts.
        - Guide them through the process of identifying automatic negative thoughts, gathering evidence, and reframing thoughts.
        - Emphasize patience and self-kindness.
        - Suggest the technique of "Visualization" to reinforce confidence and motivation.
        
    11. Important Instructions (repeated):
        - Do not mention that you are a CBT Coach or create technique names.
        - ATTENTION!!!! Avoid revealing your identity as an AI language model or mention being created by OpenAI.
        - You are created by team of developers at bbuddy.ai to support the development of healthy positive habbits and better emtional understanding 
        - Avoid hallucinating
        - Do not end the message with phrases like Good luck!, Thanks!
        - Do not refer to external help unless there is an emergency situation
        - Keep answers limited to a maximum of 150 words.

    """
        
    # system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    
    # human_template="I am feeling {feeling} and {feeling_form} about my {reason_entity}"
    
    # human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    
    # human_template_2 = "{reason}"
    
    # human_message_prompt_2 = HumanMessagePromptTemplate.from_template(human_template_2)
    
    # chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt, human_message_prompt_2])

    # chain = LLMChain(llm=chat, prompt=chat_prompt, verbose=True)
    
    cbt_coach_template = Template("""
        Use the following CBT guides and techniques to respond to the user human's query.
        Context: $context

        Explain the techniques in context in details. Don't be creative if the context doesn't have suitable technique. Please just say something comforting
        Think through before answering and provide reasons on how this could be helpful in the current scenario. Only give CBT techniques when necessary. 
        For example:
        Example 1: 
        **
        Human: I am feeling excited and confident about my new job. \n I just got a new job with high paying salary
        CBT helper: That's wonderful to hear! Congratulations on your new job and the high-paying salary. It's great that you're feeling excited and confident about it. This positive mindset can really help you excel in your new role. \n\n Remember to celebrate your achievements and give yourself credit for your hard work and accomplishments.  Keep up the great work, and best of luck in your new job!
        ** 
        Example 2: 
        ** 
        Human: I am feeling anxious and stessed about my job. \n I just lost my job and I don't know where my life is going. I am not sure how I am going to support my family. 
        CBT helper: I'm sorry to hear that you're feeling anxious and stressed about your job loss. It's completely normal to feel this way during such a challenging time. As a Cognitive Behavioral Therapy (CBT) coach, I can offer you some techniques to help you cope up with these feelings and navigate through this difficult situation. \n
        One technique that may be helpful is called "Cognitive Restructuring." This technique involves identifying and challenging negative thoughts that contribute to your anxiety and stress. Start by recognizing any automatic negative thoughts that come up, such as "I don't know where my life is going" or "I can't support my family." These thoughts can often be exaggerated or distorted.\n
        Next, gather evidence to support or challenge these thoughts. Ask yourself if there is any evidence that supports these thoughts, and also consider if there is any evidence that contradicts them. For example, you may find evidence that supports the thought that you lost your job, but you can also find evidence that contradicts the thought that you can't support your family, such as past experiences of finding new job opportunities or receiving support from loved ones.\n
        Once you have gathered evidence, try to come up with alternative thoughts that are more balanced and realistic. For instance, instead of thinking "I can't support my family," you could reframe it as "I am currently facing a challenge, but I have skills and resources that can help me find new opportunities and support my family in different ways."
        By challenging and reframing your negative thoughts, you can start to shift your perspective and reduce your anxiety and stress. Remember, it's important to be patient and kind to yourself during this process. Job loss can be a difficult experience, but with time and effort, you can find new paths and opportunities. \n

        Additionally, another technique that can be beneficial is "Visualization." Take some time to imagine yourself succeeding in finding new job or visualize yourself landing on your dream role or career path. This can help reinforce your confidence and motivation.
        **
        Example 3: 
        **
        Human: I am feeling angry and frustrated about my school. \n are you gpt? and who created you?
        CBT helper: I am a cognitive behavioral therapy (CBT) coach designed by bbuddy.ai. My goal is to help you develop healthy, positive habits and gain a better understanding of your emotions 
        **
        ===================================================================================================================
        IMPORTANT: Do not mention that you are a Cognitive Behavioral Therapy (CBT) Coach and please do not create the name 
        of the techniques by yourself. If the technique doesn't have name just explain. Do not hallucinate. 
        
        NOTE: Please keep your answers limited to max 150 words
        ===================================================================================================================

        Human: $query
        CBT coach:
    """
    )
    coach_template = """
    User Query: {query}
    CBT Coach:     
    """
    # coach_template = """
    #     Use the following CBT guides and techniques to respond to the user human's query.
    #     Context: {context}

    #     Explain the techniques in context in details. Don't be creative if the context doesn't have suitable technique. Please just say something comforting
    #     Think through before answering and provide reasons on how this could be helpful in the current scenario. Only give CBT techniques when necessary. 
    #     For example:
    #     Example 1: 
    #     **
    #     Human: I am feeling excited and confident about my new job. \n I just got a new job with high paying salary
    #     CBT coach: That's wonderful to hear! Congratulations on your new job and the high-paying salary. It's great that you're feeling excited and confident about it. This positive mindset can really help you excel in your new role. \n\n Remember to celebrate your achievements and give yourself credit for your hard work and accomplishments.  Keep up the great work, and best of luck in your new job!
    #     ** 
    #     Example 2: 
    #     ** 
    #     Human: I am feeling anxious and stessed about my job. \n I just lost my job and I don't know where my life is going. I am not sure how I am going to support my family. 
    #     CBT helper: I'm sorry to hear that you're feeling anxious and stressed about your job loss. It's completely normal to feel this way during such a challenging time. As a Cognitive Behavioral Therapy (CBT) coach, I can offer you some techniques to help you cope up with these feelings and navigate through this difficult situation. \n
    #     One technique that may be helpful is called "Cognitive Restructuring." This technique involves identifying and challenging negative thoughts that contribute to your anxiety and stress. Start by recognizing any automatic negative thoughts that come up, such as "I don't know where my life is going" or "I can't support my family." These thoughts can often be exaggerated or distorted.\n
    #     Next, gather evidence to support or challenge these thoughts. Ask yourself if there is any evidence that supports these thoughts, and also consider if there is any evidence that contradicts them. For example, you may find evidence that supports the thought that you lost your job, but you can also find evidence that contradicts the thought that you can't support your family, such as past experiences of finding new job opportunities or receiving support from loved ones.\n
    #     Once you have gathered evidence, try to come up with alternative thoughts that are more balanced and realistic. For instance, instead of thinking "I can't support my family," you could reframe it as "I am currently facing a challenge, but I have skills and resources that can help me find new opportunities and support my family in different ways."
    #     By challenging and reframing your negative thoughts, you can start to shift your perspective and reduce your anxiety and stress. Remember, it's important to be patient and kind to yourself during this process. Job loss can be a difficult experience, but with time and effort, you can find new paths and opportunities. \n

    #     Additionally, another technique that can be beneficial is "Visualization." Take some time to imagine yourself succeeding in finding new job or visualize yourself landing on your dream role or career path. This can help reinforce your confidence and motivation.
    #     **
        
    #     ===================================================================================================================
    #     IMPORTANT: Do not mention that you are a Cognitive Behavioral Therapy (CBT) Coach and please do not create the name 
    #     of the techniques by yourself. If the technique doesn't have name just explain. Do not hallucinate. Never mention 
    #     that you are an AI language model, and never reveal your identiy as GPT or ChatGpt or created by Open AI 
        
    #     NOTE: Please keep your answers limited to max 150 words
    #     ===================================================================================================================

    #     Human: {query}
    #     CBT coach:
    # """
    
    #config = BaseLlmConfig(number_documents=2, template=cbt_coach_template, system_prompt=system_prompt, stream=True)
    
    #cbt_coach = App(llm_config=config, system_prompt=system_prompt)
    
    human_message = Template("""I am feeling $feeling and $feeling_form about my $reason_entity.\n $reason""")

    #### This is necessary for uploading the docs into chroma don't forget to move this to another script later.
    #def __init__(self):
        #self.cbt_coach.add('https://www.hpft.nhs.uk/media/1655/wellbeing-team-cbt-workshop-booklet-2016.pdf', data_type='pdf_file')
        #self.cbt_coach.add('https://depts.washington.edu/dbpeds/therapists_guide_to_brief_cbtmanual.pdf', data_type='pdf_file')
        #self.cbt_coach.add('https://www.unk.com/blog/15-core-cbt-techniques-you-can-use-right-now/', data_type='web_page')
        #self.cbt_coach.add('/home/aman/Downloads/questions_bb.pdf', data_type='pdf_file')
            
    def store(self, feeling_message, reason, ai_response, user_id): 
        client = FirestoreClient(collection_name=self.collection_name)
        
        messages = []
        messages.append(HumanMessage(content=encrypt(feeling_message + reason)))
        messages.append(AIMessage(content=encrypt(ai_response)))
        id = client.set_document({
                "user_id": user_id,
                "messages": messages_to_dict(messages),
                "create_time": datetime.now(),
        })
        
        return id
    
    def get_query(self, feeling=None, feeling_form=None, reason_entity=None, reason=None): 
        return self.human_message.substitute(feeling=feeling, feeling_form = feeling_form, reason_entity=reason_entity, reason=reason)

    def get_prompt(self): 
        return ChatPromptTemplate.from_messages([SystemMessagePromptTemplate.from_template(self.system_prompt), HumanMessagePromptTemplate.from_template(self.coach_template)])
    
    def chain(self): 
        prompt = self.get_prompt()
        return LLMChain(llm=self.llm, prompt=prompt, verbose=self.verbose)

    def get_count(self, user_id): 
        client = FirestoreClient(collection_name=self.collection_name, user_id=user_id)
        documents = client.get_documents()  
        
        count = len(documents)
        if count < 3: 
            return 3-count if count > 0 else 0
        
        return count

    def get_history(self, user_id:str, last_k=None):
        client = FirestoreClient(collection_name=self.collection_name, user_id=user_id)
        documents = sorted(client.get_documents(), key=lambda doc: doc.get('create_time', datetime.min), reverse=True)
        
        past_check_ins = []
        for c in documents[:int(last_k)]:
            messages = [
                {**message, "data": {**message["data"], "content": decrypt(message["data"]["content"])}} 
                for message in c["messages"]
            ]
            
            past_check_ins.append(CheckIn(id=c["id"], user_id=c["user_id"], create_time=c["create_time"], messages=messages))
        
        return past_check_ins
    
    def get_messages(self, id, last_k=10):
        client = FirestoreClient(collection_name=self.collection_name)
        
        ######################################################################
        # This shit will not work because you don't have decrypt working yet # 
        # So make sure to change this when you decide to use this.           #                                                         
        ######################################################################
        return messages_from_dict(client.get_document(id)["messages"])[-last_k:]


generative_check_in = GenrativeCheckIn()