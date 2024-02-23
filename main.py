from dotenv import load_dotenv
from gtts import gTTS
from io import BytesIO

import streamlit as st
from streamlit_option_menu import option_menu
#from streamlit_extras.let_it_rain import rain #For animation

import google.generativeai as genai 
from pathlib import Path
from PIL import Image


from CoverLetterGenerator import generateCoverLetter
from ReviewJDandResume import getSkillAndRequirementReview
from GenerateQuestionAnswers import generateQuestionAnswers
from ChatConversation import getSimpleChatResponde1, getSimpleChatResponde2
import Utils
from Utils import readPdforDocFile, getGeminProModel
import Utils as ut 

#Not able to install streamlit_extras.let_it_rain
# def celebration_animate():
#     rain(
#         emoji="🎈",
#         font_size=54,
#         falling_speed=5,
#         animation_length= [4,5] ,
#         #animation_length= [] "infinite",
#     )

def load_css():
    with open("static/styles.css", "r") as f:
        css = f"<style>{f.read()}</style>"
        st.markdown(css, unsafe_allow_html=True)

number_of_pages = 0
text_length_char = 0
text_length_char_txt = 0
all_page_text = ""

# --- PATH SETTINGS ---
current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
company_logo = current_dir / "assets" / "company_logo.png"
web_icon =  current_dir / "assets" / "company_icon.ico"

logo_image = Image.open(company_logo)
icon_image = Image.open(web_icon)

PAGE_TITLE = "Interview Helper AI"
PAGE_ICON = icon_image
#":large_green_circle:"    # :wave:"    #:technologist"

st.set_page_config(page_title=PAGE_TITLE, 
                   page_icon=PAGE_ICON, 
                   layout= "wide",
                   menu_items=None)


# Remove whitespace from the top of the page and sidebar

#TODO: Move this Utils.py
st.markdown("""
<style>
    #MainMenu, header, footer {visibility: hidden;}
    /* This code gets the first element on the sidebar,
    and overrides its default styling */
    section[data-testid="stSidebar"] div:first-child {
        top: 0;
        height: 100vh;
    }
</style>
""",unsafe_allow_html=True)

#TODO: Move this Utils.py
st.markdown("""
    <style>
    
           /* Remove blank space at top and bottom */ 
           .block-container {
               padding-top: 0rem;
               padding-bottom: 0rem;
            }
           
           /* Remove blank space at the center canvas */ 
           .st-emotion-cache-z5fcl4 {
               position: relative;
               top: -20px;
               }
           
           /* Make the toolbar transparent and the content below it clickable */ 
           .st-emotion-cache-18ni7ap {
               pointer-events: none;
               background: rgb(255 255 255 / 0%)
               }
           .st-emotion-cache-zq5wmm {
               pointer-events: auto;
               background: rgb(255 255 255);
               border-radius: 5px;
               }
            
    </style>
    """, unsafe_allow_html=True)

# --- profile SECTION ---
with st.container():
    col1, col2 = st.columns(2, gap="small")
    with col1:
        st.image(logo_image, width=125)

