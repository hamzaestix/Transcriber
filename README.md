# YouTube Video to Text Transcriber

This Streamlit app allows you to transcribe YouTube videos to text using AssemblyAI's transcription services. The app downloads the audio from the video, uploads it to AssemblyAI, and generates a text and subtitle file for you to download.

## Features
- Convert YouTube videos to MP3
- Upload audio to AssemblyAI for transcription
- Save transcripts in `.txt` and `.srt` formats
- Download the transcripts as a `.zip` file

## Requirements
- Python 3.8 or higher
- `yt-dlp` for downloading YouTube videos
- `streamlit` for building the web app
- `ffmpeg` for converting the video to MP3 format

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
