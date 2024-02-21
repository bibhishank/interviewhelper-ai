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
                    st.session_state.resume_text = "SUCCESS"
                    st.session_state.job_description_text = "SUCCESS"
                    #st.write(f"After uploading file: {st.session_state}")
                    expander_string = " :white_check_mark: Reusme    :white_check_mark: Job Desctiption  "
                    is_expanded = False
                    #resume_job_expander.expanded = False
                    #resume_job_expander_container.empty()
                    #resume_job_expander_container = st.empty()
                    #with resume_job_expander_container:
                    #    resume_job_expander = st.expander( expander_string, expanded=is_expanded)    
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
    with st.container():
        st.write("   :blue[ **Review and Compare skill in Resume with Job Description** ]  ")  
        multi = ''' 
        :blue[ **To Review and Compare skill:** ] <small>Upload your resume in .pdf or .docx file format. Provide Job Description.</small>
        '''
        st.markdown(multi, unsafe_allow_html=True)
        
        review_resume_button = st.button(label="Review resume for Jpb Description.")

        #Create a form using st.form 
        resume_jd_review_form = st.form ("Resume JD review Form")
        with resume_jd_review_form:
            sjr_colbutton1, sjr_colbutton2 =  st.columns([1, 1])
            with sjr_colbutton1:
                rjr_resume = st.file_uploader("Upload resume (.pdf or .docx) :red[*] ", type=['pdf','doc','docx'])
                rjr_colbutton1, rjr_colbutton2 =  st.columns([8, 2])
                with rjr_colbutton1:
                    st.write("\n")
                    rjr_error_message = st.info("")
                with rjr_colbutton2:
                    st.write("")
                    rjr_submitted = st.form_submit_button(label="Review skills")
                    #st.button(label="My button", style="background-color: #DD3300; color:#eeffee; border-radius: 0.75rem;")

            with sjr_colbutton2:
                rjr_jd = st.text_area(
                    label = "Job Description :red[*] ",
                    height = 200,
                    max_chars = 6000 ,
                    placeholder = "Job Description"
                    )
        rjr_message_container = st.container(border=True)
        with rjr_message_container:
            rjr_loading_indicator_container = st.container()
            rjr_message_response = st.success("")
            
        

        if rjr_submitted:
            print(f"rjr_resume {rjr_resume} rjr_jd {rjr_jd} len(jr_jd) {len(rjr_jd)} ")
            if(rjr_resume is not None and rjr_jd and len(rjr_jd)> 50):
                #st.write("Valid input")
                #rjr_error_message.success("Review of skill aginst Job Role is in progress, please wait...")
                resume_text = readPdforDocFile(rjr_resume)
                if resume_text == "MORE_THAN_FIVE_PAGES":
                    rjr_error_message.error("PDF file contains more than 5 pages, please upload file with 5 or less pages.")
                elif resume_text == "LESS_TEXT_IN_PDF":
                    rjr_error_message.error("File has not enough content (less than 200 charater) to generate cover letter, please reupload file with enough content.")
                elif resume_text == "LESS_TEXT_IN_TXT":
                    rjr_error_message.error("File has not enough content to generate cover letter, please reupload file with enough content.")
                elif resume_text == "MORE_TEXT_IN_TXT":
                    rjr_error_message.error("File is too large, please reduce text size and re-upload file.")
                elif resume_text == "ERROR_READING_FILE":
                    rjr_error_message.error("System is not able to read provided file, please provided valid .pdf file .")
                elif resume_text == "UNSUPPORTED_FILE_TYPE":
                    rjr_error_message.error("Unsupported file type, accepted file types are .pdf, .text, .doc or .docx ")    
                else:
                    #print(f"resume_text {resume_text} \n  rjr_jd {rjr_jd}.")
                    #st.write("Conditions are satisfied, calling OpenAI")
                    rjr_response = ""
                    rjr_error_message.success("Reviewing Job Description and Resume, please wait...")
                    with rjr_loading_indicator_container:
                        rjr_loading_indicator = st.spinner("Processing...")
                        #rjr_error_message = st.spinner("Reviewing Job Description and Resume, please wait...")
                        with rjr_loading_indicator:
                            rjr_response = getSkillAndRequirementReview(resume_text, rjr_jd)
                    #print(cover_letter_text)
                    rjr_error_message.success("Here are insights of Resume against Job Description :point_down: ")
                    rjr_message_response.success(rjr_response)

            elif rjr_resume is None:
                rjr_error_message.error(" :red[ Please Upload Resume.] ")
            elif rjr_resume is not None and rjr_jd is not None and len(rjr_jd) < 50:
                rjr_error_message.error(" :red[Job Description is required more than 50 charaters long.] ")            
            elif rjr_resume is None and (rjr_jd is not None or len(rjr_jd) <= 0):
                rjr_error_message.error(" :red[Upload Resume and provide job descriptions to review.]")