with st.container():
    selected = option_menu(
        menu_title = None,
        options = ['Skills & JD review', 'Interview Questions & Ans' , 'Chat Coversation', 'Audio Conversation', 'Cover Letter'],
        #add these names from https://icons.getbootstrap.com    
        icons = ['journal-check','list-columns-reverse', 'chat-left-text-fill', 'mic', 'envelope-paper'], 
        orientation = 'horizontal',
        #"container": {"padding": "0px", "margin":"0px", "width":"0px"}
        #"container": {"padding": "0px", "overflow": "auto",    "width":"100%", "border": "3px solid green;"}
        styles={
            "container": { "max-width":"100%"},
        }
    )

    resume_and_jd_uploaded = False
    #st.write(f"In the beginning before uploading file: {st.session_state}")
    #expander_string = ":heavy_multiplication_x: **Upload Resume**   ---------   :heavy_multiplication_x: **Provide Job Desctiption** "
    expander_string = ":heavy_multiplication_x: **Upload Resume and Provide Job Desctiption** :small_red_triangle_down: "
    is_expanded = True
    if "resume_text" not in st.session_state:
        st.session_state.resume_text = ""
    if "job_description_text" not in st.session_state:
        st.session_state.job_description_text = ""

    if len(st.session_state.resume_text) >0 and len(st.session_state.job_description_text) > 0:
        resume_and_jd_uploaded = True
        expander_string = " :white_check_mark: Reusme    :white_check_mark: Job Desctiption  "
        is_expanded = False
    elif len(st.session_state.resume_text) <=0 and len(st.session_state.job_description_text) > 0:
        resume_and_jd_uploaded = False
        expander_string = " :white_check_mark: Reusme    :heavy_multiplication_x: **Provide Job Desctiption** :small_red_triangle_down:  "
        is_expanded = True

    elif len(st.session_state.resume_text) >0 and len(st.session_state.job_description_text) <=0:    
        resume_and_jd_uploaded = False
        expander_string = " :heavy_multiplication_x: **Upload Reusme** :small_red_triangle_down:    :white_check_mark:Job Desctiption  "
        is_expanded = True
    elif len(st.session_state.resume_text) <=0 and len(st.session_state.job_description_text) <=0:
        resume_and_jd_uploaded = False
        expander_string = " :heavy_multiplication_x: **Upload Resume and Provide Job Desctiption** :small_red_triangle_down: "
        is_expanded = True

    #resume_jd_message_container = st.container(border=True)

    resume_job_expander_container = st.container()
    with resume_job_expander_container:
        resume_job_expander = st.expander( expander_string, expanded=is_expanded)    
        with resume_job_expander:
            print("Drawing expander")
            resume_col, jd_col =  st.columns([1, 1])
            with resume_col:
                st.write("")
                resume_main_file = st.file_uploader("Upload resume (.pdf or .docx) :red[*] ", type=['pdf','doc','docx'],key="resume_file_key")
            with jd_col:
                jd_main_content = st.text_area(
                    label = "Job Description :red[*] ",
                    height = 75,
                    max_chars = 6000 ,
                    placeholder = "Job Description", key="job_desc_key"
                    )
            resume_jd_upload_button_col, resume_jd_upload_message_col  =  st.columns([1, 9])
            with resume_jd_upload_button_col:
                resume_jd_submit_button = st.button(label="Upload")
            with resume_jd_upload_message_col:    
                resume_jd_message_container = st.container(border=False)
                with resume_jd_message_container:
                    resume_jd_message_container = st.text("")
        
        if resume_jd_submit_button:
            print("Submitted... ")
            if(resume_main_file is not None and jd_main_content and len(jd_main_content)> 50):
                resume_jd_message_container.success("Process started")
                resume_text = ut.readPdforDocFile(resume_main_file)
                if resume_text == "MORE_THAN_FIVE_PAGES":
                    resume_jd_message_container.error("PDF file contains more than 5 pages, please upload file with 5 or less pages.")
                elif resume_text == "LESS_TEXT_IN_PDF":
                    resume_jd_message_container.error("File has not enough content(less than 200 charater) readable content, please reupload file with enough content.")
                elif resume_text == "MORE_TEXT_IN_PDF":
                    resume_jd_message_container.error("File is too large, please reduce text size and re-upload file.")
                elif resume_text == "ERROR_READING_FILE":
                    resume_jd_message_container.error("System is not able to read provided file, please provided valid .pdf file .")
                elif resume_text == "UNSUPPORTED_FILE_TYPE":
                    resume_jd_message_container.error("Unsupported file type, accepted file types are .pdf, .doc or .docx ")    
                elif resume_text == "SUCCESS":
                    ut.setJobDescriptionText(jd_main_content)
                    ut.verifyResumeandJDSize()
                    #resume_job_expander #check if expander lable can be changed
                    st.session_state.resume_text = resume_text
                    st.session_state.job_description_text = jd_main_content
                    #st.write(f"After uploading file: {st.session_state}")
                    expander_string = " :white_check_mark: Reusme    :white_check_mark: Job Desctiption  "
                    is_expanded = False
                    resume_jd_message_container.success("File uploaded sucessfully")

            elif resume_main_file is None and (jd_main_content is None or len(jd_main_content) <= 0):
                resume_jd_message_container.error(" :red[Please upload your resume and include job descriptions.]")
            elif resume_main_file is not None and (jd_main_content is None or len(jd_main_content) <= 0):
                resume_jd_message_container.error(" :red[The job description is required include the job descriptions.]")
            elif resume_main_file is  None and jd_main_content is not None and len(jd_main_content) > 0 and len(jd_main_content) < 50:
                resume_jd_message_container.error(" :red[Both the resume and job description are mandatory, with the job description needing to be a min of 50 char long.] ")            
            elif resume_main_file is not None and jd_main_content is not None and len(jd_main_content) > 0 and len(jd_main_content) < 50:
                resume_jd_message_container.error(" :red[The job description is required and must be at least 50 characters in length.] ")            
            elif resume_main_file is None and (jd_main_content is not None and len(jd_main_content) > 50):
                resume_jd_message_container.error(" :red[ The resume is not provided, please select the file to upload.] ")


