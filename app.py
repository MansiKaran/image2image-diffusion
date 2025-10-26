from flask import Flask, request, jsonify
from diffusion_service import diffusion_service
import os
from google.auth.transport import requests
from google.oauth2 import id_token

app = Flask(__name__)

# OAuth2 configuration
CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '475710976485-your-client-id.apps.googleusercontent.com')

def require_oauth2(f):
    """Decorator to require OAuth2 authentication"""
    def decorated_function(*args, **kwargs):
        # Get the Authorization header (case insensitive)
        auth_header = request.headers.get('Authorization') or request.headers.get('authorization')
        if not auth_header:
            return jsonify({'error': 'Missing Authorization header', 'headers': dict(request.headers)}), 401
        if not auth_header.lower().startswith('bearer '):
            return jsonify({'error': 'Invalid Authorization header format', 'header': auth_header}), 401
        
        # Extract the token
        token = auth_header.split(' ')[1]
        
        try:
            # Verify the Google ID token with Client ID
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
            
            # Check if the token is valid
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            
            # Store user info in request context for later use
            request.user_info = idinfo
            
        except Exception as e:
            # More detailed error logging
            return jsonify({'error': f'Token verification failed: {str(e)}', 'token_preview': token[:50] + '...', 'client_id': CLIENT_ID}), 401
        
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
def hello():
    return jsonify({
        "message": "Image2Image Diffusion Service",
        "status": "running",
        "authentication": "OAuth2 (Google)",
        "endpoints": {
            "generate": "/generate (POST) - Requires Authorization: Bearer <token> header"
        }
    })

@app.route('/generate', methods=['POST'])
@require_oauth2
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
        "random_seed": used_seed,
        "user": getattr(request, 'user_info', {}).get('email', 'unknown')
    })

@app.route('/test-auth', methods=['POST'])
@require_oauth2
def test_auth():
    """Test endpoint to verify OAuth2 authentication"""
    return jsonify({
        "message": "OAuth2 authentication successful!",
        "user": getattr(request, 'user_info', {}).get('email', 'unknown'),
        "user_info": getattr(request, 'user_info', {})
    })

if __name__ == '__main__':
    import os
    # Get port from environment variable (for Google Cloud Run)
    port = int(os.environ.get('PORT', 8080))
    # Default to 8080 for local development
    app.run(host='0.0.0.0', port=port)
