from flask import Flask, request, jsonify
from diffusion_service import diffusion_service
import os

app = Flask(__name__)

# API Key for authentication (in production, use environment variables)
API_KEY = os.getenv('API_KEY', 'your-secret-api-key-here')

def require_api_key(f):
    """Decorator to require API key authentication"""
    def decorated_function(*args, **kwargs):
        # Check for API key in headers
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != API_KEY:
            return jsonify({'error': 'Invalid or missing API key'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
def hello():
    return jsonify({
        "message": "Image2Image Diffusion Service",
        "status": "running",
        "endpoints": {
            "generate": "/generate (POST) - Requires X-API-Key header"
        }
    })

@app.route('/generate', methods=['POST'])
@require_api_key
def generate():
    data = request.get_json()
    prompt = data.get('prompt', 'a cat')
    
    # Load model if not already loaded
    if diffusion_service.pipeline is None:
        diffusion_service.load_model()
    
    # Generate image
    images, used_seed = diffusion_service.generate_image(prompt=prompt)
    
    return jsonify({
        "images": images,
        "random_seed": used_seed
    })

if __name__ == '__main__':
    import os
    # Get port from environment variable (for Google Cloud Run)
    port = int(os.environ.get('PORT', 8080))
    # Default to 8080 for local development
    app.run(host='0.0.0.0', port=port)
