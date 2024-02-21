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

#---------------------------------------------------------------------------------------------
  
jd_text = """
About the job

Our work at NVIDIA is dedicated towards a computing model passionate about visual and AI computing. For two decades, NVIDIA has pioneered visual computing, the art and science of computer graphics, with our invention of the GPU. The GPU has also proven to be unbelievably effective at solving some of the most sophisticated problems in computer science. Today, NVIDIA’s GPU simulates human intelligence, running deep learning algorithms and acting as the brain of computers, robots and self-driving cars that can perceive and understand the world. Artificial intelligence is no longer science fiction. And in the next few years, it will transform every industry. As the Senior Technical Program Manager, Infrastructure Operations within our global IT PMO team, you will be responsible for leading IT data center infrastructure programs, including data center infrastructure planning and deployment.

What You'll Be Doing

Lead the planning, execution, and monitoring of data center programs. Develop project plans, timelines, and budgets, and ensure adherence to project objectives. Coordinate project resources, lead risks, and resolve issues.
Collaborate with internal teams, external vendors, and business partners to gather requirements, address concerns, and ensure alignment with project objectives. Champion effective communication and lead collaborator expectations throughout the project lifecycle.
Effectively coordinate and lead technical discussions related to infrastructure architecture, solution approach and resource planning.
Lead global cross-functional program team of data center infrastructure design, operation and partner teams to resolve technical or deployment blockers, to keep the programs on-track.
Work with collaborators to create metrics based criteria to drive program success.
Identify learning opportunities for continuous improvements.
Regularly communicate program status and key issues to collaborators and executive management.

What We Need To See

BS/MS or equivalent experience in Engineering or Computer Science or equivalent experience.
8+ years in IT (Information Technology) industry with a focus on data center program/project management.
Proven deep customer and technical savvy born of driving complex programs in IT infrastructure.
Supreme leadership skills across broad and diverse cross-functional teams.
Strong analytical and problem-solving skills.
Experience leading global projects.
Willingness to work with distributed team members across different time zones.

NVIDIA is widely considered to be one of the technology world’s most desirable employers. We have some of the most forward-thinking and hardworking people in the world working for us. If you are creative, results-oriented and enjoy having fun, then what are you waiting for? Apply today!

The base salary range is 180,000 USD - 339,250 USD. Your base salary will be determined based on your location, experience, and the pay of employees in similar positions.

You will also be eligible for equity and benefits .  NVIDIA accepts applications on an ongoing basis. 

NVIDIA is committed to fostering a diverse work environment and proud to be an equal opportunity employer. As we highly value diversity in our current and future employees, we do not discriminate (including in our hiring and promotion practices) on the basis of race, religion, color, national origin, gender, gender expression, sexual orientation, age, marital status, veteran status, disability status or any other characteristic protected by law.

"""


