
# AI cover letter generator

### Overview
The application allows users to upload their resumes and job descriptions to generate tailored cover letters using a generative AI model. The workflow encompasses file upload, data extraction, prompt generation, and AI response handling.

### Workflow Steps

1. **User Interface**
   - **Frontend**: The user accesses the application via a web interface (`index.html`), where they can upload their resume and job description files.

2. **File Upload**
   - Users select files (resume and job description) and submit the form.
   - The request is sent to the backend for processing.

3. **File Handling**
   - The Flask app receives the uploaded files in the `/generate` route.
   - **Technology Used**: Flask for backend handling, HTML/CSS for frontend.

4. **Data Extraction**
   - The application checks the file types and processes the files accordingly:
     - **JSON**: Loaded directly as a dictionary.
     - **TXT**: Read as plain text.
     - **PDF**: Extracted text using `pdfplumber`.
     - **DOCX**: Extracted text using `python-docx`.
   - **Technology Used**: Libraries like `pdfplumber` and `python-docx` facilitate content extraction.

5. **Data Validation**
   - The application ensures both files are provided and are of allowed types.
   - Returns error messages for invalid inputs.

6. **Prompt Generation**
   - The application checks if the extracted data is structured (i.e., dictionaries) or unstructured (raw text).
   - It generates a prompt for the Generative AI model based on the input type:
     - **Structured Input**: Uses a detailed prompt that incorporates specific fields from the resume and job description.
     - **Unstructured Input**: Creates a prompt that instructs the AI to analyze the raw text.
   - **Technology Used**: Python for string manipulation and prompt creation.

7. **AI Model Interaction**
   - The application interacts with the Generative AI API (Gemini) to generate a cover letter based on the prompt.
   - Handles API responses, checking for errors or content generation issues.
   - **Technology Used**: Google Generative AI API for natural language processing.

8. **Response Handling**
   - The application processes the AI's response:
     - If successful, it returns the generated cover letter to the frontend.
     - If there’s an error, it returns an appropriate error message.
   - **Technology Used**: JSON for structured data exchange between client and server.

9. **Display Output**
   - The generated cover letter is displayed on the frontend for the user to review and download if desired.

### Data Flow

1. **Input Data**:
   - **User Input**: Resume and job description files are uploaded.
   - **File Types**: Supported types include JSON, TXT, PDF, and DOCX.

2. **Processing**:
   - **Data Extraction**: Content is extracted according to file type.
   - **Data Validation**: Ensures both files are present and valid.
   - **Prompt Creation**: Constructs a prompt for the AI based on extracted data.

3. **AI Interaction**:
   - **Prompt Sent**: The generated prompt is sent to the Generative AI model.
   - **Response Received**: The AI returns a cover letter or an error message.

4. **Output Data**:
   - **Generated Cover Letter**: Returned to the user interface for display.
   - **Error Messages**: If any errors occur, appropriate messages are displayed to the user.

### Technology Stack
- **Frontend**: HTML, CSS, JavaScript (for interactivity).
- **Backend**: Flask (Python web framework).
- **File Processing**: 
  - `pdfplumber` for PDF extraction.
  - `python-docx` for DOCX extraction.
- **Environment Variables**: `dotenv` for managing API keys securely.
- **Generative AI Model**: Google Generative AI API (Gemini).
- **Data Format**: JSON for data exchange between the server and client.

### Conclusion
This workflow efficiently integrates user inputs, file processing, AI interaction, and output generation, providing a seamless experience for generating customized cover letters.
