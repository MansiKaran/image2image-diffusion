from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello World!"

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    prompt = data.get('prompt', '')
    
    return jsonify({
        'message': f'Received prompt: {prompt}',
        'status': 'success'
    })

if __name__ == '__main__':
    app.run(debug=True, port=8080)
