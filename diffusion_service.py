import torch
import base64
import io
from diffusers import StableDiffusionPipeline

class DiffusionService:
    def __init__(self):
        self.pipeline = None
    
    def load_model(self):
        self.pipeline = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
        )
        if torch.cuda.is_available():
            self.pipeline = self.pipeline.to("cuda")
    
    def generate_image(self, prompt):
        result = self.pipeline(
            prompt=prompt,
            num_inference_steps=20,
            guidance_scale=7.5,
            guidance_rescale=1.0
        )
        
        # Convert the generated PIL Image to base64 string for JSON transmission
        image = result.images[0]             # Get the first (and only) generated image
        buffer = io.BytesIO()                # Create an in-memory file buffer
        image.save(buffer, format="JPEG")    # Save the image as JPEG to the buffer
        img_base64 = base64.b64encode(buffer.getvalue()).decode()  # Convert to base64 string
        
        return [img_base64], 42

# Create a global instance of our service
# This means the model stays loaded in memory between requests (faster)
diffusion_service = DiffusionService()