## ----  Review and Compare skill implementation start -----------------------------------------------------------
if selected == 'Skills & JD review':
    resume_review_container = st.container()
    with resume_review_container:
        if len(st.session_state.resume_text) > 0 and len(st.session_state.job_description_text) > 0:
            st.markdown(f" <small>Match your skills to the job: Analyze your resume and the job description for skill alignment. Skill gap analysis: Identify how your skills stack up against the job requirements.</small>"
                        , unsafe_allow_html=True)  

            resume_review_col1, resume_review_col2, resume_review_col3 = st.columns([1,1,1])
            with resume_review_col2:
                m = st.markdown("""
                <style>
                div.stButton > button:first-child {background-color: #0099ff;color:#ffffff;}
                </style>""", unsafe_allow_html=True)
                review_resume_button = st.button(label="Review resume for Job Description.")
            
            #st.button(label="My button", style="background-color: #DD3300; color:#eeffee; border-radius: 0.75rem;")
            rjr_message_container = st.container()
            with rjr_message_container:
                rjr_loading_indicator_container = st.container()
                #rjr_error_message = st.success("")
                rjr_message_response = st.success("")

            if review_resume_button:
                with rjr_loading_indicator_container:
                    rjr_loading_indicator = st.spinner("Processing...")
                    #rjr_error_message = st.spinner("Reviewing Job Description and Resume, please wait...")
                    with rjr_loading_indicator:
                        rjr_response = getSkillAndRequirementReview(st.session_state.resume_text, st.session_state.job_description_text)
                    #print(cover_letter_text)
                    #rjr_error_message.success("Here are insights of Resume against Job Description :point_down: ")
                    rjr_message_response.success(rjr_response)
        else:
            st.toast("Upload Resume and provide Job Description")
        #st.write(st.session_state)

