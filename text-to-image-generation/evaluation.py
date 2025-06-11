from sentence_transformers import SentenceTransformer, util
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image

# Load models for evaluation
caption_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
caption_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
similarity_model = SentenceTransformer('all-MiniLM-L6-v2')

def semantic_similarity(prompt, caption):
    emb1 = similarity_model.encode(prompt, convert_to_tensor=True)
    emb2 = similarity_model.encode(caption, convert_to_tensor=True)
    return float(util.pytorch_cos_sim(emb1, emb2)[0][0])

def evaluate_image(image_path, prompt):
    # Load the image
    image = Image.open(image_path)

    # Prepare the image for captioning
    inputs = caption_processor(images=image, return_tensors="pt")

    # Generate the caption
    out = caption_model.generate(**inputs)
    generated_caption = caption_processor.decode(out[0], skip_special_tokens=True)

    # Calculate similarity
    score = semantic_similarity(prompt, generated_caption)
    
    # Provide feedback based on similarity score
    if score > 0.8:
        return "Excellent match with the prompt 80%."
    elif score > 0.5:
        return "Good match, but could be better 50%."
    else:
        return "Poor match with the prompt."
