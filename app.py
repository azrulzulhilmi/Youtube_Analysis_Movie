from flask import Flask, request, jsonify, render_template
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import re
import os
from collections import Counter
from textblob import TextBlob
from nrclex import NRCLex

app = Flask(__name__)

STOPWORDS = set([
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd",
    'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers',
    'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
    'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been',
    'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if',
    'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
    'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out',
    'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
    'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
    'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should',
    "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't",
    'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't",
    'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't",
    'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't", 'like', 'know', 'get', 'got', 'think',
    'go', 'really', 'one', 'would', 'could', 'let', 'make', 'see'
])

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
        
    # --- 1. Basic Stats & NLP ---
    words = re.findall(r'\b\w+\b', transcript.lower())
    word_count = len(words)
    blob = TextBlob(transcript)
    
    # --- 2. Key Quotes ---
    sentences = blob.sentences
    top_pos_sentence = ""
    top_neg_sentence = ""
    max_pos = -1.0
    min_neg = 1.0
    
    for sentence in sentences:
        s_polarity = sentence.sentiment.polarity
        text_str = str(sentence)
        if len(text_str.split()) > 3: # Avoid very short sentences
            if s_polarity > max_pos:
                max_pos = s_polarity
                top_pos_sentence = text_str
            if s_polarity < min_neg:
                min_neg = s_polarity
                top_neg_sentence = text_str

    # --- 3. Sentiment Analysis (TextBlob) ---
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        sentiment_label = "Positive & Happy"
    elif polarity < -0.1:
        sentiment_label = "Negative & Sad"
    else:
        sentiment_label = "Neutral"

    # --- 4. Emotion Analysis (NRCLex) ---
    emotion_analyzer = NRCLex()
    emotion_analyzer.load_raw_text(transcript)
    
    emotions = emotion_analyzer.affect_frequencies
    raw_scores = emotion_analyzer.raw_emotion_scores
    
    positive_words = raw_scores.get('positive', 0)
    negative_words = raw_scores.get('negative', 0)

    filtered_emotions = {k: v for k, v in emotions.items() if k not in ['positive', 'negative', 'anticip'] and v > 0}
    
    top_emotions = []
    if filtered_emotions:
        sorted_emotions = sorted(filtered_emotions.items(), key=lambda item: item[1], reverse=True)
        top_emotions = [{"emotion": k.capitalize(), "score": round(v * 100, 1)} for k, v in sorted_emotions[:3]]

    emotion_names = [e['emotion'].lower() for e in top_emotions]
    emotion_str = ", ".join(emotion_names) if emotion_names else "neutral feelings"
    conclusion = f"The overall tone of the video is {sentiment_label} (Polarity Score: {polarity:.2f}). " \
                 f"The primary emotions expressed are {emotion_str}."

    # --- 5. Word Frequencies for Word Cloud JS ---
    filtered_words = [w for w in words if w not in STOPWORDS and not w.isdigit() and len(w) > 2]
    word_freq = Counter(filtered_words).most_common(100)
    # Format for wordcloud2.js: [[word, freq], ...]
    cloud_data = [[word, freq] for word, freq in word_freq]

    # --- 6. Syuzhet-style Sentiment Trajectory (Chart JS Data) ---
    num_chunks = 20
    chunk_size = max(1, len(words) // num_chunks)
    chunk_strings = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    syuzhet_scores = [TextBlob(chunk).sentiment.polarity for chunk in chunk_strings]
    
    # Smooth (Rolling average)
    smoothed_scores = []
    if len(syuzhet_scores) > 2:
        for i in range(len(syuzhet_scores)):
            start = max(0, i-1)
            end = min(len(syuzhet_scores), i+2)
            smoothed_scores.append(sum(syuzhet_scores[start:end]) / (end-start))
    else:
        smoothed_scores = syuzhet_scores

    analysis_result = {
        'transcript': transcript,
        'word_count': word_count,
        'sentiment_label': sentiment_label,
        'polarity': polarity,
        'top_emotions': top_emotions,
        'positive_words': positive_words,
        'negative_words': negative_words,
        'conclusion': conclusion,
        'top_pos_quote': top_pos_sentence,
        'top_neg_quote': top_neg_sentence,
        'wordcloud_data': cloud_data,
        'syuzhet_data': smoothed_scores
    }
    
    return jsonify(analysis_result)

if __name__ == '__main__':
    app.run(debug=True)
