from flask import Flask, request, jsonify, render_template
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import re
import os
from textblob import TextBlob
from nrclex import NRCLex
from wordcloud import WordCloud
import matplotlib
matplotlib.use('Agg')  # Required for generating plots without a GUI
import matplotlib.pyplot as plt
import numpy as np

app = Flask(__name__)
# Ensure static folder exists for wordcloud images
os.makedirs('static', exist_ok=True)

def extract_video_id(url):
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed_url.path == '/watch':
            query_params = parse_qs(parsed_url.query)
            return query_params['v'][0]
        if parsed_url.path.startswith('/embed/'):
            return parsed_url.path.split('/')[2]
        if parsed_url.path.startswith('/v/'):
            return parsed_url.path.split('/')[2]
    return url

def get_youtube_transcript(video_url):
    video_id = extract_video_id(video_url)
    try:
        api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id)
        # Prefer manually created transcript, fallback to generated
        try:
            transcript = transcript_list.find_manually_created_transcript(['en'])
        except:
            transcript = transcript_list.find_generated_transcript(['en'])
            
        fetched = transcript.fetch()
        text = "\n".join(snippet.text for snippet in fetched)
        return text
    except Exception as e:
        return f"Error fetching transcript: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'No URL provided'}), 400
        
    url = data['url']
    transcript = get_youtube_transcript(url)
    
    if transcript.startswith("Error fetching transcript"):
        return jsonify({'error': transcript}), 400
        
    # --- 1. Basic Stats ---
    word_count = len(re.findall(r'\w+', transcript))
    
    # --- 2. Sentiment Analysis (TextBlob) ---
    blob = TextBlob(transcript)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        sentiment_label = "Positive & Happy"
    elif polarity < -0.1:
        sentiment_label = "Negative & Sad"
    else:
        sentiment_label = "Neutral"

    # --- 3. Emotion Analysis (NRCLex) ---
    emotion_analyzer = NRCLex()
    emotion_analyzer.load_raw_text(transcript)
    
    emotions = emotion_analyzer.affect_frequencies
    raw_scores = emotion_analyzer.raw_emotion_scores
    
    # Extract Bing-like counts
    positive_words = raw_scores.get('positive', 0)
    negative_words = raw_scores.get('negative', 0)

    # Filter out positive/negative, keep actual emotions
    filtered_emotions = {k: v for k, v in emotions.items() if k not in ['positive', 'negative', 'anticip'] and v > 0}
    
    top_emotions = []
    if filtered_emotions:
        # Sort by value descending
        sorted_emotions = sorted(filtered_emotions.items(), key=lambda item: item[1], reverse=True)
        top_emotions = [{"emotion": k.capitalize(), "score": round(v * 100, 1)} for k, v in sorted_emotions[:3]]

    # --- 4. Conclusion Generation ---
    emotion_names = [e['emotion'].lower() for e in top_emotions]
    emotion_str = ", ".join(emotion_names) if emotion_names else "neutral feelings"
    conclusion = f"The overall tone of the video is {sentiment_label} (Polarity Score: {polarity:.2f}). " \
                 f"The primary emotions expressed are {emotion_str}."

    video_id = extract_video_id(url)

    # --- 5. Word Cloud Generation ---
    wc_filename = f"wordcloud_{video_id}.png"
    wc_path = os.path.join('static', wc_filename)
    try:
        wordcloud = WordCloud(width=800, height=400, background_color='#1e293b', colormap='viridis').generate(transcript)
        plt.figure(figsize=(8, 4), facecolor='#1e293b')
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.tight_layout(pad=0)
        plt.savefig(wc_path, facecolor='#1e293b')
        plt.close()
        wc_url = f"/static/{wc_filename}"
    except Exception as e:
        wc_url = None
        print("Word cloud error:", e)

    # --- 6. Syuzhet-style Sentiment Trajectory Plot ---
    sz_filename = f"syuzhet_{video_id}.png"
    sz_path = os.path.join('static', sz_filename)
    try:
        # Split text into chunks to simulate narrative time
        # E.g., split into 20 chunks
        words = transcript.split()
        num_chunks = 20
        chunk_size = max(1, len(words) // num_chunks)
        chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
        
        scores = [TextBlob(chunk).sentiment.polarity for chunk in chunks]
        
        # Smooth the line slightly for better visuals (rolling average)
        if len(scores) > 3:
            window_size = 3
            scores = np.convolve(scores, np.ones(window_size)/window_size, mode='valid')

        plt.figure(figsize=(8, 4), facecolor='#1e293b')
        ax = plt.axes()
        ax.set_facecolor('#1e293b')
        
        plt.plot(scores, color='#3b82f6', linewidth=2.5, marker='o', markersize=4, markerfacecolor='#8b5cf6')
        plt.axhline(y=0, color='#ef4444', linestyle='--', linewidth=1.5)
        
        plt.title('Sentiment Trajectory (Syuzhet-style)', color='#f8fafc', fontsize=14, pad=15)
        plt.xlabel('Narrative Time (Chunks)', color='#94a3b8', fontsize=10)
        plt.ylabel('Sentiment Polarity', color='#94a3b8', fontsize=10)
        
        plt.tick_params(colors='#94a3b8')
        for spine in ax.spines.values():
            spine.set_color('#334155')

        plt.tight_layout()
        plt.savefig(sz_path, facecolor='#1e293b')
        plt.close()
        sz_url = f"/static/{sz_filename}"
    except Exception as e:
        sz_url = None
        print("Syuzhet plot error:", e)


    analysis_result = {
        'transcript': transcript,
        'word_count': word_count,
        'sentiment_label': sentiment_label,
        'polarity': polarity,
        'top_emotions': top_emotions,
        'positive_words': positive_words,
        'negative_words': negative_words,
        'conclusion': conclusion,
        'wordcloud_url': wc_url,
        'syuzhet_url': sz_url
    }
    
    return jsonify(analysis_result)

if __name__ == '__main__':
    app.run(debug=True)
