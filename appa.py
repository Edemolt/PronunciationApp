import streamlit as st
import streamlit.components.v1 as components
import nltk
from nltk.corpus import cmudict
import os
import json
import pandas as pd
import speech_recognition as sr
from pydub import AudioSegment
from difflib import SequenceMatcher
import base64
import re

# Download CMU Dict if not present
try:
    nltk.data.find('corpora/cmudict')
except LookupError:
    nltk.download('cmudict')

class PronunciationTrainer:
    def __init__(self, csv_path, progress_file='progress.json'):
        self.data = pd.read_csv(csv_path)
        
        # Normalize column names
        self.data.columns = self.data.columns.str.strip().str.lower().str.replace(' ', '_')
        print("Available columns:", self.data.columns.tolist())
        
        self.progress_file = progress_file
        self.recognizer = sr.Recognizer()
        self.pronunciation_dict = cmudict.dict()
        self.load_progress()

    def load_progress(self):
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r') as f:
                self.progress = json.load(f)
        else:
            self.progress = {}

    def save_progress(self):
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f)

    def get_phonetic(self, word):
        clean = word.lower().strip('.,:;!?')
        try:
            return ' '.join(self.pronunciation_dict[clean][0])
        except KeyError:
            return "Pronunciation not available"

    def get_word_timings(self, index):
        return self.data.iloc[index]['word_timings']

    def analyze_pronunciation(self, original, attempt):
        if not attempt:
            return 0.0, {}, 0, 0, 0
        
        original = re.sub(r'[^a-zA-Z\s]', '', original)
        attempt = re.sub(r'[^a-zA-Z\s]', '', attempt)
        
        original_words = original.lower().split()
        attempt_words = attempt.lower().split()
        
        matcher = SequenceMatcher(None, original_words, attempt_words)
        metrics = {
            'correct': 0,
            'mispronounced': 0,
            'missed': 0,
            'extra': 0
        }
        
        aligned_feedback = []
        total_words = len(original_words)
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                metrics['correct'] += (i2 - i1)
                for word in original_words[i1:i2]:
                    aligned_feedback.append(('correct', word))
            elif tag == 'replace':
                metrics['mispronounced'] += (i2 - i1)
                for orig, att in zip(original_words[i1:i2], attempt_words[j1:j2]):
                    aligned_feedback.append(('mispronounced', orig, att))
            elif tag == 'insert':
                metrics['extra'] += (j2 - j1)
                for word in attempt_words[j1:j2]:
                    aligned_feedback.append(('extra', word))
            elif tag == 'delete':
                metrics['missed'] += (i2 - i1)
                for word in original_words[i1:i2]:
                    aligned_feedback.append(('missed', word))

        accuracy = (metrics['correct'] / total_words) * 100 if total_words > 0 else 0
        return accuracy, metrics, aligned_feedback, original_words, attempt_words

