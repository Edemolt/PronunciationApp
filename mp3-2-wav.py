import os
from pydub import AudioSegment

def convert_all_mp3_to_wav(mp3_folder="useful clips", wav_folder="wave files"):
    # Create output directory if it doesn't exist
    os.makedirs(wav_folder, exist_ok=True)

    # Loop through all files in the mp3 folder
    for filename in os.listdir(mp3_folder):
        if filename.endswith(".mp3"):
            mp3_path = os.path.join(mp3_folder, filename)
            wav_filename = os.path.splitext(filename)[0] + ".wav"
            wav_path = os.path.join(wav_folder, wav_filename)

            try:
                sound = AudioSegment.from_mp3(mp3_path)
                sound.export(wav_path, format="wav")
                print(f"Converted: {filename} -> {wav_filename}")
            except Exception as e:
                print(f"Failed to convert {filename}: {e}")
convert_all_mp3_to_wav()