from dotenv import load_dotenv
from gtts import gTTS
from io import BytesIO

import streamlit as st
from streamlit_option_menu import option_menu
#from streamlit_extras.let_it_rain import rain #For animation

import google.generativeai as genai 
from pathlib import Path
from PIL import Image
import pathlib
from bs4 import BeautifulSoup
import logging
import shutil

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
foot_css_file = current_dir / "static" / "footer_style.css"

pg_icon_png = current_dir / "assets" / "icon.png"

logo_image = Image.open(company_logo)
icon_image = Image.open(web_icon)
pg_icon = Image.open(pg_icon_png)

PAGE_TITLE = "Interview Helper AI"
#PAGE_ICON = icon_image
PAGE_ICON = pg_icon
#":large_green_circle:"    # :wave:"    #:technologist"

st.set_page_config(page_title = PAGE_TITLE, 
                   page_icon =  icon_image, 
                   layout= "wide",
                   menu_items=None)

def inject_ga():
    GA_ID = "google_analytics"
    GA_JS = """
    <!-- Global site tag (gtag.js) - Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-L7CQSR3TWT"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());

        gtag('config', 'G-L7CQSR3TWT');
    </script>
    """

    # Insert the script in the head tag of the static template inside your virtual
    index_path = pathlib.Path(st.__file__).parent / "static" / "index.html"
    logging.info(f'editing {index_path}')
    soup = BeautifulSoup(index_path.read_text(), features="html.parser")
    if not soup.find(id=GA_ID): 
        bck_index = index_path.with_suffix('.bck')
        if bck_index.exists():
            shutil.copy(bck_index, index_path)  
        else:
            shutil.copy(index_path, bck_index)  
        html = str(soup)
        new_html = html.replace('<head>', '<head>\n' + GA_JS)
        index_path.write_text(new_html)

inject_ga()

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

with open(foot_css_file) as ft_css:
    st.markdown("<style>{}</style>".format(ft_css.read()), unsafe_allow_html=True)

# --- profile SECTION ---
with st.container():
    col1, col2, col3 = st.columns(3, gap="small")
    with col1:
        st.image(logo_image, width=125)
    with col2:
        st.header("Interview Helper AI (Beta)")

