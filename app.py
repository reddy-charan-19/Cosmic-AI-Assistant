from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import google.generativeai as gen_ai
import requests
from googletrans import Translator

app = Flask(__name__)
CORS(app)

# Configure Gemini-Pro
GOOGLE_API_KEY = "AIzaSyDGwiW9AjSAcc1jERYGPBCXb0sadTSArnU"
gen_ai.configure(api_key=GOOGLE_API_KEY)
model = gen_ai.GenerativeModel('gemini-pro')
chat_session = model.start_chat(history=[])

# Configure Image Generation
HF_API_KEY = "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"
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {HF_API_KEY}"}

# Configure Translation
translator = Translator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_input = data.get('message')
    
    try:
        response = chat_session.send_message(user_input)
        return jsonify({
            "status": "success",
            "response": response.text
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "response": f"Error processing request: {str(e)}"
        })

@app.route('/generate-image', methods=['POST'])
def generate_image():
    data = request.get_json()
    prompt = data.get('prompt')
    
    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
        if response.status_code == 200:
            return response.content, 200, {'Content-Type': 'image/png'}
        return jsonify({"status": "error", "message": response.text}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/translate', methods=['POST'])
def translate_text():
    data = request.get_json()
    text = data.get('text')
    target_lang = data.get('target_lang')
    
    try:
        translation = translator.translate(text, dest=target_lang)
        return jsonify({
            "status": "success",
            "translation": translation.text
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True,port=5000)