resume_text = """
Bibhishan Karadkar
bibhishan_k@yahoo.com • +1 (408) 931-0588 • San Jose, CA • LinkedIn • website https://bkaradkar.net

Sr. Technical Project Manager

Accomplished Sr. Technical Project Manager with 9+ years experience and additional software engineering
expertise, leveraging tools, partnerships and technology to deliver business value. In total of ~19 years experience,
I demonstrated success identifying new technologies and opportunities to develop solutions that drive revenue,
efficiency, and productivity. Strong reputation for building collaborative relationships with cross-functional teams
(engineering, product, infrastructure, data) across multiple time zones (China, India, U.S.), effectively leading and
executing initiatives.

Individual Technological Accomplishments: Constructed personal profile website
(https://bkaradkar.net) using Streamlit & Python and deployed it on AWS EC2 instance. The website features
projects from my exploration of new technologies, particularly in Generative AI, created with the utilization of
OpenAI, DALL-E , Llama-2, Gemini Pro. New projects will be integrated into the website based on the knowledge
gained.

PROFESSIONAL EXPERIENCE

Zoom Video communication, CA (Sr TPM)

09/2021 – PRESENT
● Managed several end-to-end cross-functional projects for eCommerce marketing online revenue growth.
● Achieved rapid promotion within 1 year due to exceptional performance and impactful contributions
● Recognized with awards like "Dream Team" and "All In One" Award by the GM during All Hands meetings.
● Led 8-10 projects/Qtr & managed big teams of 10-15 engineers addressing all blockers & launch
● Key Initiative 1) Forced Break 40 min for free sequential meeting (Free user monetization)

○ Managed global program to limit users have 1:1 meetings reducing duration & restricted back to

back meetings (Impact : Drove massive revenue growth for Zoom in FY23 ~$2M)

○ Collaborated with 7-8 technical teams and non technical (Product,Finance, revenue, sales, legal,

marketing) leading to successful implementation

○ Led 10-15 Engineers and QA team in the development and launch
○ Led project planning & execution across infrastructure, mobile, desktop, and web
○ Conducted A/B testing for 5 min and 10 min break control variant before 5 weeks of the roll out
○ Partnered w/ data team to integrate analytics and measure via Tableau dashboards.

● Key Initiative 2) Data Science & Engineering (Audience segmentation ~$3M expected revenue)

○ Collaborated 6 product teams & data science to enable data tracking in Snowplow telemetry
○ Led projects with Data Engineering to merge diverse data sources for comprehensive

demographic, behavioral, psychographic, and usage data in Snowflake, processed in Databricks.

○ Engaged in Exploratory Data Analysis (EDA) discussions and Feature Engineering, utilizing the

k-means algorithm with the Elbow method identify # of segments: Champions, Dormant, At Risk.
○ Collaborated with 5 Product Eng teams to share data that will help in enabling targeted customer

engagement through predictive data on web and client platforms.

● Adopted Agile, Scrum and Waterfall approaches using tools like JIRA, Asana MS Project, Custom template
● Led In App Purchase programs for improving checkout of Zoom products on Apple and Android devices
● Managed NPI enablement of Zoom Products for Online customers like Zoom Phone, Home Destination
● Managed project plan for Zoom AI Companion that uses natural language processing (NLP), machine

learning, and voice recognition technology to understand meetings and convert into meeting summaries

● Led project related to cloud recording enforcing limits for online customers (Impact $296K MRR)

partnering with infrastructure teams

● Led projects related to in product growth marketing to increase sign up on Client & Web and Free Sign-Up

Optimizations (Impact 500K MRR) partnering with Marketing & Retention Product Management

● Managed projects related to Mobile & desktop client for showing pre & post meeting dialogues to Online
customers for driving retention promotions for Online marketing increasing free to paid conversions

Zensar Technologies - Client : Cisco Systems

1.

Technical Project Manager
Key Initiatives :
The Multiplier Effect (https://www.multiplydiversity.com/)
Led a cross-functional teams to containerizing and migrating inhouse applications to AWS for the
Multiplier Effect project, managing cost, budget, and AWS account setup. Configured various AWS
components(EC2, VPC, S3, ELB, CloudFront, IAM, RDS, CloudWatch, EKS, ECR) and managed Docker
containers, implementing CI/CD pipelines for deploying images and focusing on containerizing the Drupal
Web App on a PHP+Apache image.
Learning system recommendations for Cisco employees

04/2014 - 09/2021

2.

● Led the System Recommendation project as a Technical Project Manager, overseeing the

implementation of a machine learning engine for personalized learning recommendations based
on diverse attributes.

● Collaborated with global teams, engaged in strategic planning, architecture design, and hands-on
coding, demonstrating proficiency in Python and Big Data tools, and optimized recommendation
accuracy through algorithm adjustments and knowledge of Hadoop, Scoop, Hive, Spark, and Solr.

3.

Learning Management System, Content Management System (TeamSIte) migration to new enterprise
platform.

● Led managed communication and coordination for integrated application teams at Cisco,

developing the next-gen UI for the Enterprise Learning site, configuring the Sales Enablement
Reach Media platform, and contributing to a multilingual mobile app for partners. Key
involvement in enterprise-level application platform migrations.

Software engineer, Senior Technical Lead

03/2004 – 04/2014
● Spearheaded client collaboration, roadmap development, and successful project delivery, with a
focus on enhancing Enterprise Learning Services, facilitating ERP integration for cost savings,
implementing Mobile Transformation, and actively engaging in agile development and continuous
delivery, along with framework enhancements, search engine integrations, and seamless
application integrations using Web Service Gateways.

Employer: ETH/Dishnet DSL, Pune India -

Prior experience and achievements

● As a Java Developer, I utilized multithreading and Socket programming to design a chat server,

incorporating Visual Basic for the user interface on the client side and Java for server-side operations.

● I had the privilege of working with Dr. Vijay Bhatkar, the CEO of Dishnet, and showcasing learning

applications/projects to India's President, Dr. APJ Abdul Kalam.

EDUCATION
Master of Computer Management (MCM) - Savitribai Phule Pune University
Diploma in Computer Management (DCM) - Savitribai Phule Pune University

Certifications / ONLINE TRAININGS
▪
AWS Certified Cloud Practitioner
▪
AWS Certified Solutions Architect – Associate
▪
Certified Scrum Master (SCM)
▪
Introduction to Generative AI
▪
Udemy: Hadoop, Hive, SQOOP, Spark, Solr, Agile Scrum Development for Manager
"""

