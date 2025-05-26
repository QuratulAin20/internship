import requests
import os
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO

load_dotenv()
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")

def generate_image(prompt, style):
    styled_prompt = f"{prompt}, {style} style"
    response = requests.post(
        "https://api.stability.ai/v2beta/stable-image/generate/ultra",
        headers={
            "Authorization": f"Bearer {STABILITY_API_KEY}",
            "Accept": "image/*"
        },
        files={"none": ''},
        data={
            "prompt": styled_prompt,
            "output_format": "webp"
        }
    )
    
    if response.status_code == 200:
        # Convert the response content to an image
        image = Image.open(BytesIO(response.content))

        # Save the image as PNG
        image_filename = f"images/{prompt.replace(' ', '_')}_{style}.png"
        image.save(image_filename, format='PNG')

        return image_filename
    else:
        raise Exception(f"Image generation failed: {response.text}")

# Example usage:
# image_path = generate_image("A serene landscape", "impressionist")
# print(f"Image saved to: {image_path}")