## ----  Interview Questions and sample answers implementation start -----------------------------------------------------------
if selected == 'Interview Questions & Ans':
    interview_que_ans_container = st.container()
    with interview_que_ans_container:
        if len(st.session_state.resume_text) > 0 and len(st.session_state.job_description_text) > 0:
            #print(f"len(st.session_state.resume_text) {len(st.session_state.resume_text)} len(st.session_state.job_description_text)= {len(st.session_state.job_description_text)} ")
            st.markdown(f" <small>Unlock your interview superpowers! This tool analyzes your resume and the job description to predict the questions you'll likely be asked and suggest winning answers that showcase your skills and experience.</small>"
                        , unsafe_allow_html=True)  

            interview_que_ans_col1, interview_que_ans_col2, interview_que_ans_col3 = st.columns([1,1,1])
            with interview_que_ans_col2:
                m = st.markdown("""
                <style>
                div.stButton > button:first-child {background-color: #0099ff;color:#ffffff;}
                </style>""", unsafe_allow_html=True)
                interview_que_ans_button = st.button(label="Generate interview questions and ideal asnswers.")
        
            qa_message_container = st.container()
            with qa_message_container:
                qa_loading_indicator_container = st.container()
                qa_message_response = st.success("")

            if interview_que_ans_button:
                with qa_loading_indicator_container:
                    interview_que_ans_loading = st.spinner("Processing...")
                    with interview_que_ans_loading:
                        qa_response = generateQuestionAnswers(st.session_state.resume_text, st.session_state.job_description_text)
                    qa_message_response.success(qa_response)

## ----  Cover letter implementation start -----------------------------------------------------------
if selected == 'Cover Letter' :
    cover_letter_container = st.container()
    with cover_letter_container:
        if len(st.session_state.resume_text) > 0 and len(st.session_state.job_description_text) > 0:
            
            cover_letter_col1, cover_letter_col2, cover_letter_col3 = st.columns([1,1,1])
            with cover_letter_col1:
                st.markdown("""
                            <small>This tool utilizes both the job description and resume to generate a tailored cover letter for your job application. To ensure greater precision, kindly include the job title and company name. Incorporating these details enhances the effectiveness of the generated letter. </small>
                               """, unsafe_allow_html=True)  
            with cover_letter_col2:
                job_title = st.text_input(" Job Title :red[*] ", max_chars =50, placeholder="Technical Project Manager")
            with cover_letter_col3:
                company = st.text_input(" Applying for (Company) :red[*]", max_chars=70, placeholder="Google")

            cover_letter_btn_col1, cover_letter_btn_col2, cover_letter_btn_col3 = st.columns([1,1,1])
            with cover_letter_btn_col2:
                m = st.markdown("""
                    <style>
                    div.stButton > button:first-child {background-color: #0099ff;color:#ffffff;}
                    </style>""", unsafe_allow_html=True)
                cover_letter_button = st.button(label="Generate Cover Letter")
            
            cover_letter_message_container = st.container()
            with cover_letter_message_container:
                cover_letter_loading_indicator_container = st.container()
                cover_letter_message_response = st.success("")

            if cover_letter_button:
                print(f"job_title: {job_title is None}  len(job_title)= {len(job_title)} company: {company is not None}  len(company) {len(company)}")
                if len(job_title) >1 and len(company) >1:
                    print("Condition satisfied")
                    with cover_letter_loading_indicator_container:
                        cover_letter_loading_indicator = st.spinner("Generating cover letter, please wait...")
                        with cover_letter_loading_indicator:
                            cover_letter_text = generateCoverLetter(st.session_state.resume_text, job_title, st.session_state.job_description_text, company)
                        cover_letter_message_response.success(cover_letter_text)                
                elif len(job_title) >1 and len(company) <=0:
                    cover_letter_message_response.error("Company name is missing.")
                elif len(job_title) <=0 and len(company) >1:
                    cover_letter_message_response.error("Please provide Job description.")
                elif len(job_title) <=0 and len(company) <=0:
                    cover_letter_message_response.error("Please provide Job description.")
                else:
                    cover_letter_message_response.error("Unknown error.")

