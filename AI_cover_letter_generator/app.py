import os
import json
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv
import io 
import pdfplumber
import docx 

load_dotenv()

app = Flask(__name__)

# Configure the Generative AI API
try:
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables.")
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-1.5-flash-latest') # Or 'gemini-pro'
except Exception as e:
    print(f"Error configuring GenAI: {e}")
    model = None

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'json', 'docx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_data_from_file(uploaded_file):
    """
    Extracts content from uploaded file.
    Returns a dictionary if JSON, otherwise a string of text.
    """
    if not uploaded_file or not uploaded_file.filename:
        return None, "No file provided or file has no name."

    filename = uploaded_file.filename
    if not allowed_file(filename):
        return None, f"File type not allowed. Please use {', '.join(ALLOWED_EXTENSIONS)}."

    file_ext = filename.rsplit('.', 1)[1].lower()
    
    try:
        # Use uploaded_file.stream for libraries that expect a file-like object
        # For libraries that might close the stream, or for multiple reads, copy to BytesIO
        file_stream = io.BytesIO(uploaded_file.read()) # Read once into memory
        uploaded_file.close() # Ensure original stream is closed if not managed by Flask

        if file_ext == 'json':
            try:
                # Reset stream position if it was read into BytesIO
                file_stream.seek(0)
                data = json.load(file_stream)
                return data, None
            except json.JSONDecodeError:
                return None, "Invalid JSON content."
        
        elif file_ext == 'txt':
            file_stream.seek(0)
            return file_stream.read().decode('utf-8', errors='ignore'), None
        
        elif file_ext == 'pdf':
            text_content = ""
            # pdfplumber works directly with file paths or file-like objects
            # To avoid saving the file, we pass the BytesIO stream
            file_stream.seek(0)
            with pdfplumber.open(file_stream) as pdf:
                for page in pdf.pages:
                    text_content += page.extract_text() + "\n"
            return text_content, None
            
        elif file_ext == 'docx':
            text_content = ""
            file_stream.seek(0)
            document = docx.Document(file_stream)
            for para in document.paragraphs:
                text_content += para.text + "\n"
            return text_content, None
            
    except Exception as e:
        print(f"Error processing file {filename}: {e}")
        return None, f"Could not process file {filename}. Error: {str(e)}"
    
    return None, "Unsupported file type or error during processing."


def generate_cover_letter_prompt_structured(resume_data, job_desc_data):
    """
    Prompt for structured (JSON/dict) resume and job description.
    """
    prompt = f"""
    You are a professional career advisor and expert cover letter writer.
    Your task is to generate a compelling, highly customized, and professional cover letter.

    Candidate's Resume Details (from structured data):
    ---------------------------
    Name: {resume_data.get('name', 'The Candidate')}
    Experience: {resume_data.get('experience', 'N/A')}
    Skills: {', '.join(resume_data.get('skills', []))}
    Projects: {'; '.join(resume_data.get('projects', []))}
    Contact: {resume_data.get('contact', 'N/A')} 
    Education: {resume_data.get('education', 'N/A')}
    ---------------------------

    Job Description Details (from structured data):
    ------------------------
    Job Title: {job_desc_data.get('title', 'the advertised position')}
    Company: {job_desc_data.get('company', 'your esteemed company')}
    Key Requirements: {', '.join(job_desc_data.get('requirements', []))}
    Key Responsibilities: {'; '.join(job_desc_data.get('responsibilities', []))}
    About Company: {job_desc_data.get('about_company', '')}
    ------------------------

    Instructions for the Cover Letter:
    1.  Start with a professional salutation (e.g., "Dear Hiring Manager," or "Dear [Company Name] Recruiting Team,").
    2.  Clearly state the position being applied for: "{job_desc_data.get('title', 'the advertised position')}" at "{job_desc_data.get('company', 'your company')}".
    3.  **Crucially, analyze the candidate's resume and the job description. Highlight 2-3 specific skills, experiences, or projects from the resume that directly and strongly align with the key requirements and responsibilities of the job. Provide brief, concrete examples or elaborate slightly on how these are relevant.** Do not just list skills; explain their relevance and impact.
    4.  If 'About Company' or other company details are provided, try to weave in a sentence showing genuine interest in the company's mission, values, or recent work, if it aligns with the candidate's profile.
    5.  Express genuine enthusiasm for the role and the company.
    6.  Maintain a confident, professional, and proactive tone throughout the letter.
    7.  Keep the letter concise and impactful, ideally 3-4 paragraphs.
    8.  End with a strong closing statement, expressing eagerness for an interview and reiterating interest.
    9.  Sign off with "Sincerely," followed by the candidate's name: "{resume_data.get('name', 'The Candidate')}".

    Generate the cover letter now.
    """
    return prompt