## ----  Interview Questions and sample answers implementation start -----------------------------------------------------------
if selected == 'Interview Questions & Ans':
    with st.container():
        st.write("   :blue[ **AI predicted interview questions and asnswers with help of Resume with Job Description** ]  ")  
        multi = ''' 
        :blue[ **To interview questions and answers:** ] <small>Upload your resume in .pdf or .docx file format. Provide detailed Job Description.</small>
        '''
        st.markdown(multi, unsafe_allow_html=True)
        
        #Create a form using st.form 
        questions_answer_form = st.form ("Questions answer Form")
        with questions_answer_form:
            qa_col1, qa_col2 =  st.columns([1, 1])
            with qa_col1:
                qa_resume = st.file_uploader("Upload resume (.pdf or .docx) :red[*] ", type=['pdf','doc','docx'])
                qa_colbutton1, qa_colbutton2 =  st.columns([8, 2])
                with qa_colbutton1:
                    st.write("\n")
                    qa_error_message = st.info("")
                with qa_colbutton2:
                    st.write("")
                    qa_submitted = st.form_submit_button(label=" Generate Q&A")
            with qa_col2:
                qa_jd = st.text_area(
                    label = "Job Description :red[*] ",
                    height = 200,
                    max_chars = 6000 ,
                    placeholder = "Job Description"
                    )
        qa_message_container = st.container(border=True)
        with qa_message_container:
            qa_loading_indicator_container = st.container()
            qa_message_response = st.success("")

        if qa_submitted:
            print(f"rjr_resume {qa_resume} rjr_jd {qa_jd} len(jr_jd) {len(qa_jd)} ")
            if(qa_resume is not None and qa_jd and len(qa_jd)> 50):
                #st.write("Valid input")
                #rjr_error_message.success("Review of skill aginst Job Role is in progress, please wait...")
                resume_text = readPdforDocFile(qa_resume)
                if resume_text == "MORE_THAN_FIVE_PAGES":
                    qa_error_message.error("PDF file contains more than 5 pages, please upload file with 5 or less pages.")
                elif resume_text == "LESS_TEXT_IN_PDF":
                    qa_error_message.error("File has not enough content (less than 200 charater) to generate cover letter, please reupload file with enough content.")
                elif resume_text == "LESS_TEXT_IN_TXT":
                    qa_error_message.error("File has not enough content to generate cover letter, please reupload file with enough content.")
                elif resume_text == "MORE_TEXT_IN_TXT":
                    qa_error_message.error("File is too large, please reduce text size and re-upload file.")
                elif resume_text == "ERROR_READING_FILE":
                    qa_error_message.error("System is not able to read provided file, please provided valid .pdf file .")
                elif resume_text == "UNSUPPORTED_FILE_TYPE":
                    qa_error_message.error("Unsupported file type, accepted file types are .pdf, .text, .doc or .docx ")    
                else:
                    #print(f"resume_text {resume_text} \n  rjr_jd {rjr_jd}.")
                    #st.write("Conditions are satisfied, calling OpenAI")
                    qa_error_message.success("Generating Questions and Answers, please wait...")
                    with qa_loading_indicator_container:
                        qa_loading_indicator = st.spinner("Processing...")
                        #rjr_error_message = st.spinner("Reviewing Job Description and Resume, please wait...")
                        with qa_loading_indicator:
                            qa_response = generateQuestionAnswers(resume_text, qa_jd)
                    #print(cover_letter_text)
                    qa_error_message.success("Here are preicted Questions and Answers generated with help of Resume and Job Description :point_down: ")
                    qa_message_response.success(qa_response)

            elif qa_resume is None:
                qa_error_message.error(" :red[ Please Upload Resume.] ")
            elif qa_resume is not None and qa_jd is not None and len(qa_jd) < 50:
                qa_error_message.error(" :red[Job Description is required more than 50 charaters long.] ")            
            elif qa_resume is None and (qa_jd is not None or len(qa_jd) <= 0):
                qa_error_message.error(" :red[Upload Resume and provide job descriptions to review.]")