## ----  Chat coversation start-------------------------------------------------------------------------
if selected == 'Chat Coversation':
    #TODO: introduce get started button
    if "skill_review_button_clicked" not in st.session_state:
        st.session_state.skill_review_button_clicked = False
            
    # Initialize session state for chat history if it doesn't exist 
    with st.container():

        st.write("   :blue[ **Interview like Conversation with AI** ]  ")  

        chat_conversation_button_container = st.container()
        if st.session_state.skill_review_button_clicked == False:
            with chat_conversation_button_container:
                chat_conversation_button = st.button(label="Let's get conversation started.")
        else:
            chat_conversation_button_container = st.empty()
            chat_conversation_button_container.empty()

        if(st.session_state.skill_review_button_clicked or chat_conversation_button) and len(st.session_state.resume_text) > 0 and len(st.session_state.job_description_text) > 0:

            st.session_state.skill_review_button_clicked = True

            model = getGeminProModel()

            first_prompt_template = f"""Role: Chat Practice Partner for interview
            Topic: Job interview
            Style: Casual, respectful, not too enthusiastic or flowery.

            Steps:
            From the provided Resume and Job Description, initiate with a topic-specific interview question. 
            Ask one question at a time.
            Analyze job description and gather company information and influence questions with that information.
            Very first time user will just say "Lets get started" then provide a first questions. There will not be answer provided.
            If there is "Answer" available in users response, review the answer, and provide next one question.
                
            Example:
            Question: "Can you share details on your last project ?”

            Here is Resume: \" {st.session_state.resume_text}. \" 

            Here is Job Description \"{st.session_state.job_description_text}. \" 
            """

            # Add a Gemini Chat history object to Streamlit session state
            if "chat" not in st.session_state:
                st.session_state.chat = model.start_chat(history = [])
                #st.session_state.chat = model.start_chat(prompt_template)

            if "very_first_request" not in st.session_state:
                st.session_state.very_first_request = True

            first_container = st.container(height=380, border=False)
            second_container = st.container()
            with first_container:
                for message in st.session_state.chat.history:
                    x = message.parts[0].text.find("Role: Chat Practice Partner for interview")
                    if x < 0:
                        with st.chat_message(ut.role_to_streamlit(message.role)):
                            st.markdown(message.parts[0].text)

                if st.session_state.very_first_request == True:
                    response = st.session_state.chat.send_message(first_prompt_template) 
                    #print(f"Sending first request: {first_prompt_template}")
                    if response and len(response.text) >=0:
                        st.session_state.very_first_request = False
                        # Display last 
                    with st.chat_message("assistant"):
                            st.markdown(response.text)

                # Accept user's next message, add to context, resubmit context to Gemini
                with second_container:
                    prompt = st.chat_input("Answer")
                
                if prompt: 
                    # Display user's last message
                    st.chat_message("user").markdown(prompt)
                    
                    # Send user entry to Gemini and read the response
                    #print(st.session_state.very_first_request)
                    prompt = "Answer:" + prompt
                    response = st.session_state.chat.send_message(prompt)
                    #print(f"Sending second request: {prompt} ")
                    
                    if response and len(response.text) >=0:
                        st.session_state.very_first_request = False
                    # Display last 
                    with st.chat_message("assistant"):
                        st.markdown(response.text)

## ----  Chat coversation end----------------------------
 
