# Pronunciation Training System

An end-to-end system for practicing and analyzing pronunciation with audio-visual feedback.

## Features
- MP3 to WAV conversion
- Audio alignment with Gentle forced aligner
- Interactive pronunciation analysis
- Progress tracking
- Phonetic transcription using CMU Pronouncing Dictionary
- Real-time audio highlighting

## Prerequisites
- Conda/Miniconda
- Docker
- FFmpeg
- Python 3.8+

## Setup Instructions

1. **Create Conda Environment**
```bash
conda create -n pronunciation_trainer python=3.8
conda activate pronunciation_trainer
```

2. **Install Python Dependencies**
```bash
pip install -r requirements.txt
```

3. **Create Required Directories**
```bash
mkdir -p useful_clips data json_files
```

4. **Download NLTK Data**
```bash
python -m nltk.downloader cmudict
```

## requirements.txt
```
streamlit==1.22.0
nltk==3.8.1
pandas==1.5.3
pydub==0.25.1
SpeechRecognition==3.10.0
python-docx==0.8.11
Jinja2==3.1.2
```

## Workflow

1. **Add MP3 files** to `useful_clips` directory
2. **Convert to WAV**:
```bash
python mp3-2-wav.py
```

3. **Process audio alignment** using Gentle:
```bash
docker run -P -p 8765:8765 lowerquality/gentle
```
Upload WAV files and transcripts through the web interface at `http://localhost:8765`

4. **Save JSON outputs** to `json_files` directory

5. **Generate CSV dataset**:
```bash
python add_data.py
```

6. **Launch the application**:
```bash
streamlit run app.py
```

## Key Files
```
├── app.py                 - Main application
├── mp3-2-wav.py           - Audio format converter
├── add_data.py            - Data pipeline
├── requirements.txt       - Dependency list
├── timed_data.csv         - Processed dataset
└── progress.json          - User progress tracking
```

## Usage Notes
1. Ensure microphone access is enabled for recording
2. Speak clearly during recording attempts
3. Review phonetic transcriptions for difficult words
4. Regular practice sessions yield best results

## Clean Up
When finished working:
```bash
conda deactivate
```

## Troubleshooting
- If audio processing fails, verify FFmpeg installation:
  ```bash
  conda install ffmpeg
  ```
- For microphone issues, check system permissions
- Clear browser cache if UI elements malfunction