## ----  Cover letter implementation start -----------------------------------------------------------
if selected == 'Cover Letter' :
#====Second project of Blog generation        
    with st.container():
        st.write("")
        #st.divider()
        
        st.write("   :blue[ **Generate cover letter for Job application** ]  ")  
        multi = ''' 
        :blue[ **To generate a cover letter:** ] <small>Upload your resume in .pdf or .docx file format or your skills. Provide Role, Industry, Job Description and how approximate number of word of cover letter.</small>
        '''
        st.markdown(multi, unsafe_allow_html=True)
        
        #Create a form using st.form 
        cover_letter_form = st.form ("Cover Letter Form")
        
        with cover_letter_form:
            col1, col2, col3  =  st.columns([4, 2, 2])
            with col1:
                #uploaded_file = form.file_uploader("upload .txt or .pdf file")
                uploaded_resume = st.file_uploader("Upload resume (.pdf or .docx) :red[*] ", type=['pdf','doc','docx'])
            with col2:
                letter_length = st.number_input("Cover letter length(words) :red[*] ", 300 , 600)                
                job_title = st.text_input(" Job Title :red[*] ", max_chars =50, placeholder="Technical Project Manager")
            with col3:
                experience_years = st.number_input("Year of experience", 1 , 50)
                industry = st.text_input(" Industry", max_chars=70, placeholder="Marketing")            
            
            colbutton1, colbutton2 =  st.columns([1, 1])
            with colbutton1:
                skills = st.text_area(
                    label = "If file is not uploaded add your skills here",
                    height = 200,
                    max_chars = 4000 ,
                    placeholder = "Project Management, Scrum Master"
                    )
            with colbutton2:
                jd = st.text_area(
                    label = "Job Description :red[*] ",
                    height = 200,
                    max_chars = 6000 ,
                    placeholder = "Job Description"
                    )
            
            first_col, second_col, last_col = st.columns([4,1,5])
            with first_col:
                cl_message_container = st.container(border=False)
                with cl_message_container:
                    #cover_letter_message = st.markdown("", unsafe_allow_html=True)
                    cover_letter_message = st.error("")
            with second_col:
                cover_letter_submitted = st.form_submit_button(label="Generate")
            with last_col:
                company = st.text_input(" Applying for (Company)", max_chars=70, placeholder="Google")            

        cover_letter_message_container = st.container(border=True)
        with cover_letter_message_container:
            cover_letter_loading_indicator_container = st.container()
            cover_letter_message_response = st.success("")

        #Validation of all the fields
        if cover_letter_submitted:
            #st.write("Button clicked")
            #print(f" uploaded_resume is not None {uploaded_resume is not None}  skills is not None {skills is not None} ")
            if (uploaded_resume is not None or (skills is not None and len(skills)>0 )) and job_title and len(job_title)>0 and industry and len(industry)>0 and jd and len(jd)> 0:
                #print("We have a file or skills")
                if len(skills) >= 5:
                    #print("Skills more than 5 char found")
                    skill_text = skills
                    resume_text = ""
                    uploaded_file_error = ""
                    cover_letter_message.success("Generating cover letter, please wait...")
                    cover_letter_text = generateCoverLetter(resume_text, skills, job_title, industry, jd, company, letter_length, experience_years)
                    cover_letter_message.success("Here is cover letter :point_down: ")
                    cover_letter_message_response.success(cover_letter_text)
                    #print(cover_letter_text)
                elif uploaded_resume is None and skills is not None and len(skills) < 5:
                    #cover_letter_message.markdown("<h8 style='text-align: left; color: red'> Skills are too short to generate cover letter, add more content or upload Resume. </h8>" , unsafe_allow_html=True)
                    cover_letter_message.error("Skills are too short to generate cover letter, add more content or upload Resume..")
                elif uploaded_resume is not None and ( skills is None or len(skills) < 5):
                    #print("File found")
                    skills = ""
                    #resume_text = read_resume_file(uploaded_resume)
                    resume_text = readPdforDocFile(uploaded_resume)
                    if resume_text == "MORE_THAN_FIVE_PAGES":
                        cover_letter_message.error("PDF file contains more than 5 pages, please upload file with 5 or less pages.")
                    elif resume_text == "LESS_TEXT_IN_PDF":
                        cover_letter_message.error("File has not enough content (less than 200 charater) to generate cover letter, please reupload file with enough content.")
                    elif resume_text == "LESS_TEXT_IN_TXT":
                        cover_letter_message.error("File has not enough content to generate cover letter, please reupload file with enough content.")
                    elif resume_text == "MORE_TEXT_IN_TXT":
                        cover_letter_message.error("File is too large, please reduce text size and re-upload file.")
                    elif resume_text == "ERROR_READING_FILE":
                        cover_letter_message.error("System is not able to read provided file, please provided valid .pdf file .")
                    elif resume_text == "UNSUPPORTED_FILE_TYPE":
                        cover_letter_message.error("Unsupported file type, accepted file types are .pdf, .text, .doc or .docx ")    
                    else:
                        #print(f"resume_text {resume_text} \n skills {skills}, \n job_title  {job_title}, \n industry {industry}, \n jd {jd}, \n company {company} , \n letter_length = {letter_length}, \n experience_years = {experience_years} ")
                        #st.write("Conditions are satisfied, calling OpenAI")
                        cover_letter_message.success("Generating cover letter, please wait...")
                        with cover_letter_loading_indicator_container:
                            cover_letter_loading_indicator = st.spinner("Processing...")
                            #rjr_error_message = st.spinner("Reviewing Job Description and Resume, please wait...")
                            with cover_letter_loading_indicator:
                                cover_letter_text = generateCoverLetter(resume_text, skills, job_title, industry, jd, company, letter_length, experience_years)
                        #print(cover_letter_text)
                        cover_letter_message.success("Here is cover letter :point_down: ")
                        cover_letter_message_response.success(cover_letter_text)
                    #cover_letter_message.markdown("<h8 style='text-align: left; color: red'>{uploaded_file_error}</h8>" , unsafe_allow_html=True)
                else:
                    cover_letter_message.markdown("<h8 style='text-align: left; color: red'> Skills are too short to generate cover letter, add more content or upload Resume. </h8>" , unsafe_allow_html=True)
                    
            else:
                #print("In validation error area")
                if job_title is None or len(job_title)<=0: 
                    cover_letter_message.error(" Please provide Job Title ")
                elif industry is None or len(industry)<=0:
                    cover_letter_message.error(" Please provide Industry value ")
                elif jd is None or len(jd)<=0:
                    cover_letter_message.error(" Please provide Job Description  ")
                elif uploaded_resume is None and skills is not None and len(skills) <= 0:
                    cover_letter_message.error(" Upload Resume or add your skills. ")

            
