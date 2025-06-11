# Text-to-Image Generator Web App

This application is a complete pipeline that takes a user's text prompt, generates an image using a
diffusion model, displays it, stores it along with the prompt history, and evaluates how well the image
matches the prompt.

1.Data Flow
User Inputs Prompt + Style Streamlit Frontend Generate Image (Stable Diffusion) Save Image
Locally Insert Record in SQLite DB Display in Gallery
Evaluate with BLIP + SentenceTransformer Show Evaluation Score

2. Components
   
Frontend (Streamlit UI)
- Text input for prompts.
- Dropdown for selecting image style: realistic, cyberpunk, cartoon.
- Button to trigger image generation.
- Section to display:
 - The generated image.
 - Prompt history gallery.
 - Evaluation results

Backend Logic
- Image Generation
- Model: Stable Diffusion Stability AI ("stabilityai/stable-diffusion-3.5-large")
- Library: diffusers, torch
- Execution: Uses torch.float32 and runs on cpu or cuda
- Style is appended to prompt before generation

3. Image Captioning
- Model: Salesforce/blip-image-captioning-base
- Library: transformers, PIL
- Output: Generates textual description of the image.
Semantic Similarity Evaluation
- Model: all-MiniLM-L6-v2 from sentence-transformers
- Computes cosine similarity between the user's prompt and the generated caption.
- Outputs feedback:
 - > 0.8: "Excellent match"
 - > 0.5: "Good match"
 - <= 0.5: "Poor match"
   
4. Data Storage
- Database: SQLite (sqlite3)
- Records:
 - Prompt
 - Style
 - Local image path
 - Timestamp
- Directory: All images are saved to /images/

5. Functionality
- User inputs a text prompt and selects a style.
- Image is generated using Stable Diffusion.
- The image is displayed immediately in the UI.
- Prompt, style, image path, and timestamp are stored in a local SQLite DB.
- Each image is evaluated using BLIP-generated captions and sentence similarity.
- Results are shown in a report: how well the image matches the prompt.
