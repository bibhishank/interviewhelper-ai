import os
from dotenv import load_dotenv
import google.generativeai as genai
import PyPDF2
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LTTextBoxHorizontal
from pdfminer.high_level import extract_pages
import docx2txt
import io

load_dotenv()
gemini_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=gemini_key)

# Set up the model
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

number_of_pages = 0
text_length_char = 0

#---------------------------------------------------------------------------------------------
# .pdf file parser , returns text back


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
      return "LESS_TEXT_IN_TXT"
    if text_length_char > 15000:
      return "MORE_TEXT_IN_TXT"
    
    return file_text
  except Exception as e:
     raise Exception ("error reading the PDF file")
     return "ERROR_READING_FILE"


#---------------------------------------------------------------------------------------------
#Function to identify uploaded resume file type and call parser method
def readPdforDocFile(file):
  if file.name.endswith(".pdf"):
    #print("PDF")
    return readPdfFile(file)
  elif file.name.endswith(".doc"):
     print("Doc")
  elif file.name.endswith(".docx"):
    print("Docx")
  else:
     return "UNSUPPORTED_FILE_TYPE"

#Output should be in bulleted formats

#---------------------------------------------------------------------------------------------
#Generate cover letter calling Gemini Pro  
def generateCoverLetter(resume_text, skills, job_title, industry, jd, company, letter_length, experience_years):
  resume_skills_experience_prompt = ""
  company_prompt = ""
  experience_years_prompt = ""
  if resume_text is not None and len(resume_text) > 0:
     #global resume_skills_experience_prompt 
     resume_skills_experience_prompt = f"My personal details, professional experience, skills are available in my resume here,  \"{resume_text}\"  "
  if skills is not None and len(skills) > 0:
     resume_skills_experience_prompt = f"Skills are \"{skills}\". "
  if company is not None and len(company) > 0:
     company_prompt = f" Cover letter is for a company \"{company}\". "
  if experience_years is not None and experience_years > 0:
     experience_years_prompt = f"Total experience is {experience_years} years."

  #print(f"resume_skills_experience_prompt {resume_skills_experience_prompt}, \n job_title  {job_title}, \n industry {industry}, \n jd {jd}, \n company_prompt {company_prompt} , \n letter_length = {letter_length}, \n experience_years_prompt = {experience_years_prompt} ")

  prompt_parts = [
    f""" I want you to act as a job seeker. 
    Write a conversational, more than {letter_length} words cover letter for a \"{job_title}\" role in the \"{industry}\" industry. 
    {company_prompt}
    {experience_years_prompt}
    {resume_skills_experience_prompt}
    Job description as \"{jd}\" 
    Complete the last sentence. 
    """
  ]

  #print("\n\n\n\n\n")
  #print(prompt_parts)
  #return "Wait for the responde"
  model = genai.GenerativeModel(model_name="gemini-pro",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

  #response = model.generate_content(prompt_parts)

  responses = model.generate_content(prompt_parts, stream=True)
  response_stream = ""
  for response in responses:
    #print(response.text)
    response_stream += response.text

  #print(response_stream)
  return response_stream
#---------------------------------------------------------------------------------------------
#print("I am running")
  
#============= File reading with PyPDF2, issue with this was, spaces between the words were getting disappeared from the output text 
  # def read_resume_file(file):
  #   if file.name.endswith(".pdf"):
  #       try:
  #           pdf_reader = PyPDF2.PdfReader(file)
  #           text = ""
  #           global number_of_pages
  #           number_of_pages = len(pdf_reader.pages)
  #           if number_of_pages > 5:
  #               return "MORE_THAN_FIVE_PAGES"
  #           for page in pdf_reader.pages:
  #               #text+= page.extract_text()
  #               text+= page.extractText()
  #           global text_length_char
  #           text_length_char = len(text)
  #           if text_length_char < 500:
  #               return "LESS_TEXT_IN_TXT"
  #           if text_length_char > 8000:
  #               return "MORE_TEXT_IN_TXT"
  #           return text
  #       except Exception as e:
  #           print("Error-----------", e.with_traceback)
  #           raise Exception ("error reading the PDF file")

  #   elif file.name.endswith(".txt"):
  #       text_file_text = file.read().decode("utf-8")
  #       global text_length_char_txt
  #       text_length_char_txt =  len(text_file_text) 
  #       return text_file_text
  #   else:
  #       raise Exception(
  #           "unsupported file format only pdf and text file suppoted")


#-----------------------------------------This code works for absulute path but not uploaded file--------------------
# def extract_text_from_pdf(pdf_path):
#     with open(pdf_path, 'rb') as fh:
#         # iterate over all pages of PDF document
#         for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
#             # creating a resoure manager
#             pdf_resource_manager = PDFResourceManager()
            
#             # create a file handle
#             my_fake_file_handle = io.StringIO()
            
#             # creating a text converter object
#             text_converter = TextConverter(
#                                 pdf_resource_manager, 
#                                 my_fake_file_handle, 
#                                 codec='utf-8', 
#                                 laparams=LAParams()
#                         )
#             # creating a page interpreter
#             page_interpreter = PDFPageInterpreter(
#                                 pdf_resource_manager, 
#                                 text_converter
#                             )

#             # process current page
#             page_interpreter.process_page(page)
            
#             # extract text
#             text = my_fake_file_handle.getvalue()
#             yield text

#             # close open handles
#             text_converter.close()
#             my_fake_file_handle.close()