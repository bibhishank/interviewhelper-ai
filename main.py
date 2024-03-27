from dotenv import load_dotenv
from gtts import gTTS
from io import BytesIO

import streamlit as st
from streamlit_option_menu import option_menu
# from streamlit_modal import Modal
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
import os
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests
import requests
from pip._vendor import cachecontrol
from google.oauth2 import id_token
import firebase_admin
from firebase_admin import auth, exceptions, credentials, initialize_app

#Not able to install streamlit_extras.let_it_rain
# def celebration_animate():
#     rain(
#         emoji="🎈",
#         font_size=54,
#         falling_speed=5,
#         animation_length= [4,5] ,
#         #animation_length= [] "infinite",
#     )

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

st.set_page_config(page_title = PAGE_TITLE, page_icon =  icon_image, layout= "wide", menu_items=None)
#st.set_page_config(page_title = PAGE_TITLE, page_icon =  web_icon, layout= "wide", menu_items=None)


#-- below commented code is for showing Modal for Privacy Policy and Terms and Conditions
# privacy_polict_modal = Modal(key="privacy_policy",title="Privacy Policy")
# def open_privacy_popup(str):
#     with privacy_polict_modal.container():
#         st.markdown(str, unsafe_allow_html=True)

# term_condition_modal = Modal(key="terms_and_condition",title="Terms and Conditions")
# def open_term_popup(str):
#     with term_condition_modal.container():
#         st.markdown(str, unsafe_allow_html=True)

## ----  Google Analytics code for website trafic tracking  -----------------------------------------------------------
if "google_tag_found" not in st.session_state:
    st.session_state.google_tag_found = False

def inject_ga():
    GA_ID = "G-L7CQSR3TWT"
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
    #print(index_path) 
    logging.info(f'editing {index_path}')
    soup = BeautifulSoup(index_path.read_text(), features="html.parser")

    #google_tag_found = False

    for item in soup.find_all('script'):
        if 'G-L7CQSR3TWT' in item.text:
            #print(f"Line found {item.text}")
            st.session_state.google_tag_found = True

    #if not soup.find(id=GA_ID): 
    if st.session_state.google_tag_found == False: 
        bck_index = index_path.with_suffix('.bck')
        if bck_index.exists():
            shutil.copy(bck_index, index_path)  
        else:
            shutil.copy(index_path, bck_index)  
        html = str(soup)
        new_html = html.replace('<head>', '<head>\n' + GA_JS)
        index_path.write_text(new_html)

if st.session_state.google_tag_found == False:
    inject_ga()

## ----  Review and Compare skill implementation start -----------------------------------------------------------
if "last_tab_clicked" not in st.session_state:
    st.session_state.last_tab_clicked = ""

if "last_uploaded_file_name" not in st.session_state:
    st.session_state.last_uploaded_file_name = ""


def initiate_session():
            # Add a previous bot question  to Streamlit session state
        if "current_question" not in st.session_state:
            st.session_state.current_question = ""

        # Add a Gemini Chat history object to Streamlit session state
        if "very_first_request" not in st.session_state:
            st.session_state.very_first_request = True

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
               top: 5px;
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

#CSS for login button
st.markdown("""      
    <style>
        a.my_button {
            padding: 3px 6px;
            border: 1px outset buttonborder;
            border-radius: 3px;
            color: #ffffff;;
            background-color: #0099ff;
            text-decoration: none;
        }
    </style>
""",unsafe_allow_html=True)

st.markdown(
    """
    <style>
    .element-container:has(style){
        display: none;
    }
    #button-after {
        display: none;
    }
    .element-container:has(#button-after) {
        display: none;
    }
    .element-container:has(#button-after) + div button {
        background: none!important;
        border: none;
        padding: 0!important;
        text-align: left; 
        color: #5C6BC0 ;
        text-decoration: none;
        cursor: pointer;        
        }
    </style>
    """,
    unsafe_allow_html=True,
)

def load_css():
    with open("static/styles.css", "r") as f:
        css = f"<style>{f.read()}</style>"
        st.markdown(css, unsafe_allow_html=True)
 
load_css()

with open(foot_css_file) as ft_css:
    st.markdown("<style>{}</style>".format(ft_css.read()), unsafe_allow_html=True)

if "email" not in st.session_state:
    st.session_state.email = ''

after_loging_redirect_uri = "http://localhost:8501"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1" # to allow Http traffic for local dev

