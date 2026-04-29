# YouTube Review Analyzer

A Python-based web application designed to analyze YouTube video transcripts using Sentiment Analysis, Emotion Extraction, and Word Clouds.

## Features

- **Transcript Extraction**: Automatically downloads the English transcript of any standard YouTube video URL using `youtube_transcript_api`.
- **Sentiment Analysis**: Calculates the polarity score of the transcript (Positive, Negative, Neutral) using `TextBlob`.
- **Emotion Extraction**: Identifies the primary emotions expressed in the video (e.g., Joy, Anticipation, Trust) using `NRCLex`.
- **Word Cloud Generation**: Automatically generates a word cloud image to highlight the most frequently used words.

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **Analysis**: TextBlob, NRCLex, WordCloud, Matplotlib

## Setup Instructions

1. Clone the repository.
2. Set up a Python virtual environment: `python -m venv venv`
3. Activate the virtual environment.
4. Install dependencies: `pip install -r requirements.txt`
5. Run the application: `python app.py`
6. Open your browser and navigate to `http://127.0.0.1:5000`

## Author
Azrul Zulhilmi Ahmad Rosli
