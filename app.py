from flask import Flask, request, jsonify, render_template
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import re

app = Flask(__name__)

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
        
    # Simple analysis: word count
    word_count = len(re.findall(r'\w+', transcript))
    
    analysis_result = {
        'transcript': transcript,
        'analysis': f"The transcript contains approximately {word_count} words."
    }
    
    return jsonify(analysis_result)

if __name__ == '__main__':
    app.run(debug=True)