chat_prompt_template = """
Role: Chat Practice Partner for interview
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

Here is Resume: " 
Bibhishan Karadkar
bibhishan_k@yahoo.com • +1 (408) 931-0588 • San Jose, CA • LinkedIn • website https://bkaradkar.net

Sr. Technical Project Manager

Accomplished Sr. Technical Project Manager with 9+ years experience and additional software engineering
expertise, leveraging tools, partnerships and technology to deliver business value. In total of ~19 years experience,
I demonstrated success identifying new technologies and opportunities to develop solutions that drive revenue,
efficiency, and productivity. Strong reputation for building collaborative relationships with cross-functional teams
(engineering, product, infrastructure, data) across multiple time zones (China, India, U.S.), effectively leading and
executing initiatives.

Individual Technological Accomplishments: Constructed personal profile website
(https://bkaradkar.net) using Streamlit & Python and deployed it on AWS EC2 instance. The website features
projects from my exploration of new technologies, particularly in Generative AI, created with the utilization of
OpenAI, DALL-E , Llama-2, Gemini Pro. New projects will be integrated into the website based on the knowledge
gained.

PROFESSIONAL EXPERIENCE

Zoom Video communication, CA (Sr TPM)

09/2021 – PRESENT
● Managed several end-to-end cross-functional projects for eCommerce marketing online revenue growth.
● Achieved rapid promotion within 1 year due to exceptional performance and impactful contributions
● Recognized with awards like "Dream Team" and "All In One" Award by the GM during All Hands meetings.
● Led 8-10 projects/Qtr & managed big teams of 10-15 engineers addressing all blockers & launch
● Key Initiative 1) Forced Break 40 min for free sequential meeting (Free user monetization)

○ Managed global program to limit users have 1:1 meetings reducing duration & restricted back to

back meetings (Impact : Drove massive revenue growth for Zoom in FY23 ~$2M)

○ Collaborated with 7-8 technical teams and non technical (Product,Finance, revenue, sales, legal,

marketing) leading to successful implementation

○ Led 10-15 Engineers and QA team in the development and launch
○ Led project planning & execution across infrastructure, mobile, desktop, and web
○ Conducted A/B testing for 5 min and 10 min break control variant before 5 weeks of the roll out
○ Partnered w/ data team to integrate analytics and measure via Tableau dashboards.

● Key Initiative 2) Data Science & Engineering (Audience segmentation ~$3M expected revenue)

○ Collaborated 6 product teams & data science to enable data tracking in Snowplow telemetry
○ Led projects with Data Engineering to merge diverse data sources for comprehensive

demographic, behavioral, psychographic, and usage data in Snowflake, processed in Databricks.

○ Engaged in Exploratory Data Analysis (EDA) discussions and Feature Engineering, utilizing the

k-means algorithm with the Elbow method identify # of segments: Champions, Dormant, At Risk.
○ Collaborated with 5 Product Eng teams to share data that will help in enabling targeted customer

engagement through predictive data on web and client platforms.

● Adopted Agile, Scrum and Waterfall approaches using tools like JIRA, Asana MS Project, Custom template
● Led In App Purchase programs for improving checkout of Zoom products on Apple and Android devices
● Managed NPI enablement of Zoom Products for Online customers like Zoom Phone, Home Destination
● Managed project plan for Zoom AI Companion that uses natural language processing (NLP), machine

learning, and voice recognition technology to understand meetings and convert into meeting summaries

● Led project related to cloud recording enforcing limits for online customers (Impact $296K MRR)

partnering with infrastructure teams

● Led projects related to in product growth marketing to increase sign up on Client & Web and Free Sign-Up

Optimizations (Impact 500K MRR) partnering with Marketing & Retention Product Management

● Managed projects related to Mobile & desktop client for showing pre & post meeting dialogues to Online
customers for driving retention promotions for Online marketing increasing free to paid conversions

Zensar Technologies - Client : Cisco Systems

1.

Technical Project Manager
Key Initiatives :
The Multiplier Effect (https://www.multiplydiversity.com/)
Led a cross-functional teams to containerizing and migrating inhouse applications to AWS for the
Multiplier Effect project, managing cost, budget, and AWS account setup. Configured various AWS
components(EC2, VPC, S3, ELB, CloudFront, IAM, RDS, CloudWatch, EKS, ECR) and managed Docker
containers, implementing CI/CD pipelines for deploying images and focusing on containerizing the Drupal
Web App on a PHP+Apache image.
Learning system recommendations for Cisco employees

04/2014 - 09/2021

2.

● Led the System Recommendation project as a Technical Project Manager, overseeing the

implementation of a machine learning engine for personalized learning recommendations based
on diverse attributes.

● Collaborated with global teams, engaged in strategic planning, architecture design, and hands-on
coding, demonstrating proficiency in Python and Big Data tools, and optimized recommendation
accuracy through algorithm adjustments and knowledge of Hadoop, Scoop, Hive, Spark, and Solr.

3.

Learning Management System, Content Management System (TeamSIte) migration to new enterprise
platform.

● Led managed communication and coordination for integrated application teams at Cisco,

developing the next-gen UI for the Enterprise Learning site, configuring the Sales Enablement
Reach Media platform, and contributing to a multilingual mobile app for partners. Key
involvement in enterprise-level application platform migrations.

Software engineer, Senior Technical Lead

03/2004 – 04/2014
● Spearheaded client collaboration, roadmap development, and successful project delivery, with a
focus on enhancing Enterprise Learning Services, facilitating ERP integration for cost savings,
implementing Mobile Transformation, and actively engaging in agile development and continuous
delivery, along with framework enhancements, search engine integrations, and seamless
application integrations using Web Service Gateways.

Employer: ETH/Dishnet DSL, Pune India -

Prior experience and achievements

● As a Java Developer, I utilized multithreading and Socket programming to design a chat server,

incorporating Visual Basic for the user interface on the client side and Java for server-side operations.

● I had the privilege of working with Dr. Vijay Bhatkar, the CEO of Dishnet, and showcasing learning

applications/projects to India's President, Dr. APJ Abdul Kalam.

EDUCATION
Master of Computer Management (MCM) - Savitribai Phule Pune University
Diploma in Computer Management (DCM) - Savitribai Phule Pune University

Certifications / ONLINE TRAININGS
▪
AWS Certified Cloud Practitioner
▪
AWS Certified Solutions Architect – Associate
▪
Certified Scrum Master (SCM)
▪
Introduction to Generative AI
▪
Udemy: Hadoop, Hive, SQOOP, Spark, Solr, Agile Scrum Development for Manager
. " 
"""

#-----------------------------------------------------------------------------------------------------------
# This function create prompt template to get the interview question in text format to be converted in Audio
def getAudio_first_prompt():
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

    Here is Resume: \" {resume_text}. \" 

    Here is Job Description \"{jd_text}. \" 

    """
  return audio_first_prompt_template

def printMessage():
   print("Testing Utils.py")

#printMessage()
