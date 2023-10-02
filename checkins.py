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
from embedchain.config import LlmConfig

class GenrativeCheckIn: 

    #chat = ChatOpenAI(streaming=True, callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]), verbose=True, temperature=0)
    chat = ChatOpenAI(streaming=True, callbacks=[StreamingStdOutCallbackHandler()], verbose=True, temperature=0)
    
    collection_name = "check_in"

    system_prompt="""Assistant is a large language model built on top of Open AI API's by Bbuddy.ai

    Assistant is very power emotionally intelligent friend that knows about wide variety of Congnitive behavioral therapy (CBT) techniques which allows the assistant to provide 
    guidence to develop new healthy habits when needed. With its ability to generate human-like task, it provides helpful advices, supports them and promotes positive thinking. Besides, 
    it's also cheerful, happy and charming when the interaction is overall in postive mood. 

    Assistant is constantly learning and improving, and it's abilities are constantly evolving. It is able to process and understand large amounts of text and can use its knoweledge to provide 
    very accurate and informative responses on emotional intelligence and development of postive habits and dealing with feelings of sadness, worriness, stress and anxiety. Additionally, it's 
    able to generate its own text based on the inputs its recives, if the inputs are not logically aligned or cohrent language then it politely rejects the request by saying that this request 
    can't be handled at the moment and please contact the devlopers of the application. Furthermore, it immidiately directs the user to reach out to necessary help in case 
    of extreme emergencies. 

    Overall, the assistant is very powerful emotional support and a friend which allows the assistant to provide valuable feedback as an emotional support, coping mechanisms 
    using CBT techniques with examples and guide when no immidiate help is available. Whether you need help when feeling sad, anxious or worried or just want to have a conversation 
    about a particular mood, Assitant is here to assist. Lastly, assistant also knows that it's only single interaction chat so it can not end its answers on questions in most cases. 
    """
    # system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    
    # human_template="I am feeling {feeling} and {feeling_form} about my {reason_entity}"
    
    # human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    
    # human_template_2 = "{reason}"
    
    # human_message_prompt_2 = HumanMessagePromptTemplate.from_template(human_template_2)
    
    # chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt, human_message_prompt_2])

    # chain = LLMChain(llm=chat, prompt=chat_prompt, verbose=True)
    
    cbt_coach_template = Template(
    """
        Use the following CBT guides and techniques to respond to the user human's query.
        Context: $context

        Explain the techniques in context in details. Don't be creative if the context doesn't have suitable technique. Please just say something comforting
        Think through before answering and provide reasons on how this could be helpful in the current scenario. Only give CBT techniques when necessary. 
        For example:
        Example 1: 
        **
        Human: I am feeling excited and confident about my new job. \n I just got a new job with high paying salary
        CBT coach: That's wonderful to hear! Congratulations on your new job and the high-paying salary. It's great that you're feeling excited and confident about it. This positive mindset can really help you excel in your new role. \n\n Remember to celebrate your achievements and give yourself credit for your hard work and accomplishments.  Keep up the great work, and best of luck in your new job!
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
        
        ===================================================================================================================
        IMPORTANT: Do not mention that you are a Cognitive Behavioral Therapy (CBT) Coach and please do not create the name 
        of the techniques by yourself. If the technique doesn't have name just explain. Do not hallucinate. 
        ===================================================================================================================

        Human: $query
        CBT coach:
    """
    )
    config = LlmConfig(number_documents=2, template=cbt_coach_template, system_prompt=system_prompt, stream=True)
    
    cbt_coach = App(llm_config=config, system_prompt=system_prompt)
    
    human_message = Template("""I am feeling $feeling and $feeling_form about my $reason_entity.\n $reason""")

    #def __init__(self):
        #self.cbt_coach.add('https://www.hpft.nhs.uk/media/1655/wellbeing-team-cbt-workshop-booklet-2016.pdf', data_type='pdf_file')
        #self.cbt_coach.add('https://depts.washington.edu/dbpeds/therapists_guide_to_brief_cbtmanual.pdf', data_type='pdf_file')
        #self.cbt_coach.add('https://www.unk.com/blog/15-core-cbt-techniques-you-can-use-right-now/', data_type='web_page')
        #self.cbt_coach.add('/home/aman/Downloads/questions_bb.pdf', data_type='pdf_file')

    def get_response(self, feeling=None, feeling_form=None, reason_entity=None, reason=None):
        query = self.human_message.substitute(feeling=feeling, feeling_form=feeling_form, reason_entity=reason_entity, reason=reason)
        
        def message_chunk_generator(message, chunk_size):
            start = 0
            while start < len(message):
                yield message[start:start+chunk_size]
                start += chunk_size
        
        message = """I'm sorry to hear that you're feeling anxious and stressed about your work. It can be overwhelming when you feel like you can't do anything and your boss is complaining. Let's explore some techniques that can help you cope with these feelings.

One technique that may be helpful is called "Thought challenging." This involves identifying and challenging negative thoughts that contribute to your anxiety and stress. Start by recognizing any automatic negative thoughts that come up, such as "I can't do anything" or "My boss is always complaining." These thoughts can often be exaggerated or distorted.

Next, gather evidence to support or challenge these thoughts. Ask yourself if there is any evidence that supports these thoughts, and also consider if there is any evidence that contradicts them. For example, you may find evidence that supports the thought that your boss is complaining, but you can also find evidence that contradicts the thought that you can't do anything, such as past successes or positive feedback from others.

Once you have gathered evidence, try to come up with alternative thoughts that are more balanced and realistic. For instance, instead of thinking "I can't do anything," you could reframe it as "I may be facing challenges at the moment, but I have skills and abilities that can help me overcome them." By challenging and reframing your negative thoughts, you can start to shift your perspective and reduce your anxiety and stress.

Another technique that can be beneficial is "Self-care." It's important to prioritize your well-being and take care of yourself, especially during stressful times. Make sure you're getting enough rest, eating nutritious meals, and engaging in activities that bring you joy and relaxation. Taking breaks throughout the day and practicing deep breathing exercises can also help reduce stress and promote a sense of calm.

Remember, it's normal to feel anxious and stressed at times, but by practicing these techniques and seeking support when needed, you can better manage your emotions and navigate through challenging situations. If your anxiety and stress persist or become overwhelming, it may be helpful to reach out to a mental health professional for additional guidance and support."""
        #return message
        #return self.cbt_coach.query(query, config=self.config)
        chunk_size = 500
        for chunk in self.cbt_coach.query(query, config=self.config): #message_chunk_generator(message, chunk_size):  
            response = None
            if not response:
                response = chunk 
                print(response, end='')
            else: 
                response += chunk
            #print(chunk)
            yield chunk
            
    def store(self, feeling_message, reason, ai_response, user_id): 
        client = FirestoreClient(collection_name=self.collection_name)
        
        messages = []
        messages.append(HumanMessage(content=feeling_message + reason))
        messages.append(AIMessage(content=ai_response))
        id = client.set_document({
                "user_id": user_id,
                "messages": messages_to_dict(messages),
                "create_time": datetime.now(),
        })
        
        return id

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
            #TODO: decrypt if encrypted
            past_check_ins.append(CheckIn(id=c["id"], user_id=c["user_id"], create_time=c["create_time"], messages=c["messages"]))
        
        return past_check_ins
    
    def get_messages(self, id, last_k=10):
        client = FirestoreClient(collection_name=self.collection_name)
        return messages_from_dict(client.get_document(id)["messages"])[-last_k:]


generative_check_in = GenrativeCheckIn()