def main():
    st.title("Pronunciation Trainer")
    
    if 'trainer' not in st.session_state:
        if os.path.exists('timed_data.csv'):
            st.session_state.trainer = PronunciationTrainer('timed_data.csv')
        else:
            st.error("timed_data.csv file not found!")
            return

    menu = st.sidebar.selectbox("Menu", ["Practice", "Progress"])
    
    if menu == "Practice":
        st.header("Practice Pronunciation")
        sentences = st.session_state.trainer.data['sentence'].tolist()
        selected_idx = st.selectbox("Select Sentence", range(len(sentences)), format_func=lambda x: sentences[x])
        
        if selected_idx is not None:
            sentence = sentences[selected_idx]
            audio_path = st.session_state.trainer.data.iloc[selected_idx]['wav_file']
            json_path = st.session_state.trainer.data.iloc[selected_idx]['json_file']
            
            st.subheader("Original Sentence")
            st.write(sentence)
            
            if st.button("Play Reference Audio"):
                try:
                    # Load the audio from the wav file
                    audio = AudioSegment.from_wav(audio_path)
                    
                    # Load the JSON timing data
                    with open(json_path, 'r') as f:
                        timing_data = json.load(f)
                    
                    # Process word timings based on timing_data from JSON file
                    valid_words = []
                    for word_info in timing_data.get("words", []):
                        word_text = word_info.get("word", "")
                        start_time = word_info.get("start", 0)
                        end_time = word_info.get("end", 0)
                        if word_text:
                            valid_words.append({
                                "word": word_text,
                                "start": start_time,
                                "end": end_time
                            })

                    # Convert audio to base64 for embedding in HTML
                    audio_bytes = audio.export(format='wav').read()
                    b64_audio = base64.b64encode(audio_bytes).decode('utf-8')
                    audio_uri = f"data:audio/wav;base64,{b64_audio}"

                    # Build the transcript HTML with spans for each word
                    words_html = " ".join([
                        f'<span class="word" data-start="{wt["start"]:.2f}" data-end="{wt["end"]:.2f}">{wt["word"]}</span>'
                        for wt in valid_words
                    ])

                    # Build the complete HTML code
                    html = f"""
                    <html>
                    <head>
                        <style>
                            .word {{
                                transition: all 0.3s;
                                margin-right: 8px;
                                display: inline-block;
                                padding: 2px 5px;
                            }}
                            .highlight {{
                                background: #ff0000; /* Bright red */
                                color: white;
                                font-weight: bold;
                                border-radius: 4px;
                            }}
                        </style>
                    </head>
                    <body>
                        <audio id="audioPlayer" controls style="width: 100%;">
                            <source src="{audio_uri}" type="audio/wav">
                        </audio>
                        <div id="wordDisplay" style="margin: 20px 0; font-size: 24px; line-height: 2.5;">
                            {words_html}
                        </div>
                        <script>
                            const audio = document.getElementById('audioPlayer');
                            const words = document.querySelectorAll('.word');
                            
                            // Update highlighting whenever the audio time updates
                            audio.addEventListener('timeupdate', function() {{
                                const currentTime = audio.currentTime;
                                words.forEach(word => {{
                                    const start = parseFloat(word.dataset.start);
                                    const end = parseFloat(word.dataset.end);
                                    if (currentTime >= start && currentTime < end) {{
                                        word.classList.add('highlight');
                                    }} else {{
                                        word.classList.remove('highlight');
                                    }}
                                }});
                            }});
                        </script>
                    </body>
                    </html>
                    """
                    # Use components.html to embed the HTML with a set height
                    components.html(html, height=300)
                    
                except Exception as e:
                    st.error(f"Error playing audio: {str(e)}")
            
            if st.button("Start Recording"):
                with sr.Microphone() as source:
                    st.write("Recording... Speak now!")
                    audio_recorded = st.session_state.trainer.recognizer.listen(source)
                    
                    try:
                        user_text = st.session_state.trainer.recognizer.recognize_google(audio_recorded)
                        accuracy, metrics, feedback, original_words, attempt_words = st.session_state.trainer.analyze_pronunciation(sentence, user_text)
                        
                        st.subheader("Analysis Results")
                        st.write(f"Your attempt: {user_text}")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("Accuracy", f"{accuracy:.1f}%")
                        col2.metric("Correct Words", metrics['correct'])
                        col3.metric("Mispronounced", metrics['mispronounced'])
                        col4.metric("Missed Words", metrics['missed'])
                        
                        st.subheader("Word-by-word Feedback")
                        cols = st.columns(5)
                        col_idx = 0
                        for item in feedback:
                            if item[0] == 'correct':
                                cols[col_idx].success(f"{item[1]}")
                            elif item[0] == 'mispronounced':
                                cols[col_idx].error(f"{item[2]} → {item[1]}")
                            elif item[0] == 'missed':
                                cols[col_idx].warning(f"[Missing: {item[1]}]")
                            elif item[0] == 'extra':
                                cols[col_idx].info(f"[Extra: {item[1]}]")
                            
                            col_idx = (col_idx + 1) % 5
                        
                        st.subheader("Phonetic Guidance")
                        for word in original_words:
                            phonetic = st.session_state.trainer.get_phonetic(word)
                            st.write(f"**{word}**: /{phonetic}/")
                        
                    except sr.UnknownValueError:
                        st.error("Could not understand audio")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    elif menu == "Progress":
        st.header("Learning Progress")
        if st.session_state.trainer.progress:
            for idx, record in st.session_state.trainer.progress.items():
                with st.expander(f"Sentence {int(idx)+1} - {record['date']}"):
                    st.write(f"Score: {record['score']*100:.1f}%")
                    st.write(f"Original: {record['original']}")
                    st.write(f"Attempt: {record['attempt']}")
        else:
            st.write("No progress recorded yet")

if __name__ == "__main__":
    main()
