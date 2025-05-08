from flask import Flask, request, jsonify, send_file, render_template
from gtts import gTTS
from langdetect import detect
import pandas as pd
import io
from rapidfuzz import process, fuzz   # <<< ADD THIS

app = Flask(__name__)

# Load datasets
english_df = pd.read_csv('C://Users//SHUDESH//Documents//Questions_answers.csv')
tamil_df = pd.read_csv('C://Users//SHUDESH//Documents//tamil.csv')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-answer', methods=['POST'])
def get_answer():
    data = request.get_json()
    question = data.get('question')
    detected_lang = detect(question)

    # Find answer
    answer = find_answer(question, detected_lang)

    if answer:
        return jsonify({'answer': answer, 'language': detected_lang})
    else:
        return jsonify({'answer': "Sorry, I couldn't find the answer.", 'language': detected_lang})

def find_answer(question, detected_lang):
    if detected_lang == 'en':
        questions_list = english_df['Question'].tolist()
        best_match = process.extractOne(question, questions_list, scorer=fuzz.token_sort_ratio)
        if best_match and best_match[1] > 60:  # Only accept match if similarity > 60%
            matched_question = best_match[0]
            answer_row = english_df[english_df['Question'] == matched_question]
            if not answer_row.empty:
                return answer_row.iloc[0]['Answer']
    elif detected_lang == 'ta':
        tamil_questions_list = tamil_df['கேள்வி'].tolist()
        best_match = process.extractOne(question, tamil_questions_list, scorer=fuzz.token_sort_ratio)
        if best_match and best_match[1] > 60:
            matched_question = best_match[0]
            answer_row = tamil_df[tamil_df['கேள்வி'] == matched_question]
            if not answer_row.empty:
                return answer_row.iloc[0]['பதில்']
    return None

@app.route('/speak', methods=['POST'])
def speak():
    data = request.get_json()
    text = data.get('text')
    language = data.get('language')

    lang_code = 'en' if language == 'en' else 'ta'

    # Generate audio in memory (not saved to file!)
    tts = gTTS(text=text, lang=lang_code)
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)

    return send_file(mp3_fp, mimetype="audio/mpeg")

if __name__ == '__main__':
    app.run(debug=True)
