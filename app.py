import os
from flask import Flask, render_template, request, jsonify,url_for
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv
import openai
import requests
from gtts import gTTS
import asyncio
import string
import random
import speech_recognition as sr
from pydub import AudioSegment
import soundfile



#load the api keys from the the .env file
load_dotenv()
#
hugging_face = "<YOUR_HUGGING_FACE_API_KEY>"
open_ai_key = "<YOUR_OPENAI_API_KEY>"
#
openai.api_key = open_ai_key

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'wav'}


def get_answer_openai(question):
    completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages = [{"role": "system", "content" : "I want you to act like d&d dungeon master (but do not refer to yourself as such), but you're actually running a SOC2 cybersecurity tabletop exercise. Try to make your responses relatively brief."},
                            {"role": "user", "content" : "Generate a basic cybersecurity breach scenario for a tabletop exercise"},
                            {"role":"system","content":"The company uses Microsoft Defender for their endpoint security, and Rapid7 for incident monitoring."},
                            {"role":"user","content":question}
                ]
            )
    
    return completion['choices'][0]['message']['content']


###





def text_to_audio(text,filename):

    '''
    tts = gTTS(text)
    tts.save(f'static/audio/{filename}.mp3')
    '''

    CHUNK_SIZE = 1024
    url = "https://api.elevenlabs.io/v1/text-to-speech/EXAVITQu4vr4xnSDxMaL"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": "<YOUR_ELEVEN_LABS_API_KEY>"
    }

    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    response = requests.post(url, json=data, headers=headers)
    with open('static/audio/' + filename + '.mp3', 'wb') as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)
    



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    if 'audio' in request.files:
        audio = request.files['audio']
        if audio and allowed_file(audio.filename):
            filename = secure_filename(audio.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            audio.save(filepath)
            transcription = process_audio(filepath)
            return jsonify({'text': transcription})

    text = request.form.get('text')
    if text:
        response = process_text(text)
        return {'text': response['text'],'voice': url_for('static', filename='audio/' + response['voice'])}

    return jsonify({'text': 'Invalid request'})

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def process_audio(filepath):
    # Placeholder function for processing audio (speech-to-text transcription)
    # Replace this with your own implementation using libraries like SpeechRecognition or DeepSpeech
    #return 'hello This is a placeholder transcription for audio'
    '''API_URL = "https://api-inference.huggingface.co/models/jonatasgrosman/wav2vec2-large-xlsr-53-english"
    headers = {"Authorization": hugging_face}
    with open(filepath, "rb") as f:
        data = f.read()
    response = requests.post(API_URL, headers=headers, data=data)
    data = response.json()
    return data['text']
    '''
    newfile = (filepath + ".wav")
    data, samplerate = soundfile.read(filepath)
    soundfile.write(newfile, data, samplerate, subtype='PCM_16')

    # Initialize the recognizer
    r = sr.Recognizer()
    r.energy_threshold = 300

    audio = sr.AudioFile(newfile)
    with audio as source:
        audio = r.record(source)
        type(audio)             
        result = r.recognize_google(audio)
    return result
 


def process_text(text):
    # Placeholder function for processing user's text input
    # Replace this with your own implementation
    return_text = get_answer_openai(text)
    #asyncio.run(text_to_audio(return_text))
    # generating random strings
    res = ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k=8))
    text_to_audio(return_text,res)
    return {"text":return_text,"voice": f"{res}.mp3"}


if __name__ == '__main__':
    app.run(debug=True)