# Initialize Firebase app 
cred = credentials.Certificate("./assets/interviewhelperai-953c56a8958e.json")
try:
    firebase_admin.get_app()
except ValueError as e:
    initialize_app(cred)



# --- profile SECTION ---
with st.container():
    col1, col2, col3 = st.columns([2,6,2], gap="small")
    with col1:
        st.image(logo_image, width=125)
    with col2:
        #st.header("Interview Helper AI (Beta)")
        st.markdown('<center><h1>Interview Helper AI (Beta)</h1></center>', unsafe_allow_html=True)
    with col3:
        st.write("#")
        user_login_container = st.container()


@st.cache_resource(experimental_allow_widgets=True)
def getFlow():
    client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "./assets/client_secret_471004611997-9adc1u3a2verok60l2ptl3f38bf6d4hi.apps.googleusercontent.com.json")
    flow = Flow.from_client_secrets_file(
        client_secrets_file = client_secrets_file,
        scopes = ["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
        redirect_uri = after_loging_redirect_uri
    )
    return flow

def get_logged_in_user_email():
    try:
        query_params = st.query_params
        #print(f"query_params= {type(query_params.to_dict())}")
        query_param_dict = query_params.to_dict()
        request_url = after_loging_redirect_uri + "/?"
        for key in query_param_dict.keys():
            request_url += key + "=" + query_param_dict[key] + "&"
        #print(f" request_url= {request_url}")
        code = query_params.get('code')
        state = query_params.get('state')
        #print(f"First state= {state} code= {code}")
        if code:
                flow = getFlow()
                flow.fetch_token(authorization_response=request_url)
                #print("After flow.fetch_token")
                credentials = flow.credentials
                request_session = requests.session()
                cached_session = cachecontrol.CacheControl(request_session)
                token_request = google.auth.transport.requests.Request(session=cached_session)
                GOOGLE_CLIENT_ID = st.secrets["client_id"]
                
                id_info = id_token.verify_oauth2_token(
                    id_token=credentials._id_token,
                    request=token_request,
                    audience=GOOGLE_CLIENT_ID
                )
                #print(f"After getting id_info {id_info.keys()}")
                #id_info.keys() = (['iss', 'azp', 'aud', 'sub', 'email', 'email_verified', 'at_hash', 'name', 'picture', 'given_name', 'family_name', 'locale', 'iat', 'exp'])
                st.session_state["google_id"] = id_info.get("sub")
                st.session_state["user_name"] = id_info.get("name")
                st.session_state["email"] = id_info.get("email")
                #print(f'google_id = {id_info.get("sub")} user_name = {id_info.get("name")} email_id = {id_info.get("email")} picture = {id_info.get("picture")}')

                user_email = id_info.get("email")
                #creating a user in firebase
                if user_email:
                    try:
                        user = auth.get_user_by_email(user_email)
                        print(f"Existing user= {user_email}")
                    except exceptions.FirebaseError:
                        #print("In inner exception")
                        user = auth.create_user(uid=id_info.get("sub"), display_name=id_info.get("name"), email=user_email )
                        print(f"Added user to Firebase= {user_email}")
                    st.session_state.email = user.email

                #st.write(f"Hello {st.session_state['user_name']}! <br/> <a href='/'><button>Logout</button></a>")

    except Exception as e:
        print("An outer error occurred:", e)

def show_login_button():
    flow = getFlow()
    authorization_url, state = flow.authorization_url()
    with user_login_container:
        st.markdown(f'<center><a href="{authorization_url}" target="_self" class="google-sign-in-button">Login with Google</a><center>', unsafe_allow_html=True)
    get_logged_in_user_email()


def check_login():
    #st.title('Welcome!')
    #print(f"st.session_state.email={st.session_state.email}")
    if not st.session_state.email:
        #print(f"not st.session_state.email = {not st.session_state.email} = not st.session_state.email {st.session_state.email}")
        #print("calling get_logged_in_user_email()")
        get_logged_in_user_email()
        if not st.session_state.email:
            #print("calling show_login_button()")
            show_login_button()

    if st.session_state.email:
        #st.write(st.session_state.email)
        with user_login_container:
            #print(f" User name in session= {st.session_state.user_name} ")
            st.write(f'<center> {st.session_state.user_name} </center>', unsafe_allow_html=True)
            logout_col1, logout_col2, logout_col3 = st.columns([1,1,1])
            with logout_col2:
                logout_button = st.button("Logout", type="primary", key="logout_non_required")
                if logout_button:
                    st.session_state.email = ''
                    print("Calling rerun")
                    st.rerun()

check_login()

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
    expander_string = ":heavy_multiplication_x: **Upload Resume and Provide Job Description** :small_red_triangle_down: (one time activity)"
    is_expanded = True
    if "resume_text" not in st.session_state:
        st.session_state.resume_text = ""
    if "job_description_text" not in st.session_state:
        st.session_state.job_description_text = ""

    
    select_file_for_upload = ""
    if "selected_file_to_upload"  not in st.session_state:
        st.session_state.selected_file_to_upload = ""
    else:
        select_file_for_upload = st.session_state.selected_file_to_upload
    
    if "file_reuploaded_chat_update" not in st.session_state:
        st.session_state.file_reuploaded_chat_update = False

    if "file_reuploaded_audio_update" not in st.session_state:
        st.session_state.file_reuploaded_audio_update = False

    if "audio_coversation_tab_cliecked" not in st.session_state:
        st.session_state.audio_coversation_tab_cliecked = False


    #print(f"st.session_state.last_uploaded_file_name {st.session_state.last_uploaded_file_name} and  select_file_for_upload ={select_file_for_upload}")
    #print(st.session_state.last_uploaded_file_name != select_file_for_upload)
    
    if len(st.session_state.resume_text) >0 and len(st.session_state.job_description_text) > 0 :
        resume_and_jd_uploaded = True
        expander_string = " :white_check_mark: Reusme    :white_check_mark: Job Description  "
        is_expanded = False
        #print("in new condition 1")
    elif len(st.session_state.resume_text) >0 and len(st.session_state.job_description_text) > 0 and st.session_state.last_uploaded_file_name != select_file_for_upload:
        #print("in new condition2")
        resume_and_jd_uploaded = False
        expander_string = " :white_check_mark: Reusme    :heavy_multiplication_x: **Upload changes** :small_red_triangle_down:  "
        is_expanded = True

    elif len(st.session_state.resume_text) <=0 and len(st.session_state.job_description_text) > 0:
        #print("in new condition3")
        resume_and_jd_uploaded = False
        expander_string = " :white_check_mark: Reusme    :heavy_multiplication_x: **Provide Job Description** :small_red_triangle_down:  "
        is_expanded = True

    elif len(st.session_state.resume_text) >0 and len(st.session_state.job_description_text) <=0:    
        #print("in new condition4")
        resume_and_jd_uploaded = False
        expander_string = " :heavy_multiplication_x: **Upload Reusme** :small_red_triangle_down:    :white_check_mark:Job Description  "
        is_expanded = True
    elif len(st.session_state.resume_text) <=0 and len(st.session_state.job_description_text) <=0:
        #print("in new condition5")
        resume_and_jd_uploaded = False
        expander_string = " :heavy_multiplication_x: **Upload Resume and Provide Job Description** :small_red_triangle_down: (one time activity)"
        is_expanded = True

    #resume_jd_message_container = st.container(border=True)
    #print(f"is_expanded= {is_expanded}") 

    resume_job_expander_container = st.container()
    with resume_job_expander_container:
        resume_job_expander = st.expander( expander_string, expanded=is_expanded)    
        with resume_job_expander:
            #print("Drawing expander")
            resume_col, jd_col =  st.columns([1, 1])
            with resume_col:
                st.write("")
                resume_main_file = st.file_uploader("Upload resume (.pdf or .docx) :red[*] ", type=['pdf','docx'], key="resume_file_key")
                if resume_main_file:
                    st.session_state.selected_file_to_upload = resume_main_file.name
            with jd_col:
                jd_main_content = st.text_area(
                    label = "Job Description :red[*] ",
                    height = 75,
                    max_chars = 9000 ,
                    placeholder = "Job Description", key="job_desc_key"
                    )
            resume_jd_upload_button_col, resume_jd_upload_message_col  =  st.columns([1, 9])
            with resume_jd_upload_button_col:
                m = st.markdown("""
                    <style>
                    div.stButton > button:first-child {background-color: #0099ff;color:#ffffff;}
                    </style>""", unsafe_allow_html=True)
                
                resume_jd_submit_button = st.button(label="Upload")
            with resume_jd_upload_message_col:    
                resume_jd_message_container = st.container(border=False)
                with resume_jd_message_container:
                    resume_jd_message_container = st.text("")
        
        if resume_jd_submit_button:
            #print("Submitted... ")
            if(resume_main_file is not None and jd_main_content and len(jd_main_content)> 50):
                resume_jd_message_container.success("Process started")
                try:
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
                        st.session_state.last_uploaded_file_name = resume_main_file.name
                        ut.setJobDescriptionText(jd_main_content)
                        ut.verifyResumeandJDSize()
                        st.session_state.resume_text = ut.getResumeText()
                        st.session_state.job_description_text = jd_main_content
                        st.session_state.file_reuploaded = True
                        st.session_state.file_reuploaded_chat_update = True
                        st.session_state.file_reuploaded_audio_update = True
                        #print(f"st.session_state.resume_text = {st.session_state.resume_text} \n and \n st.session_state.job_description_text = {st.session_state.job_description_text} ")
                        expander_string = " :white_check_mark: Reusme    :white_check_mark: Job Description  "
                        is_expanded = False
                        #resume_jd_message_container.success("File uploaded sucessfully")
                        resume_jd_message_container.write("File uploaded sucessfully")
                except Exception as e:
                    print("An error occurred:", e)

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
    #print("Current tab = Skills & JD review")
    #print(f"Last tab ={st.session_state.last_tab_clicked}")
    last_tab_selected = st.session_state.last_tab_clicked
    st.session_state.last_tab_clicked = "Skills & JD review"

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
                review_resume_button_container = st.empty()
                with review_resume_button_container:
                    m = st.markdown("""
                    <style>
                    div.stButton > button:first-child {background-color: #0099ff;color:#ffffff;}
                    </style>""", unsafe_allow_html=True)
                    review_resume_button = st.button(label="Review skill alignments with Job Description.")
                    #st.button(label="My button", style="background-color: #DD3300; color:#eeffee; border-radius: 0.75rem;")
            
            rjr_message_container = st.container()
            with rjr_message_container:
                rjr_loading_indicator_container = st.container()
                #rjr_error_message = st.success("")
                #rjr_message_response = st.success()
                rjr_message_response = st.empty()
                if len(st.session_state.skillJDReview_value) > 0 :
                    rjr_message_response.success(st.session_state.skillJDReview_value)
                    if not st.session_state.email:
                        review_resume_button_container.empty()
                        review_resume_button_container.success("Please login to review again")


            if review_resume_button:
                with rjr_loading_indicator_container:
                    rjr_loading_indicator = st.spinner("Reviewing skills alignment for the Job Description, please wait...")
                    #rjr_error_message = st.spinner("Reviewing Job Description and Resume, please wait...")
                    try:
                        with rjr_loading_indicator:
                            rjr_response = getSkillAndRequirementReview(st.session_state.resume_text, st.session_state.job_description_text)
                        #print(cover_letter_text)
                        st.session_state.skillJDReview_loaded = True
                        st.session_state.skillJDReview_value = rjr_response
                        rjr_message_response.empty()
                        rjr_message_response.success(rjr_response)

                        if not st.session_state.email:
                            #print(f"Email not found and value shows: {st.session_state.email}")
                            review_resume_button_container.empty()
                            review_resume_button_container.success("Please login to review again")

                    except Exception as e:
                        print("An error occurred:", e)

    else:
        st.toast("Upload Resume and provide Job Description")
    #st.write(st.session_state)

## ----  Interview Questions and sample answers implementation start -----------------------------------------------------------
if selected == 'Interview Q & A':
    #print("Current tab = Interview Q & A")
    #print(f"Last tab ={st.session_state.last_tab_clicked}")
    st.session_state.last_tab_clicked = "Interview Q & A"

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
                qa_button_container = st.empty()
                with qa_button_container:
                    m = st.markdown("""
                    <style>
                    div.stButton > button:first-child {background-color: #0099ff;color:#ffffff;}
                    </style>""", unsafe_allow_html=True)
                    interview_que_ans_button = st.button(label="Generate interview questions and ideal asnswers.")
        
            qa_message_container = st.container()
            with qa_message_container:
                qa_loading_indicator_container = st.container()
                qa_message_response = st.empty()
                if len(st.session_state.questionAnswer_value) > 0:
                    qa_message_response.success(st.session_state.questionAnswer_value)
                    if not st.session_state.email:
                        qa_button_container.empty()
                        qa_button_container.success("Please login to regenerate Q & A")


            if interview_que_ans_button:
                with qa_loading_indicator_container:
                    interview_que_ans_loading = st.spinner("Generating interview questions and ideal asnswers, please wait...")
                    try:
                        with interview_que_ans_loading:
                            qa_response = generateQuestionAnswers(st.session_state.resume_text, st.session_state.job_description_text)
                        #st.session_state.skill = True
                        st.session_state.questionAnswer_value = qa_response   
                        qa_message_response.empty()                 
                        qa_message_response.success(qa_response)
                        
                        if not st.session_state.email:
                            #print(f"Email not found and value shows: {st.session_state.email}")
                            qa_button_container.empty()
                            qa_button_container.success("Please login to regenerate Q & A")

                    except Exception as e:
                        print("An error occurred:", e)


## ----  Cover letter implementation start -----------------------------------------------------------
if selected == 'Cover Letter' :
    #print("Current tab = Cover Letter")
    #print(f"Last tab ={st.session_state.last_tab_clicked}")
    st.session_state.last_tab_clicked = "Cover Letter"

    if len(st.session_state.resume_text) > 0 and len(st.session_state.job_description_text) > 0:
        cover_letter_container = st.container(border=True)
        with cover_letter_container:
            cover_letter_col1, cover_letter_col2, cover_letter_col3 = st.columns([1,1,1])
            with cover_letter_col1:
                st.markdown("""
                            <small>This tool utilizes both the job description and resume to generate a tailored cover letter for your job application. To ensure greater precision, kindly include the job title and company name. Incorporating these details enhances the effectiveness of the generated letter. </small>
                               """, unsafe_allow_html=True)  
            with cover_letter_col2:
                job_title = st.text_input(" Job Title :red[*] ", max_chars =50, placeholder="Technical Project Manager", key="job_title")
            with cover_letter_col3:
                company = st.text_input(" Applying for (Company) :red[*]", max_chars=70, placeholder="Google", key="company_input")

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
                cover_letter_button_container = st.empty()
                with cover_letter_button_container:
                    m = st.markdown("""
                        <style>
                        div.stButton > button:first-child {background-color: #0099ff;color:#ffffff;}
                        </style>""", unsafe_allow_html=True)
                    cover_letter_button = st.button(label="Generate Cover Letter")
            
            cover_letter_message_container = st.container()
            with cover_letter_message_container:
                cover_letter_loading_indicator_container = st.container()
                cover_letter_message_response = st.empty()
                if len(st.session_state.coverLetter_value) > 0:
                    cover_letter_message_response.success(st.session_state.coverLetter_value)
                    if not st.session_state.email:
                        cover_letter_button_container.empty()
                        cover_letter_button_container.success("Please login to regenerate Cover leter")


            if cover_letter_button:
                #print(f"job_title: {job_title is None}  len(job_title)= {len(job_title)} company: {company is not None}  len(company) {len(company)}")
                try:
                    if len(job_title) >1 and len(company) >1:
                        #print("Condition satisfied")
                        with cover_letter_loading_indicator_container:
                            cover_letter_loading_indicator = st.spinner("Generating cover letter, please wait...")
                            with cover_letter_loading_indicator:
                                cover_letter_text = generateCoverLetter(st.session_state.resume_text, job_title, st.session_state.job_description_text, company)
                            st.session_state.coverLetter_value = cover_letter_text
                            cover_letter_message_response.empty()
                            #print(f"Cover Letter text: {cover_letter_text}")
                            cover_letter_message_response.success(cover_letter_text)
                            
                            if not st.session_state.email:
                                #print(f"Email not found and value shows: {st.session_state.email}")
                                cover_letter_button_container.empty()
                                cover_letter_button_container.success("Please login to regenerate Cover leter")

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
    #print("Current tab = Chat Coversation")
    #print(f"Last tab ={st.session_state.last_tab_clicked}")
    st.session_state.last_tab_clicked = "Chat Coversation"

    #TODO: introduce get started button
    if "skill_review_button_clicked" not in st.session_state:
        st.session_state.skill_review_button_clicked = False
            
    # Initialize session state for chat history if it doesn't exist 
    if len(st.session_state.resume_text) > 0 and len(st.session_state.job_description_text) > 0:
        chat_conversation_container = st.container(border=True)
        with chat_conversation_container:
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

            if "chat_very_first_request" not in st.session_state:
                st.session_state.chat_very_first_request = True

            first_container = st.container(height=380, border=False)
            second_container = st.container()
            with first_container:
                for message in st.session_state.chat.history:
                    x = message.parts[0].text.find("Role: Chat Practice Partner for interview")
                    if x < 0:
                        with st.chat_message(ut.role_to_streamlit(message.role)):
                            st.markdown(message.parts[0].text)

                if st.session_state.chat_very_first_request == True or st.session_state.file_reuploaded_chat_update == True:
                    if st.session_state.file_reuploaded_chat_update == True:
                        print("File update detected")
                    with st.spinner('💡 Generating question, please wait'):
                        chat_response = st.session_state.chat.send_message(ut.getChat_first_prompt(st.session_state.resume_text, st.session_state.job_description_text)) 
                        st.session_state.file_reuploaded_chat_update = False
                    #print(f"Sending first request: {first_prompt_template}")
                    if chat_response and len(chat_response.text) >=0:
                        st.session_state.chat_very_first_request = False
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
                    #print(st.session_state.chat_very_first_request)
                    second_prompt_with_ans = "Answer:" + second_prompt
                    with st.spinner('💡 Processing'):
                        second_response = st.session_state.chat.send_message(second_prompt_with_ans)
                    #print(f"Sending second request: {prompt}")
                    
                    if second_response and len(second_response.text) >=0:
                        st.session_state.chat_very_first_request = False
                        # Display last 
                        with st.chat_message("assistant"):
                            st.markdown(second_response.text)

## ----  Chat coversation end----------------------------


## ----  Audio coversation implementation starts----------------------------
if selected == 'Audio Conversation':
    #print("Current tab = Audio Conversation")
    #print(f"Last tab ={st.session_state.last_tab_clicked}")
    if(st.session_state.last_tab_clicked != "Audio Conversation"):
        st.session_state.audio_coversation_tab_cliecked = True
    
    st.session_state.last_tab_clicked = "Audio Conversation"

    if "audio_conv_button_clicked" not in st.session_state:
        st.session_state.audio_conv_button_clicked = False

    

    #print(f"setting in the beginning = { st.session_state.audio_coversation_tab_cliecked } ")

    if len(st.session_state.resume_text) > 0 and len(st.session_state.job_description_text) > 0:
        audio_conversation_container = st.container(border=True)
        with audio_conversation_container:
            multi = ''' 
            <small>Interview like audio conversation with AI, opportunity to practice responding to these questions in a simulated environment. Through continuous repetition and practice, you can refine your answers and improve  overall interview performance, aided by the AI's feedback and guidance throughout the process. </small>
            '''
            st.markdown(multi, unsafe_allow_html=True)
            st.markdown( """ <style>
                        #rcorners2 {
            border-radius: 25px;
            border: 2px solid #73AD21;
            padding: 20px; 
            }
            </style>
                        """,  unsafe_allow_html=True)

            audio_conf_info_col1, audio_conf_info_col2, audio_conf_info_col3 = st.columns([1,1,1])
            with audio_conf_info_col1:
                st.markdown(f"<p id='rcorners2'> 🦾 Offers individuals an opportunity to practice responding to various questions commonly asked in interviews. </p>", unsafe_allow_html=True)
            with audio_conf_info_col2:
                st.markdown(f"<p id='rcorners2'> 🦾 By repeatedly answering questions from the AI, individuals can improve their overall interview performance over time. </p>", unsafe_allow_html=True)
            with audio_conf_info_col3:
                st.markdown(f"<p id='rcorners2'> 🦾 This personalized feedback aids individuals in honing their interview skills and building confidence for actual interviews. </p>", unsafe_allow_html=True)
            
            initiate_session()

            audio_conversation_button_container = st.empty()
            if st.session_state.audio_conv_button_clicked == False and len(st.session_state.resume_text) > 0 and len(st.session_state.job_description_text) > 0:
                with audio_conversation_button_container.container(border=True):
                    #print(f"Debug 1 {st.session_state.skill_review_button_clicked}")
                    chat_btn_col1, chat_btn_btn_col2, chat_btn_btn_col3 = st.columns([1,1,1])
                    with chat_btn_btn_col2:                
                        m = st.markdown("""
                            <style>
                            div.stButton > button:first-child {background-color: #0099ff;color:#ffffff;}
                            </style>""", unsafe_allow_html=True)
                        audio_conversation_button = st.button(label="Let's get audio conversation started.")
                    if audio_conversation_button:
                        st.session_state.audio_conv_button_clicked = True
                        st.session_state.audio_coversation_tab_cliecked = False
                        audio_conversation_button_container.empty()
            else:
                audio_conversation_button_container.empty()

            if(st.session_state.audio_conv_button_clicked ) and len(st.session_state.resume_text) > 0 and len(st.session_state.job_description_text) > 0:
                st.session_state.audio_conv_button_clicked = True
                #print("Let's get conversation started, Button action.")
                audio_model = ut.getGeminProModel()
                # Add a Gemini Chat history object to Streamlit session state
                if "audio_chat" not in st.session_state:
                    st.session_state.audio_chat = audio_model.start_chat(history = [])

                if "audio_very_first_request" not in st.session_state:
                    st.session_state.audio_very_first_request = True

                audio_first_container = st.container(height=200, border=True)
                #audio_second_container = st.container()
                audio_second_container = st.empty()
                with audio_first_container:
                    if st.session_state.audio_very_first_request == True or st.session_state.file_reuploaded_audio_update == True:
                        if st.session_state.file_reuploaded_audio_update == True:
                            #print("File update detected for audio")
                            st.session_state.audio_chat = audio_model.start_chat(history = [])
                        with st.spinner('💡 Generating question, please wait...'):
                            audio_first_prompt_template = ut.getAudio_first_prompt(st.session_state.resume_text, st.session_state.job_description_text)
                            st.session_state.file_reuploaded_audio_update = False
                            response_for_audio1 = st.session_state.audio_chat.send_message(audio_first_prompt_template) 
                            #print("First response received")
                        if response_for_audio1 and len(response_for_audio1.text) >=0:
                            st.session_state.current_question = response_for_audio1.text
                            st.session_state.audio_very_first_request = False
                            st.session_state.audio_coversation_tab_cliecked = False
                            audio_conversation_button_container.empty()
                            #print("First response received, set all the variables")

                        with st.chat_message("assistant"):
                            #print("Adding message with assisatant")
                            #print("Writing click message and audio content")
                            #with st.spinner('💡 Generating question, please wait...'):
                            text = f"<h5 style='text-align: left; '> Click on play to liesten to the question </h5>"
                            sound_file = BytesIO()
                            tts = gTTS(response_for_audio1.text, lang='en')
                            tts.write_to_fp(sound_file)
                            st.markdown(text, unsafe_allow_html=True)
                            st.audio(sound_file)
                            #print("Done with writing video content")
                        audio_conversation_button_container.empty()

                    # Accept user's next message, add to context, resubmit context to Gemini
                    with audio_second_container:
                        m = st.markdown("""
                            <style>
                            div.stButton > button:first-child {background-color: #0099ff;color:#ffffff;}
                            </style>""", unsafe_allow_html=True)
                        nextaudio_btn_col1, nextaudio_btn_btn_col2, nextaudio_btn_btn_col3 = st.columns([1,1,1])
                        with nextaudio_btn_btn_col2:                
                            audio_next_question = st.button(" Generate next question ")
                    
                    #print(f"st.session_state.audio_conv_button_clicked = {st.session_state.audio_conv_button_clicked}  st.session_state.audio_coversation_tab_cliecked ={st.session_state.audio_coversation_tab_cliecked}")
                    tmp_container = st.empty()
                    if st.session_state.audio_conv_button_clicked and st.session_state.audio_coversation_tab_cliecked:
                        #print("Tab clicked when second time and showing old questions")
                        audio_first_container.empty()
                        with tmp_container:
                            with st.chat_message("assistant"):
                                #Store this response, as a current question in session, and move current question value to previous question
                                with st.spinner('💡 Processing...'):
                                    text = f"<h5 style='text-align: left; '> Click on play to liesten to the question </h5>"
                                    #print(text)
                                    st.markdown(text, unsafe_allow_html=True)
                                    second_sound_file = BytesIO()
                                    tts1 = gTTS(st.session_state.current_question, lang='en')
                                    tts1.write_to_fp(second_sound_file)
                                    st.audio(second_sound_file)
                                    st.session_state.audio_coversation_tab_cliecked = False

                    if audio_next_question:
                        #print("Button click event started")
                        prompt = "NO Answer" 
                        tmp_container.empty()
                        audio_first_container.empty()
                        with st.spinner('💡 Getting next question...'):
                            response_for_audio2 = st.session_state.audio_chat.send_message(prompt)                    
                        if response_for_audio2 and len(response_for_audio2.text) >=0:
                            st.session_state.very_first_request = False
                        audio_first_container.empty()
                        st.session_state.audio_coversation_tab_cliecked = False

                        with st.chat_message("assistant"):
                            #Store this response, as a current question in session, and move current question value to previous question
                            st.session_state.current_question = response_for_audio2.text
                            text = f"<h5 style='text-align: left; '> Click on play to liesten to the question </h5>"
                            #print(text)
                            st.markdown(text, unsafe_allow_html=True)
                            second_sound_file = BytesIO()
                            tts1 = gTTS(response_for_audio2.text, lang='en')
                            tts1.write_to_fp(second_sound_file)
                            st.audio(second_sound_file)
  

##- Celebration with dropping ballon or any other emoji
#celebration_animate()
#--- Footer code 
st.write("#")
st.write("#")
footer_container = st.container(border=True)
EMAIL = "bibhishan_k@yahoo.com"
MOBILE = "+1 (408)931-0588"
LOCATION = "Newark CA, USA"
WEBSITE = "www.bkaradkar.net"
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
        st.subheader ("Contact Info")        
        css_example = f'''
        <i class="fa-solid fa-envelope"></i> {EMAIL}
        
        <i class="fa-solid fa-location-dot"></i> {LOCATION}

        <i class="fa-solid fa-user-tie"></i> {WEBSITE}
        '''

        #Mobile number removed from contact information
        #<i class="fa-solid fa-mobile"></i> {MOBILE}

        st.write(css_example,unsafe_allow_html=True)

        #--- Bacuase of popup and modal issues in Streamlit, removing below links we will add them in future
        # st.subheader ("Policies")
        # st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
        
        #<button onclick="location.href='http://www.example.com'" type="button">www.example.com</button>
    
        # privacy_policy = st.button(label='Privacy Policy', key="policy_btn")
        # if privacy_policy:
        #     open_privacy_popup(hc.pricacy_policy_html_str)
        # #st.markdown("<a style='text-align: left; color: #5C6BC0 ; text-decoration: none;' href='https://ww.google.com' target='_blank'> Privacy Policy </a>" , unsafe_allow_html=True)
        # st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
        # term_condition = st.button(label='Terms and Conditions', key="terms_btn")
        # if term_condition:
        #     open_term_popup(hc.term_condition_html_str)
        # #st.markdown("<a style='text-align: left; color: #5C6BC0 ; text-decoration: none;' href='https://ww.google.com' target='_blank'> Terms and Conditions </a>" , unsafe_allow_html=True)
        # st.subheader ("Support")
        # st.markdown("<a style='text-align: left; color: #5C6BC0 ; text-decoration: none;' href='https://ww.google.com' target='_blank'> Disclaimer </a>" , unsafe_allow_html=True)
        # st.markdown("<a style='text-align: left; color: #5C6BC0 ; text-decoration: none;' href='https://ww.google.com' target='_blank'> Helps and FAQs </a>" , unsafe_allow_html=True)
    
    with col3:
        st.subheader("Social Media")
        #st.markdown(""" ‹a style="color: #SC6BC0; text-decoration: none;" href="https://twitter.com"> <i class-"fa-brands fa-instagram"></i> </a›""", unsafe_allow_html = True)
        #<a style="color: #sc6bc0; text-decoration: none;" href="https://bkaradkar.net"> <i class="fa-brands fa-instagram"></i> </a>
        #<a style="color: #sc6bc0; text-decoration: none;" href="https://bkaradkar.net"> <i class="fa-brands fa-twitter"></i> </a>        
        social_media = f""" 
                                                                                                                        
        <a style="color: #sc6bc0; text-decoration: none;" href="https://www.linkedin.com/in/bibhishan-karadkar-910ba77/"> <i class="fa-brands fa-linkedin fa-2xl" style="color: #3a88fe;"></i> </a>
        <a style="color: #sc6bc0; text-decoration: none;" href="https://bkaradkar.net"> <i class="fa-brands fa-youtube fa-2xl" style="color: #e32400;"></i> </a>
        """
        st.write(social_media, unsafe_allow_html=True)

        #st.write(f'<i class="fa-solid fa-user-tie"></i> {WEBSITE}', unsafe_allow_html=True)
