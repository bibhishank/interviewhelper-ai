import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_extras.let_it_rain import rain #For animation

import json
import ast
from CoverLetterGenerator import generateCoverLetter, readPdforDocFile


def celebration_animate():
    rain(
        emoji="🎈",
        font_size=54,
        falling_speed=5,
        animation_length= [4,5] ,
        #animation_length= [] "infinite",
    )

number_of_pages = 0
text_length_char = 0
text_length_char_txt = 0
all_page_text = ""

PAGE_TITLE = "Interview Helper AI"
PAGE_ICON = ":large_green_circle:"    # :wave:"    #:technologist"

st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout= "wide",menu_items=None)
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

# Remove whitespace from the top of the page and sidebar
st.markdown("""
        <style>
               .css-18e3th9 {
                    padding-top: 0rem;
                    padding-bottom: 10rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
               .css-1d391kg {
                    padding-top: 3.5rem;
                    padding-right: 1rem;
                    padding-bottom: 3.5rem;
                    padding-left: 1rem;
                }
        </style>
        """, unsafe_allow_html=True)


with st.container():
    selected = option_menu(
        menu_title = None,
        options = ['Interview Questions' , 'Cover Letter', 'Chat Coversation', 'Audio Conversation'],
        #add these names from https://icons.getbootstrap.com    
        icons = ['list-columns-reverse', 'envelope-paper', 'chat-left-text-fill', 'mic'], 
        orientation = 'horizontal',
        styles={
        "container": {"padding_top" : "0", "padding_right" : "10", "padding_left" : "5", "padding_bottom" : "10"}
        #"container": {"padding": "0px", "margin":"0px", "width":"0px"}
        #"container": {"padding": "0px", "overflow": "auto",    "width":"100%", "border": "3px solid green;"}
        #"container": {"width":"100%"}
        }
    )


if selected == 'Interview Questions' : 
    with st.container():
        st.write("I am in Interview Questions")

## ----  Cover letter implementation start
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
                uploaded_resume = st.file_uploader("Upload resume (.pdf or .docx)")
            with col2:
                letter_length = st.number_input("Cover letter length(words)", 300 , 600)                
                job_title = st.text_input(" Job Title ", max_chars =50, placeholder="Technical Project Manager")
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
                    label = "Job Description",
                    height = 200,
                    max_chars = 4000 ,
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
                    #cover_letter_message.markdown("<h8 style='text-align: left; color: red'>Conditions are satisfied, calling OpenAI</h8>" , unsafe_allow_html=True)
                    #print(f"resume_text {resume_text} \n skills {skills}, \n job_title  {job_title}, \n industry {industry}, \n jd {jd}, \n company {company} , \n letter_length = {letter_length}, \n experience_years = {experience_years} ")
                    #cover_letter_message.markdown("<h8 style='text-align: left; color: red'>Generation cover letter, please wait</h8>" , unsafe_allow_html=True)
                    cover_letter_message.success("Generating cover letter, please wait...")
                    cover_letter_text = generateCoverLetter(resume_text, skills, job_title, industry, jd, company, letter_length, experience_years)
                    cover_letter_message.success("Here is cover letter :point_down: ")
                    cover_letter_message_response.success(cover_letter_text)
                    print(cover_letter_text)
                elif uploaded_resume is None and skills is not None and len(skills) < 5:
                    #cover_letter_message.markdown("<h8 style='text-align: left; color: red'> Skills are too short to generate cover letter, add more content or upload Resume. </h8>" , unsafe_allow_html=True)
                    cover_letter_message.error("Skills are too short to generate cover letter, add more content or upload Resume..")
                elif uploaded_resume is not None and ( skills is None or len(skills) < 5):
                    print("File found")
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
                        print(f"resume_text {resume_text} \n skills {skills}, \n job_title  {job_title}, \n industry {industry}, \n jd {jd}, \n company {company} , \n letter_length = {letter_length}, \n experience_years = {experience_years} ")
                        #st.write("Conditions are satisfied, calling OpenAI")
                        cover_letter_message.success("Generating cover letter, please wait...")
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

            
## ----  Cover letter implementation end



if selected == 'Chat Coversation' : 
    with st.container():
        st.write("I am in Chat Coversation")
if selected == 'Audio Conversation' :
    with st.container():
        st.write("I am in Audio Conversation")

##- Celebration with dropping ballon or any other emoji
#celebration_animate()