with st.container():
    selected = option_menu(
        menu_title = None,
        options = ['Skills & JD review', 'Interview Q & A' , 'Chat Coversation', 'Audio Conversation', 'Cover Letter'],
        #add these names from https://icons.getbootstrap.com    
        icons = ['journal-check','list-columns-reverse', 'chat-left-text-fill', 'mic', 'envelope-paper'], 
        orientation = 'horizontal',
        #"container": {"padding": "0px", "margin":"0px", "width":"0px"}
        #"container": {"padding": "0px", "overflow": "auto",    "width":"100%", "border": "3px solid green;"}
        styles={
            "container": { "max-width":"100%"},
        }
    )

    if "skillJDReview_value" not in st.session_state:
        st.session_state.skillJDReview_value = ""
    if "questionAnswer_value" not in st.session_state:
        st.session_state.questionAnswer_value = ""
    if "coverLetter_value" not in st.session_state:
        st.session_state.coverLetter_value = ""

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
            #print("Drawing expander")
            resume_col, jd_col =  st.columns([1, 1])
            with resume_col:
                st.write("")
                resume_main_file = st.file_uploader("Upload resume (.pdf or .docx) :red[*] ", type=['pdf','doc','docx'], key="resume_file_key")
            with jd_col:
                jd_main_content = st.text_area(
                    label = "Job Description :red[*] ",
                    height = 75,
                    max_chars = 7000 ,
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
            #print("Submitted... ")
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
    
    #if st.session_state.skillJDReview_loaded == False:
    if len(st.session_state.resume_text) > 0 and len(st.session_state.job_description_text) > 0:
        resume_review_container = st.container(border=True)
        with resume_review_container:
            st.markdown(f" <small>Match your skills to the job: Analyze your resume and the job description for skill alignment. Skill gap analysis: Identify how your skills stack up against the job requirements.</small>"
                        , unsafe_allow_html=True)  

            st.markdown( """ <style>
                        #rcorners2 {
            border-radius: 25px;
            border: 2px solid #73AD21;
            padding: 20px; 
            }
            </style>
                        """,  unsafe_allow_html=True)

            resume_review_info_col1, resume_review_info_col2, resume_review_info_col3 = st.columns([1,1,1])
            with resume_review_info_col1:
                st.markdown(f"<p id='rcorners2'>🦾 Analyze your resume and the job description for skill alignment. </p>", unsafe_allow_html=True)
            with resume_review_info_col2:
                st.markdown(f"<p id='rcorners2'>🦾 Identify how your skills stack up against the job requirements. </p>", unsafe_allow_html=True)
            with resume_review_info_col3:
                st.markdown(f"<p id='rcorners2'>🦾 Use the insights from skill alignment and gap analysis to customize your resume </p>", unsafe_allow_html=True)

            resume_review_col1, resume_review_col2, resume_review_col3 = st.columns([1,1,1])
            with resume_review_col2:
                m = st.markdown("""
                <style>
                div.stButton > button:first-child {background-color: #0099ff;color:#ffffff;}
                </style>""", unsafe_allow_html=True)
                review_resume_button = st.button(label="Review skill alignments for Job Description.")
            #st.button(label="My button", style="background-color: #DD3300; color:#eeffee; border-radius: 0.75rem;")
            rjr_message_container = st.container()
            with rjr_message_container:
                rjr_loading_indicator_container = st.container()
                #rjr_error_message = st.success("")
                #rjr_message_response = st.success()
                rjr_message_response = st.container()
                if len(st.session_state.skillJDReview_value) > 0:
                    rjr_message_response.success(st.session_state.skillJDReview_value)

            if review_resume_button:
                with rjr_loading_indicator_container:
                    rjr_loading_indicator = st.spinner("Reviewing skills alignment for the Job Description, please wait...")
                    #rjr_error_message = st.spinner("Reviewing Job Description and Resume, please wait...")
                    with rjr_loading_indicator:
                        rjr_response = getSkillAndRequirementReview(st.session_state.resume_text, st.session_state.job_description_text)
                    #print(cover_letter_text)
                    st.session_state.skillJDReview_loaded = True
                    st.session_state.skillJDReview_value = rjr_response
                    rjr_message_response.success(rjr_response)
    else:
        st.toast("Upload Resume and provide Job Description")
    #st.write(st.session_state)

## ----  Interview Questions and sample answers implementation start -----------------------------------------------------------
if selected == 'Interview Q & A':
    if len(st.session_state.resume_text) > 0 and len(st.session_state.job_description_text) > 0:
        interview_que_ans_container = st.container(border=True)
        with interview_que_ans_container:
            #print(f"len(st.session_state.resume_text) {len(st.session_state.resume_text)} len(st.session_state.job_description_text)= {len(st.session_state.job_description_text)} ")
            st.markdown(f" <small>Unlock your interview superpowers! This tool analyzes your resume and the job description to predict the questions you'll likely be asked and suggest winning answers that showcase your skills and experience.</small>"
                        , unsafe_allow_html=True)  

            st.markdown( """ <style>
                        #rcorners2 {
            border-radius: 25px;
            border: 2px solid #73AD21;
            padding: 20px; 
            }
            </style>
                        """,  unsafe_allow_html=True)

            qanda_info_col1, qanda_info_info_col2, qanda_info_info_col3 = st.columns([1,1,1])
            with qanda_info_col1:
                st.markdown(f"<p id='rcorners2'>🦾 Analyze your resume and job description to predict interview questions. </p>", unsafe_allow_html=True)
            with qanda_info_info_col2:
                st.markdown(f"<p id='rcorners2'>🦾 Tailored Answer Suggestions, Receive personalized recommendations for crafting winning answers. </p>", unsafe_allow_html=True)
            with qanda_info_info_col3:
                st.markdown(f"<p id='rcorners2'>🦾 Showcase Your Strengths, skills confidently to impress interviewers. </p>", unsafe_allow_html=True)

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
                qa_message_response = st.container()
                if len(st.session_state.questionAnswer_value) > 0:
                    qa_message_response.success(st.session_state.questionAnswer_value)

            if interview_que_ans_button:
                with qa_loading_indicator_container:
                    interview_que_ans_loading = st.spinner("Generating interview questions and ideal asnswers, please wait...")
                    with interview_que_ans_loading:
                        qa_response = generateQuestionAnswers(st.session_state.resume_text, st.session_state.job_description_text)
                    #st.session_state.skill = True
                    st.session_state.questionAnswer_value = qa_response                    
                    
                    qa_message_response.success(qa_response)

## ----  Cover letter implementation start -----------------------------------------------------------
if selected == 'Cover Letter' :
    if len(st.session_state.resume_text) > 0 and len(st.session_state.job_description_text) > 0:
        cover_letter_container = st.container(border=True)
        with cover_letter_container:
            cover_letter_col1, cover_letter_col2, cover_letter_col3 = st.columns([1,1,1])
            with cover_letter_col1:
                st.markdown("""
                            <small>This tool utilizes both the job description and resume to generate a tailored cover letter for your job application. To ensure greater precision, kindly include the job title and company name. Incorporating these details enhances the effectiveness of the generated letter. </small>
                               """, unsafe_allow_html=True)  
            with cover_letter_col2:
                job_title = st.text_input(" Job Title :red[*] ", max_chars =50, placeholder="Technical Project Manager")
            with cover_letter_col3:
                company = st.text_input(" Applying for (Company) :red[*]", max_chars=70, placeholder="Google")

            st.markdown( """ <style>
                        #rcorners2 {
            border-radius: 25px;
            border: 2px solid #73AD21;
            padding: 20px; 
            }
            </style>
                        """,  unsafe_allow_html=True)

            cover_letter_info_col1, cover_letter_info_col2, cover_letter_info_col3 = st.columns([1,1,1])
            with cover_letter_info_col1:
                st.markdown(f"<p id='rcorners2'>🦾 Utilize both the job description and resume to create a custom cover letter for job applications. </p>", unsafe_allow_html=True)
            with cover_letter_info_col2:
                st.markdown(f"<p id='rcorners2'>🦾  Improve the accuracy of the cover letter by providing the job title and company name for better alignment with the position. </p>", unsafe_allow_html=True)
            with cover_letter_info_col3:
                st.markdown(f"<p id='rcorners2'>🦾 Ensure the generated cover letter effectively reflects your qualifications and suitability for the specific role and company. </p>", unsafe_allow_html=True)

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
                cover_letter_message_response = st.container()
                if len(st.session_state.coverLetter_value) > 0:
                    cover_letter_message_response.success(st.session_state.coverLetter_value)

            if cover_letter_button:
                print(f"job_title: {job_title is None}  len(job_title)= {len(job_title)} company: {company is not None}  len(company) {len(company)}")
                try:
                    if len(job_title) >1 and len(company) >1:
                        #print("Condition satisfied")
                        with cover_letter_loading_indicator_container:
                            cover_letter_loading_indicator = st.spinner("Generating cover letter, please wait...")
                            with cover_letter_loading_indicator:
                                cover_letter_text = generateCoverLetter(st.session_state.resume_text, job_title, st.session_state.job_description_text, company)
                            st.session_state.coverLetter_value = cover_letter_text
                            cover_letter_message_response.empty()
                            #cover_letter_message_response.sucess("")
                            cover_letter_message_response.success(cover_letter_text)                
                    elif len(job_title) >1 and len(company) <=0:
                        cover_letter_message_response.error("Company name is missing.")
                    elif len(job_title) <=0 and len(company) >1:
                        cover_letter_message_response.error("Please provide Job Title.")
                    elif len(job_title) <=0 and len(company) <=0:
                        cover_letter_message_response.error("Please provide Job Title and Company name.")
                    else:
                        cover_letter_message_response.error("Unknown error.")
                except Exception as e:
                    print("An error occurred:", e)

## ----  Chat coversation start-------------------------------------------------------------------------
if selected == 'Chat Coversation':
    #TODO: introduce get started button
    if "skill_review_button_clicked" not in st.session_state:
        st.session_state.skill_review_button_clicked = False
            
    # Initialize session state for chat history if it doesn't exist 
    chat_conversation_container = st.container(border=True)
    with chat_conversation_container:
        if len(st.session_state.resume_text) > 0 and len(st.session_state.job_description_text) > 0:
            st.markdown(f" <small>This Interview like conversation offers a realistic simulation of the interview process, helping users build confidence and refine their responses in a supportive environment. This is is an immersive experience where users engage in simulated interviews facilitated by artificial intelligence.</small>"
                        , unsafe_allow_html=True)  
            st.markdown( """ <style>
                        #rcorners2 {
            border-radius: 25px;
            border: 2px solid #73AD21;
            padding: 20px; 
            }
            </style>
                        """,  unsafe_allow_html=True)

            resume_review_info_col1, resume_review_info_col2, resume_review_info_col3 = st.columns([1,1,1])
            with resume_review_info_col1:
                st.markdown(f"<p id='rcorners2'>🦾 Engage in lifelike interview scenarios to practice and refine responses.. </p>", unsafe_allow_html=True)
            with resume_review_info_col2:
                st.markdown(f"<p id='rcorners2'>🦾 Gain confidence by participating in simulated interviews tailored to your needs. </p>", unsafe_allow_html=True)
            with resume_review_info_col3:
                st.markdown(f"<p id='rcorners2'>🦾 Experience immersive interviews guided by artificial intelligence for personalized support and feedback. </p>", unsafe_allow_html=True)


        chat_conversation_button_container = st.empty()
        if st.session_state.skill_review_button_clicked == False and len(st.session_state.resume_text) > 0 and len(st.session_state.job_description_text) > 0:
            with chat_conversation_button_container.container():
                #print(f"Debug 1 {st.session_state.skill_review_button_clicked}")
                chat_btn_col1, chat_btn_btn_col2, chat_btn_btn_col3 = st.columns([1,1,1])
                with chat_btn_btn_col2:                
                    m = st.markdown("""
                        <style>
                        div.stButton > button:first-child {background-color: #0099ff;color:#ffffff;}
                        </style>""", unsafe_allow_html=True)
                    chat_conversation_button = st.button(label="Let's get conversation started.")
                if chat_conversation_button:
                    st.session_state.skill_review_button_clicked = True
                    chat_conversation_button_container.empty()
        else:
            chat_conversation_button_container.empty()

        if(st.session_state.skill_review_button_clicked ) and len(st.session_state.resume_text) > 0 and len(st.session_state.job_description_text) > 0:
            st.session_state.skill_review_button_clicked = True
            #print("Let's get conversation started, Button action.")
            model = getGeminProModel()
            # Add a Gemini Chat history object to Streamlit session state
            if "chat" not in st.session_state:
                st.session_state.chat = model.start_chat(history = [])

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
                    with st.spinner('💡 Generating question, please wait'):
                        chat_response = st.session_state.chat.send_message(ut.getChat_first_prompt(st.session_state.resume_text, st.session_state.job_description_text)) 
                    #print(f"Sending first request: {first_prompt_template}")
                    if chat_response and len(chat_response.text) >=0:
                        st.session_state.very_first_request = False
                        #print(f"Debug 4 {st.session_state.skill_review_button_clicked}")
                        chat_conversation_button_container.empty()

                        # Display last 
                    with st.chat_message("assistant"):
                            st.markdown(chat_response.text)
                    #print(f"Debug 5 {st.session_state.skill_review_button_clicked}")
                    chat_conversation_button_container.empty()

                # Accept user's next message, add to context, resubmit context to Gemini
                with second_container:
                    second_prompt = st.chat_input("Answer")
                
                if second_prompt: 
                    # Display user's last message
                    st.chat_message("user").markdown(second_prompt)
                    
                    # Send user entry to Gemini and read the response
                    #print(st.session_state.very_first_request)
                    second_prompt_with_ans = "Answer:" + second_prompt
                    with st.spinner('💡 Processing'):
                        second_response = st.session_state.chat.send_message(second_prompt_with_ans)
                    #print(f"Sending second request: {prompt} ")
                    
                    if second_response and len(second_response.text) >=0:
                        st.session_state.very_first_request = False
                    # Display last 
                    with st.chat_message("assistant"):
                        st.markdown(second_response.text)

## ----  Chat coversation end----------------------------


## ----  Audio coversation implementation starts----------------------------
if selected == 'Audio Conversation':
    aundio_conversation_container = st.container()
    with aundio_conversation_container:
        multi = ''' 
         <small>Interview like audio conversation with AI, opportunity to practice responding to these questions in a simulated environment. Through continuous repetition and practice, you can refine your answers and improve  overall interview performance, aided by the AI's feedback and guidance throughout the process. </small>
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

        first_container = st.container(height=200)
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
            
            lets_get_started_cotainer = st.empty()
            lets_get_started = None
            if st.session_state.very_first_request == True and len(st.session_state.resume_text) > 0 and len(st.session_state.job_description_text) > 0:
                with lets_get_started_cotainer:
                    lets_get_started = st.button("Let's get started")

            # if lets_get_started:
            #     st.session_state.very_first_request = True
            #     lets_get_started_cotainer.empty()
        
            if lets_get_started and st.session_state.very_first_request == True:
                #print(f"Sending first request: {audio_first_prompt_template}")
                with st.spinner('💡Thinking'):
                    lets_get_started_cotainer.empty()
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
                            sound_file = BytesIO()
                            tts = gTTS(response_for_audio1.text, lang='en')
                            tts.write_to_fp(sound_file)
                            #print("Showing Audio control")
                            st.markdown(text, unsafe_allow_html=True)
                            st.audio(sound_file)
                            #st.markdown(response.text)
                            lets_get_started_cotainer.empty()                            
            
            if st.session_state.very_first_request == False:
                # Accept user's next message, add to context, resubmit context to Gemini
                with second_container:
                    # Add button instead of the chat input
                    #prompt = st.chat_input("Answer")
                    next_question = st.button("Next question")
                
                if next_question: 
                    # Send user entry to Gemini and read the response
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
st.write("#")
st.write("#")
st.write("#")
footer_container = st.container(border=True)
EMAIL = "bibhishan_k@yahoo.com"
MOBILE = "+1 (408)931-0588"
LOCATION = "Newark CA, USA"
with footer_container:
    coll, col2, col3 = st.columns((2,1,1))
    with coll:
        st.subheader("Mission")
        st.markdown(f"""<small> The mission of our website is to empower users worldwide with personalized and effective interview preparation assistance leveraging cutting-edge AI technology. 
                    We aim to provide a comprehensive platform where users can access tailored resources, including mock interviews, expert feedback, and personalized coaching, to enhance their interview skills and confidence. 
                    Our goal is to democratize access to high-quality interview preparation support, 
                    regardless of background or experience, ultimately helping users secure their dream jobs and advance their careers.</small>""" ,unsafe_allow_html = True)
    
    #Got these icons and classes from https://fontawesome.com/search?q=tw&o=r&m=free
    with col2:
        st.subheader ("Policies")
        st.markdown("<a style='text-align: left; color: #5C6BC0 ; text-decoration: none;' href='https://ww.google.com' target='_blank'> Privacy Policy </a>" , unsafe_allow_html=True)
        st.markdown("<a style='text-align: left; color: #5C6BC0 ; text-decoration: none;' href='https://ww.google.com' target='_blank'> Terms and Conditions </a>" , unsafe_allow_html=True)
        st.subheader ("Support")
        st.markdown("<a style='text-align: left; color: #5C6BC0 ; text-decoration: none;' href='https://ww.google.com' target='_blank'> Disclaimer </a>" , unsafe_allow_html=True)
        st.markdown("<a style='text-align: left; color: #5C6BC0 ; text-decoration: none;' href='https://ww.google.com' target='_blank'> Helps and FAQs </a>" , unsafe_allow_html=True)
    
    with col3:
        st.subheader ("Contact Info")        
        css_example = f'''
        <i class="fa-solid fa-envelope"></i> {EMAIL}
        
        <i class="fa-solid fa-mobile"></i> {MOBILE}
        
        <i class="fa-solid fa-location-dot"></i> {LOCATION}
        '''
        st.write(css_example,unsafe_allow_html=True)

        st.subheader("Social Media")
        #st.markdown(""" ‹a style="color: #SC6BC0; text-decoration: none;" href="https://twitter.com"> <i class-"fa-brands fa-instagram"></i> </a›""", unsafe_allow_html = True)
        social_media = f""" <a style="color: #sc6bc0; text-decoration: none;" href="https://bkaradkar.net"> <i class="fa-brands fa-instagram"></i> </a>
        <a style="color: #sc6bc0; text-decoration: none;" href="https://bkaradkar.net"> <i class="fa-brands fa-linkedin"></i> </a>
        <a style="color: #sc6bc0; text-decoration: none;" href="https://bkaradkar.net"> <i class="fa-brands fa-youtube"></i> </a>
        <a style="color: #sc6bc0; text-decoration: none;" href="https://bkaradkar.net"> <i class="fa-brands fa-twitter"></i> </a>
        """
        st.write(social_media, unsafe_allow_html=True)
