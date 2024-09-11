import streamlit as st
import yt_dlp
import os
import requests
import time
import shutil
from zipfile import ZipFile
import tempfile

# AssemblyAI API details
ASSEMBLYAI_API_KEY = ''  # Replace with your AssemblyAI API key
headers = {'authorization': ASSEMBLYAI_API_KEY, 'content-type': 'application/json'}

# Function to download the YouTube video and convert it to MP3
def download_youtube_audio(youtube_url, output_file='audio.mp3'):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
    os.rename('audio.mp3', output_file)
    return output_file

# Function to upload the MP3 file to AssemblyAI
def upload_to_assemblyai(file_path):
    with open(file_path, 'rb') as f:
        response = requests.post('https://api.assemblyai.com/v2/upload', headers=headers, files={'file': f})
        response_json = response.json()
        return response_json['upload_url']

# Function to transcribe the audio using AssemblyAI
def transcribe_audio(upload_url):
    transcript_request = {
        'audio_url': upload_url,
        'auto_highlights': True,
        'iab_categories': True
    }
    transcript_response = requests.post('https://api.assemblyai.com/v2/transcript', json=transcript_request, headers=headers)
    transcript_id = transcript_response.json()['id']
    
    polling_endpoint = f'https://api.assemblyai.com/v2/transcript/{transcript_id}'
    while True:
        transcript_result = requests.get(polling_endpoint, headers=headers)
        result = transcript_result.json()
        if result['status'] == 'completed':
            return result
        elif result['status'] == 'failed':
            raise Exception('Transcription failed')
        time.sleep(5)

# Function to save the transcript as .txt and .srt files
def save_transcript(transcript, temp_dir):
    txt_filename = os.path.join(temp_dir, 'transcript.txt')
    srt_filename = os.path.join(temp_dir, 'transcript.srt')
    
    with open(txt_filename, 'w') as txt_file:
        txt_file.write(transcript['text'])
    
    with open(srt_filename, 'w') as srt_file:
        for i, subtitle in enumerate(transcript['words']):
            start_time = int(subtitle['start']) // 1000
            end_time = int(subtitle['end']) // 1000
            start_minutes, start_seconds = divmod(start_time, 60)
            end_minutes, end_seconds = divmod(end_time, 60)
            srt_file.write(f"{i+1}\n")
            srt_file.write(f"{start_minutes:02}:{start_seconds:02},000 --> {end_minutes:02}:{end_seconds:02},000\n")
            srt_file.write(f"{subtitle['text']}\n\n")
    
    return txt_filename, srt_filename

# Streamlit app
st.title("YouTube Video To Text Transcriber")
st.write("Created by Hamza Akmal - A Project of Nine Alert")

youtube_url = st.text_input("Enter YouTube Video URL:")

if st.button("Start Transcription"):
    if not youtube_url:
        st.warning("Please provide a YouTube URL.")
    else:
        progress_bar = st.progress(0)
        progress_bar.progress(10)
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                st.write("Downloading audio...")
                mp3_file = download_youtube_audio(youtube_url, os.path.join(temp_dir, 'audio.mp3'))
                progress_bar.progress(30)

                st.write("Uploading audio to NineAlert Server...")
                upload_url = upload_to_assemblyai(mp3_file)
                progress_bar.progress(60)

                st.write("Transcribing audio...")
                transcript = transcribe_audio(upload_url)
                progress_bar.progress(90)

                st.write("Saving transcript...")
                txt_file, srt_file = save_transcript(transcript, temp_dir)

                # Create ZIP file
                zip_filename = os.path.join(temp_dir, "transcription_files.zip")
                with ZipFile(zip_filename, 'w') as zipf:
                    zipf.write(txt_file, os.path.basename(txt_file))
                    zipf.write(srt_file, os.path.basename(srt_file))
                progress_bar.progress(100)

                st.success("Transcription complete!")

                # Provide download button
                with open(zip_filename, 'rb') as f:
                    st.download_button(
                        label="Download Transcript Files (ZIP)",
                        data=f,
                        file_name="transcription_files.zip",
                        mime="application/zip"
                    )
        except Exception as e:
            st.error(f"Error: {str(e)}")
