import os
from dotenv import load_dotenv
import google.generativeai as genai
import PyPDF2

from pdfminer.layout import LTTextBoxHorizontal
from pdfminer.high_level import extract_pages
import docx2txt
import io

load_dotenv()
gemini_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=gemini_key)

#Funtion to generate random HTML color code
def getRandomColor():
  import random
  r = lambda: random.randint(0,255)
  return '#%02X%02X%02X' % (r(),r(),r())

#===================================== Set up the model
generation_config = {
  "temperature": 0.7,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 2048,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
]

#---------------------------------------------------------------------------------------------
# This function create and returns model
def getGeminProModel():
    model = genai.GenerativeModel(model_name="gemini-pro",
                              generation_config=generation_config,
                              safety_settings=safety_settings)
    return model

##===================================== Set up the model

# Gemini uses 'model' for assistant; Streamlit uses 'assistant'
def role_to_streamlit(role):
  if role == "model":
    return "assistant"
  else:
    return role

#---------------------------------------------------------------------------------------------

resume_text = ""
jd_text = ""

#---------------------------------------------------------------------------------------------
def setResumeText(file_text):
    print("setting value in resume_text global variable")
    global resume_text 
    resume_text = file_text

#---------------------------------------------------------------------------------------------
def getResumeText():
   print("Returning value in resume_text global variable")
   return resume_text

#---------------------------------------------------------------------------------------------
def setJobDescriptionText(jd_text_input):
   global jd_text
   jd_text = jd_text_input

#---------------------------------------------------------------------------------------------
def getJobDescription():
   print("Returning value in job description global variable")
   return jd_text

#---------------------------------------------------------------------------------------------
def verifyValues():
   print(f"resume_text: \n {resume_text}")
   print(f"jd_text: \n {jd_text}")
#---------------------------------------------------------------------------------------------
def verifyResumeandJDSize():
   print(f"resume_text: \n {len(resume_text)} character")
   print(f"jd_text: \n {len(jd_text)} character")

#---------------------------------------------------------------------------------------------
# .pdf file parser , returns text back
def readPdfFile(pdf_file_path):
  #text = ""
  #for page in extract_text_from_pdf(pdf_file_path):
  #  text += ' ' + page
  #return text
  file_text = ""
  page_count = 0
  
  try:
    pdf_reader = PyPDF2.PdfReader(pdf_file_path)
    number_of_pages = len(pdf_reader.pages)
    if number_of_pages > 5:
       return "MORE_THAN_FIVE_PAGES"
    for page_layout in extract_pages(pdf_file_path):
      page_count +=1
      print(f"Looking for pages {page_count}")
      for element in page_layout:
          if isinstance(element, LTTextBoxHorizontal):
            #lines.extend(element.get_text().splitlines())
            file_text += element.get_text() + '\n'

    text_length_char = len(file_text)
    if text_length_char < 200:
      return "LESS_TEXT_IN_PDF"
    if text_length_char > 15000:
      return "MORE_TEXT_IN_PDF"
    
    setResumeText(file_text)
    return "SUCCESS"
  except Exception as e:
     raise Exception ("error reading the PDF file")
     return "ERROR_READING_FILE"

#---------------------------------------------------------------------------------------------
def readDocFile(doc_path):
    '''
    Helper function to extract plain text from .doc or .docx files

    :param doc_path: path to .doc or .docx file to be extracted
    :return: string of extracted text
    '''
    temp = docx2txt.process(doc_path)
    return temp
    st.write(temp)
    st.write("---------------------------------------------------------------------------------------------")
    text = [line.replace('\t', ' ') for line in temp.split('\n') if line]
    #return ' '.join(text)

#---------------------------------------------------------------------------------------------
#Function to identify uploaded resume file type and call parser method
def readPdforDocFile(file):
  if file.name.endswith(".pdf"):
    print("PDF")
    return readPdfFile(file)
  elif file.name.endswith(".docx") or file.name.endswith(".doc"):
     return readDocFile(file)
  else:
     return "UNSUPPORTED_FILE_TYPE"

#Output should be in bulleted formats

#-----------------------------------------------------------------------------------------------------------
# This function create prompt template to get the interview question in text format to be converted in Audio
def getAudio_first_prompt(in_resume_text, in_job_description_text):
  audio_first_prompt_template = f"""Role: Chat Practice Partner for interview
    Topic: Job interview
    Style: Casual, respectful, not too enthusiastic or flowery.

    Steps:
    From the provided Resume and Job Description, initiate with a topic-specific interview question. 

    Ask one question at a time.

    Analyze job description and gather company information and influence questions with that information.

    Very first time user, will just say "Lets get started", then provide a first questions. There will not be answer provided.

    If there is "Answer" available in users request, review the answer, and provide next one question. 
    If there is "NO Answer" text mentioned in user request, ignore the request and provide the next question.
        
    Example:
    Question: "Can you share details on your last project ?”

    Here is Resume: \" {in_resume_text}. \" 

    Here is Job Description \"{in_job_description_text}. \" 

    """
  return audio_first_prompt_template

def printMessage():
   print("Testing Utils.py")

#printMessage()

#-----------------------------------------------------------------------------------------------------------