if selected == 'Audio Conversation':
    with st.container():
        multi = ''' 
        <b>Interview like audio conversation with AI </b> <small> AI will ask you questions, practice answering these questions, and keep practicing</small>
        '''
        st.markdown(multi, unsafe_allow_html=True)
        model = ut.getGeminProModel()
        
        audio_first_prompt_template = ut.getAudio_first_prompt(st.session_state.resume_text, st.session_state.job_description_text)

        # Add a previous bot question  to Streamlit session state
        if "previous_question" not in st.session_state:
            st.session_state.previous_question = ""

        # Add a current bot question  to Streamlit session state
        if "current_question" not in st.session_state:
            st.session_state.current_question = ""


        # Add a Gemini Chat history object to Streamlit session state
        if "chat" not in st.session_state:
            st.session_state.chat = model.start_chat(history = [])
            #st.session_state.chat = model.start_chat(prompt_template)

        if "very_first_request" not in st.session_state:
            st.session_state.very_first_request = True

        first_container = st.container(height=200, border=True)
        second_container = st.container()
        
        with first_container:
            message_request_counter = 0
            for message in st.session_state.chat.history:
                x = message.parts[0].text.find("Role: Chat Practice Partner for interview")
                if x < 0:
                    #with st.chat_message(ut.role_to_streamlit(message.role)):
                    message_request_counter += 1
                        #st.markdown(message.parts[0].text) - Not printing messages in history
            #print(f"Message counter: {message_request_counter} ")    
            
            lets_get_started_cotainer = st.container()
            lets_get_started = None
            if st.session_state.very_first_request == True:
                with lets_get_started_cotainer:
                    lets_get_started = st.button("Let's get started")

            # if lets_get_started:
            #     st.session_state.very_first_request = True
            #     lets_get_started_cotainer.empty()
        
            if lets_get_started and st.session_state.very_first_request == True:
                #print(f"Sending first request: {audio_first_prompt_template}")
                with st.spinner('💡Thinking'):
                    response_for_audio1 = st.session_state.chat.send_message(audio_first_prompt_template) 
                
                if response_for_audio1 and len(response_for_audio1.text) >=0:
                    #print(f"First request Response : {response_for_audio1}")
                    st.session_state.very_first_request = False
                    st.session_state.previous_question = response_for_audio1.text
                    # Display last
                    with st.chat_message("assistant"):
                        #Render first Audio response
                        question_audio_container =st.container()
                        with question_audio_container:
                            text = f"<h3 style='text-align: left; '> Liesten to the question</h3>"
                            #text = f"<h3 style='text-align: left; color: {ut.getRandomColor()}; '> Liesten to the question</h3>"
                            #print(text)
                            st.markdown(text, unsafe_allow_html=True)
                            sound_file = BytesIO()
                            tts = gTTS(response_for_audio1.text, lang='en')
                            tts.write_to_fp(sound_file)
                            #print("Showing Audio control")
                            st.audio(sound_file)
                            #st.markdown(response.text)
                            lets_get_started_cotainer.empty()                            
            
            if st.session_state.very_first_request == False:
                # Accept user's next message, add to context, resubmit context to Gemini
                with second_container:
                    # Add button instead of the shat input
                    #prompt = st.chat_input("Answer")
                    next_question = st.button("Next question")
                
                if next_question: 
                    # Display user's last message
                    #st.chat_message("user").markdown(prompt)
                    #print("next_question button pressed")
                    # Send user entry to Gemini and read the response
                    #print(st.session_state.very_first_request)

                    prompt = "NO Answer" 
                    
                    #print(f"Sending second request: {prompt} ")
                    with st.spinner('💡Thinking'):
                        response = st.session_state.chat.send_message(prompt)
                    
                    #print(f"Response of second request: {response} ")

                    if response and len(response.text) >=0:
                        st.session_state.very_first_request = False
                    # Display last 
                    first_container.empty()

                    #with first_container:
                    question_audio_container =st.container()
                    with question_audio_container:
                        with st.chat_message("assistant"):
                            #Store this response, as a current question in session, and move current question value to previous question
                            tmp_text = st.session_state.current_question
                            st.session_state.previous_question = tmp_text
                            st.session_state.current_question = response.text
                            
                            #question_audio_container.empty()

                            #with question_audio_container:
                            text = f"<h3 style='text-align: left; '> Liesten to the question</h3>"
                            #print(text)
                            st.markdown(text, unsafe_allow_html=True)
                            second_sound_file = BytesIO()
                            tts1 = gTTS(response.text, lang='en')
                            tts1.write_to_fp(second_sound_file)
                            st.audio(second_sound_file)

                            #Render Audio of last question
                            #st.markdown(response.text)                            

                    #else:
                    #    print("No response for the first request")     

    
##- Celebration with dropping ballon or any other emoji
#celebration_animate()