## ----  Cover letter implementation end ----------------------------

## ----  Chat coversation start----------------------------
if selected == 'Chat Coversation':

    # Initialize session state for chat history if it doesn't exist 
    with st.container():
        st.write("   :blue[ ** Interview like Conversation with AI  ** ]  ")  
        multi = ''' 
        :blue[ **To Review and Compare skill:** ] <small>Upload your resume in .pdf or .docx file format. AI will ask you questions against job desctiption.</small>
        '''
        st.markdown(multi, unsafe_allow_html=True)

        # load_dotenv()
        # gemini_key = os.getenv("GOOGLE_API_KEY")
        # genai.configure(api_key=gemini_key)
        #model = genai.GenerativeModel("gemini-pro")

        model = getGeminProModel()
        
        #THese attributed need to be read from uploaded resume and Job Description
        resume_text = ut.resume_text
        jd_text = ut.jd_text

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

        Here is Resume: \" {resume_text}. \" 

        Here is Job Description \"{jd_text}. \" 

        """

        # Add a Gemini Chat history object to Streamlit session state
        if "chat" not in st.session_state:
            st.session_state.chat = model.start_chat(history = [])
            #st.session_state.chat = model.start_chat(prompt_template)

        if "very_first_request" not in st.session_state:
            st.session_state.very_first_request = True

        first_container = st.container(height=400, border=False)
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
        
        #TODO: THese attributed need to be read from uploaded resume and Job Description
        resume_text = ut.resume_text
        jd_text = ut.jd_text    

        audio_first_prompt_template = ut.getAudio_first_prompt()

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
