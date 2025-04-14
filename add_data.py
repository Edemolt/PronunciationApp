import os
import json
import csv

def process_files(json_folder, data_folder, csv_filename):
    # Determine if we need to write the header by checking if the CSV file exists.
    csv_exists = os.path.exists(csv_filename)
    
    with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header if file does not exist.
        if not csv_exists:
            writer.writerow(["sentence", "mp3_file", "wav_file", "json_file"])
        
        # Iterate through all files in the json folder.
        for file in os.listdir(json_folder):
            if file.lower().endswith('.json'):
                json_file_path = os.path.join(json_folder, file)
                try:
                    with open(json_file_path, 'r', encoding='utf-8') as jf:
                        data = json.load(jf)
                    
                    # Extract the transcript from the JSON file.
                    transcript = data.get("transcript", "")
                    if transcript:
                        # Build the corresponding mp3 and wav file names.
                        base_filename = os.path.splitext(file)[0]
                        mp3_filename = base_filename + ".mp3"
                        wav_filename = base_filename + ".wav"
                        
                        # Build file paths.
                        mp3_path = os.path.join(data_folder, mp3_filename)
                        wav_path = os.path.join(data_folder, wav_filename)
                        
                        # Write the row in CSV format.
                        writer.writerow([transcript, mp3_path, wav_path, json_file_path])
                    else:
                        print(f"No transcript found in {json_file_path}.")
                except Exception as e:
                    print(f"Error processing {json_file_path}: {e}")

if __name__ == "__main__":
    # Define the folder paths.
    json_folder = "json_files"
    data_folder = "data"   # folder containing both the mp3 and wav files
    csv_filename = "timed_data.csv"  # CSV file to create or append
    
    process_files(json_folder, data_folder, csv_filename)
