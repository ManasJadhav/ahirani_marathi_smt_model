from flask import Flask, request, jsonify
import models.smt_translation as smt_translation;
import configparser
import os

app = Flask(__name__)

config = configparser.ConfigParser()
try:
    config.read('config.ini')
except FileNotFoundError:
    pass

# defining default value if config.ini not found
API_HOST = os.environ.get('API_HOST', '0.0.0.0') 
API_PORT = os.environ.get('API_PORT', 5000)

print(f"API server listening on {API_HOST}:{API_PORT}")

@app.route("/test")
def test():
    return jsonify({'success': True, 'msg': 'Welcome to test route of Translation API'})

@app.route('/translate', methods=['POST'])
def translate():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Missing data in request'}), 400
    
    translated_text = smt_translation.translate(data["ahirani_text"])


    return jsonify({'marathi_text': translated_text})

if __name__ ==  '__main__':
    app.run(debug=True, host=API_HOST, port=API_PORT)