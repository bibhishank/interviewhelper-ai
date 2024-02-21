from Utils import getGeminProModel


#response = ""
#---------------------------------------------------------------------------------------------
#Chat conversation with Gemini Pro  

def getChatResponde(chat_resume_text, chat_jd, chat_input):
    
    
    prompt_parts = [
    f""" Role: Chat Practice Partner for interviewee
        Topic: Job interview
        Style: Casual, respectful, not too enthusiastic or flowery.

        Steps:
        Initiate with a topic-specific question.

        Wait for interviewee answer. One question at a time.
        Reply genuinely, with brief follow-ups.
        Encourage interviewee to share thoughts and opinions supportively.
        Maintain a balanced conversation.

        Example:
        Question: "Can you share details on your last project ?”
        Response: “Yes, Sure. My last project I worked on was implementing forced breaks of 10 minute on back to back meetings. I worked with multiple cross-functional teams including Engineering, Marketing, Legal, Product owners. My responsibility was from getting approval for this project from leadership and teams like Legal and finance till executing this program for few countries to the AB test and then launch it globally.”

        Respond with "OK" and wait for me to say "Let's get started" before asking the first question.

        Here is interviewee's resume: \"{chat_resume_text}\"
        Here is Job Description: \"{chat_jd}\"
    """
    ]
    
    if model is None:
        model = getGeminProModel()

    if chat is None:
        chat = model.start_chat(history=[])
    else:
        chat_responses = chat.send_message(prompt_parts,stream=True)
        chat_response_stream = ""
        for chat_response in chat_responses:
            chat_response_stream += chat_response.text

    return chat_response_stream

#---------------------------------------------------------------------------------------------

def getSimpleChatResponde1(message):
    if model is None:
        model = getGeminProModel()

    #openai.ChatCompletion.create
    if chat is None:
        chat = model.start_chat(history=[])
    else:
        chat_responses = chat.send_message(message,stream=True)
        chat_response_stream = ""
        for chat_response in chat_responses:
            chat_response_stream += chat_response.text

    return chat_response_stream

#---------------------------------------------------------------------------------------------

def getSimpleChatResponde2(message):
    if model is None:
        model = getGeminProModel()

    #openai.ChatCompletion.create
    if chat is None:
        chat = model.start_chat(history=[])
    else:
        chat_responses = chat.send_message(message,stream=True)
        chat_response_stream = ""
        for chat_response in chat_responses:
            chat_response_stream += chat_response.text

    return chat_response_stream
