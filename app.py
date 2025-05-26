import streamlit as st
from database import init_db, insert_prompt, fetch_images, connect_db
from generator import generate_image
from evaluation import evaluate_image
import os
import pandas as pd

# Initialize the database
init_db()

# Connect to the database
connection = connect_db()

# Streamlit page setup
st.set_page_config(page_title="Stable Diffusion Generator", layout="centered")
st.title("\U0001F3A8 Text-to-Image Generator")

# User input for prompt and style
prompt = st.text_input("Enter a prompt")

styles = [
    "realistic",
    "cyberpunk",
    "cartoon",
    "oil painting",
    "pixel art",
    "animation",
    "Geometric & Fractal Art",
    "Architectural",
    "Traditional",
    "Abstract",
    "Modern & Digital",
    "Fantasy & Sci-Fi",
    "Cartoon & Comics"
]

style = st.selectbox("Choose a style", styles)

evaluation_reports = []  # List to store evaluation reports

if st.button("Generate Image"):
    image_path = generate_image(prompt, style)
    
    if image_path:  
        # Insert prompt and image path into the database
        insert_prompt(connection, prompt, style, image_path)

        # Evaluate the generated image against the prompt
        evaluation_result = evaluate_image(image_path, prompt)

        # Store the evaluation report
        evaluation_reports.append({
            "Prompt": prompt,
            "Image Path": image_path,
            "Evaluation": evaluation_result
        })

        # Display the evaluation result
        st.subheader("Evaluation Result")
        st.image(image_path, use_container_width=True)
        st.write(f"**Prompt:** {prompt}")
        st.write(f"**Evaluation:** {evaluation_result}")

    else:
        st.write("Image generation failed.")

# Display the image gallery
st.subheader("Generated Images")
images = fetch_images(connection)  
if images:
    for entry in images:
        prompt, image_path = entry
        if os.path.exists(image_path):
            col1, col2 = st.columns([1, 2])  # Create two columns
            with col1:
                st.image(image_path, use_container_width=True)  # Display the image
            with col2:
                st.write(f"**Prompt:** {prompt}")  # Display the prompt below the image
        else:
            st.warning(f"Image not found for prompt: {prompt}")
else:
    st.info("No images generated yet.")

# Display evaluation reports
st.subheader("Evaluation Reports")
if evaluation_reports:
    for report in evaluation_reports:
        st.image(report["Image Path"], use_container_width=True)
        st.write(f"**Prompt:** {report['Prompt']}")
        st.write(f"**Evaluation:** {report['Evaluation']}")
else:
    st.info("No evaluation reports available.")

# Download button for the report
if st.button("Download Evaluation Report"):
    df = pd.DataFrame(evaluation_reports)
    report_file = "evaluation_report.csv"
    df.to_csv(report_file, index=False)
    st.download_button(
        label="Download Report",
        data=open(report_file, 'rb'),
        file_name=report_file,
        mime='text/csv'
    )

# Display prompt history
st.subheader("Prompt History")
if images:
    for entry in images:
        prompt, _ = entry
        st.write(f"- {prompt}")
else:
    st.info("No prompt history available.")

# Close the database connection
connection.close()