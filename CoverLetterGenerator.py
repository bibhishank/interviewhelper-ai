from Utils import getGeminProModel

#---------------------------------------------------------------------------------------------
#Generate cover letter calling Gemini Pro  
#def generateCoverLetter(resume_text, skills, job_title, industry, jd, company, letter_length, experience_years):
def generateCoverLetter(resume_text, job_title, jd, company):  
   #generateCoverLetter(resume_text, job_title, jd, company)
  resume_skills_experience_prompt = ""
  company_prompt = ""
  #experience_years_prompt = ""
  if resume_text is not None and len(resume_text) > 0:
     #global resume_skills_experience_prompt 
     resume_skills_experience_prompt = f"Candidate details, professional experience, skills are available in resume here:  \"{resume_text}\"  "
#   if skills is not None and len(skills) > 0:
#      resume_skills_experience_prompt = f"Skills are \"{skills}\". "
  if company is not None and len(company) > 0:
     company_prompt = f" Cover letter is for a company \"{company}\". "
#   if experience_years is not None and experience_years > 0:
#      experience_years_prompt = f"Total experience is {experience_years} years."

  #print(f"resume_skills_experience_prompt {resume_skills_experience_prompt}, \n job_title  {job_title}, \n industry {industry}, \n jd {jd}, \n company_prompt {company_prompt} , \n letter_length = {letter_length}, \n experience_years_prompt = {experience_years_prompt} ")
 #Write a conversational, more than {letter_length} words cover letter for a \"{job_title}\" role in the \"{industry}\" industry. 
  prompt_parts = [
    f""" Role: Job application cover letter writer
      Topic: Job interview
      Style: Casual, respectful, not too enthusiastic or flowery.

      Steps: 
      Gather company information.
      Review Resume.
      Analyze Job Description and gather company information and influence cover letter with that information.
      
      With all these infomation,  Write a conversational, more than 500 words cover letter for a \"{job_title}\" role.
      
      Cover Letter should not be less than 300 charaters.

    {company_prompt}
    {resume_skills_experience_prompt}
    Candidate Job description: \"{jd}\" 
    Complete the last sentence. 
    """
  ]
  
  model = getGeminProModel()

  responses = model.generate_content(prompt_parts, stream=True)
  response_stream = ""
  for response in responses:
    #print(response.text)
    response_stream += response.text

  #print(response_stream)
  return response_stream
#---------------------------------------------------------------------------------------------