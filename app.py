from flask import Flask, request, jsonify
from diffusion_service import diffusion_service

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello World!"

@app.route('/generate', methods=['POST'])
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