def generate_cover_letter_prompt_unstructured(resume_text, job_desc_text):
    """
    Prompt for unstructured (raw text) resume and job description.
    The LLM will need to parse these texts first.
    """
    prompt = f"""
    You are a professional career advisor and expert cover letter writer.
    Your task is to analyze the provided raw text of a resume and a job description, extract the key information, and then generate a compelling, highly customized, and professional cover letter.

    Candidate's Resume (raw text):
    ---------------------------
    {resume_text}
    ---------------------------

    Job Description (raw text):
    ------------------------
    {job_desc_text}
    ------------------------

    Analysis and Extraction Task (Internal Step for you, the AI):
    1.  From the Resume Text: Identify and extract the candidate's name, a summary of their key experience, relevant skills (especially technical ones), and notable projects or achievements. Also look for contact information or education if available.
    2.  From the Job Description Text: Identify and extract the job title, company name, key requirements (skills, experience levels), and primary responsibilities. Also look for any information about the company.

    Cover Letter Generation Instructions (Based on your analysis):
    1.  Using the extracted information, start with a professional salutation (e.g., "Dear Hiring Manager," or "Dear [Extracted Company Name] Recruiting Team,").
    2.  Clearly state the position being applied for (e.g., "[Extracted Job Title]" at "[Extracted Company Name]").
    3.  **Crucially, based on your analysis, highlight 2-3 specific skills, experiences, or projects from the extracted resume information that directly and strongly align with the extracted key requirements and responsibilities of the job. Provide brief, concrete examples or elaborate slightly on how these are relevant.** Do not just list skills; explain their relevance and impact.
    4.  If you extracted any information about the company, try to weave in a sentence showing genuine interest in the company's mission, values, or recent work, if it aligns with the candidate's profile.
    5.  Express genuine enthusiasm for the role and the company.
    6.  Maintain a confident, professional, and proactive tone throughout the letter.
    7.  Keep the letter concise and impactful, ideally 3-4 paragraphs.
    8.  End with a strong closing statement, expressing eagerness for an interview and reiterating interest.
    9.  Sign off with "Sincerely," followed by the extracted candidate's name. If the name cannot be reliably extracted, use "The Applicant".

    Generate the cover letter now based on your analysis of the provided texts.
    """
    return prompt

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html') # No more default data

@app.route('/generate', methods=['POST'])
def generate():
    if not model:
        return jsonify({"error": "Generative AI model not configured. Please check API key."}), 500

    if 'resume' not in request.files or 'job_description' not in request.files:
        return jsonify({"error": "Both resume and job description files are required."}), 400

    resume_file = request.files['resume']
    job_file = request.files['job_description']

    if resume_file.filename == '' or job_file.filename == '':
        return jsonify({"error": "No selected file or empty filename."}), 400

    resume_data, error_resume = extract_data_from_file(resume_file)
    if error_resume:
        return jsonify({"error": f"Resume processing error: {error_resume}"}), 400

    job_data, error_job = extract_data_from_file(job_file)
    if error_job:
        return jsonify({"error": f"Job description processing error: {error_job}"}), 400

    prompt = ""
    is_structured_input = isinstance(resume_data, dict) and isinstance(job_data, dict)

    if is_structured_input:
        prompt = generate_cover_letter_prompt_structured(resume_data, job_data)
        print("\n--- USING STRUCTURED PROMPT ---")
    else:
        # If one is dict, convert to string for unstructured prompt
        resume_text_for_prompt = json.dumps(resume_data, indent=2) if isinstance(resume_data, dict) else str(resume_data)
        job_text_for_prompt = json.dumps(job_data, indent=2) if isinstance(job_data, dict) else str(job_data)
        prompt = generate_cover_letter_prompt_unstructured(resume_text_for_prompt, job_text_for_prompt)
        print("\n--- USING UNSTRUCTURED PROMPT ---")

    print("\n--- PROMPT SENT TO GENAI (First 500 chars) ---")
    print(prompt[:500] + "...")
    print("----------------------------------------------\n")

    try:
        response = model.generate_content(prompt)
        generated_text = ""
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            generated_text = response.candidates[0].content.parts[0].text
        else:
            # Try to get text from prompt_feedback if generation failed due to safety or other reasons
            if response.prompt_feedback and response.prompt_feedback.block_reason:
                 generated_text = f"Error: Generation blocked. Reason: {response.prompt_feedback.block_reason_message or response.prompt_feedback.block_reason}"
            else:
                generated_text = "Error: Could not retrieve text from GenAI response. The response might be empty or malformed."
            print(f"Unexpected GenAI response structure or issue: {response}")
        
        print("\n--- RESPONSE FROM GENAI (First 500 chars) ---")
        print(generated_text[:500] + "...")
        print("---------------------------------------------\n")

        return jsonify({"cover_letter": generated_text})

    except Exception as e:
        print(f"Error during GenAI call: {e}")
        return jsonify({"error": f"An error occurred with the AI model: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
