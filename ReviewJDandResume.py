from Utils import getGeminProModel

#---------------------------------------------------------------------------------------------
#Generate cover letter calling Gemini Pro  
def getSkillAndRequirementReview(resume_text, rjr_jd):
  #print(f"resume_skills_experience_prompt {resume_skills_experience_prompt}, \n job_title  {job_title}, \n industry {industry}, \n jd {jd}, \n company_prompt {company_prompt} , \n letter_length = {letter_length}, \n experience_years_prompt = {experience_years_prompt} ")

  prompt_parts = [
    f""" You are an experienced Technical Human Resource Manager,your task is to review the provided resume against the job description.
    Please share your professional evaluation on whether the candidate's profile aligns with the role.
    Resume is \"{resume_text}\""
    Job description is \"{rjr_jd}\" 
    Provide me the percentage of match between the resume and job description.
    List down matching skills.
    List down missing skills. 

    Also provide suggestions for improving resumes to better match specific job opportunities, including recommending additional skills or experiences to highlight.

    """
  ]

  #print("\n\n\n\n\n")
  #print(prompt_parts)
  #return "Wait for the responde"
  model = getGeminProModel()
  responses = model.generate_content(prompt_parts, stream=True)
  response_stream = ""
  for response in responses:
    #print(response.text)
    response_stream += response.text
  return response_stream
#---------------------------------------------------------------------------------------------