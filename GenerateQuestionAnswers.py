from Utils import getGeminProModel



#---------------------------------------------------------------------------------------------
#Generate cover letter calling Gemini Pro  
def generateQuestionAnswers(resume_text, qa_jd):
    prompt_parts = [ f"""
    Generate a set of interview questions and ideal answers for a job position based on the provided Job Description and the candidate's Resume. 
    The Job Description emphasizes key skills, responsibilities, and qualifications. 
    The candidate's Resume indicates proficiency in specific skills, experiences, and achievements.
    Job Description: \"{qa_jd}\"
    Candidate's Resume:\"{resume_text}\"
    For each question, provide an ideal answer that showcases the candidate's suitability for the mentioned position, considering both the requirements in the Job Description and the candidate's background as outlined in the Resume.
    Provide at least 10 questions and detailed ideal answer.
    """
    ]

    model = getGeminProModel()
    responses = model.generate_content(prompt_parts, stream=True)
    response_stream = ""
    for response in responses:
        response_stream += response.text
    return response_stream
#---------------------------------------------------------------------------------------------

