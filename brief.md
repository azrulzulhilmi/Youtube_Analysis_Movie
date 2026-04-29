# YouTube Review Analyzer

## Project Overview & Brief
This project is a web application designed to analyze YouTube videos. The goal is to build a beginner friendly tool where a user can provide a YouTube video URL. The application will then extract the transcript from the video and process it to provide an analysis or review. 

**Target Repository:** [https://github.com/azrulzulhilmi/Youtube_Review.git](https://github.com/azrulzulhilmi/Youtube_Review.git)

## Tech Stack & Planning
We are keeping the architecture simple and clean:
* **Backend:** Flask (Python) to serve the API and run the transcript extraction script.
* **Frontend:** HTML, basic CSS, and plain JavaScript.
* **Version Control:** Git and GitHub.

## Core Features
* **Smart URL Input:** A simple user interface with a text box that accepts any standard YouTube link format.
* **Automatic Transcript Extraction:** A backend service that automatically takes the video ID and downloads the English transcript using the `youtube_transcript_api` library.
* **Analysis Display:** A clean results panel on the website that displays the processed analysis and transcript text.

## Website Sections (Single Page Layout)
* **Header:** The website title and a short sentence explaining what it does.
* **Input Area:** A large, clear text box for pasting the YouTube link, alongside an "Analyze" button.
* **Results Panel:** A box that appears below the input area to display the final transcript or analysis once it is ready.

## Instructions for AI Assistant (Vibecode)
Please build a full stack web application with the following specifications:
1. Create a frontend with an input field for the YouTube URL and a submit button.
2. Create a backend API endpoint (using Flask or FastAPI) that receives the URL.
3. Implement the transcript extraction logic provided below in the backend.
4. Connect the extraction output to an analysis function (such as summarizing or analyzing sentiment).
5. Return the analysis to the frontend and display it to the user in a readable format.

## Build Steps & Deployment Workflow
1. **Step 1 (Backend):** Set up a basic Flask server, integrate the provided Python transcript code, and create an API route that receives a URL and returns the text.
2. **Step 2 (Frontend):** Write the HTML for the input box and button, then add some simple CSS to make it look clean.
3. **Step 3 (Integration):** Write the JavaScript to send the URL from the frontend to the Flask server and update the page with the result.
4. **Step 4 (Local Testing):** You must build, run, and test the complete application on localhost first. Ensure the frontend successfully sends the URL to the backend, the backend fetches the transcript, and the analysis is displayed correctly without any errors.
5. **Step 5 (Push to GitHub):** Only after the application has been thoroughly tested and verified working on localhost, you are instructed to commit and push the working codebase to the project repository: [https://github.com/azrulzulhilmi/Youtube_Review.git](https://github.com/azrulzulhilmi/Youtube_Review.git).

## Setup Instructions
1. Install the required Python packages: `pip install youtube_transcript_api flask`
2. Run the backend server locally.
3. Open the frontend interface in a web browser to test.

***

### Python Code for Transcript Extraction

Use this robust version of the transcript extraction code in the backend. It includes a helper function to automatically extract the video ID from any standard YouTube link format.

```python
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

def extract_video_id(url):
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    if parsed_url.hostname in ('[www.youtube.com](https://www.youtube.com)', 'youtube.com'):
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
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Prefer manually created transcript, fallback to generated
        try:
            transcript = transcript_list.find_manually_created_transcript(['en'])
        except:
            transcript = transcript_list.find_generated_transcript(['en'])
            
        fetched = transcript.fetch()
        text = "\n".join(snippet['text'] for snippet in fetched)
        return text
        
    except Exception as e:
        return f"Error fetching transcript: {str(e)}"