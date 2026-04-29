document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('analyze-form');
    const urlInput = document.getElementById('youtube-url');
    const analyzeBtn = document.getElementById('analyze-btn');
    const btnText = analyzeBtn.querySelector('.btn-text');
    const loader = analyzeBtn.querySelector('.loader');
    const errorMessage = document.getElementById('error-message');
    const resultsPanel = document.getElementById('results-panel');
    
    // UI Elements for Data
    const conclusionText = document.getElementById('conclusion-text');
    const wordCount = document.getElementById('word-count');
    const polarityScore = document.getElementById('polarity-score');
    const emotionsList = document.getElementById('emotions-list');
    const wordcloudBox = document.getElementById('wordcloud-box');
    const wordcloudImg = document.getElementById('wordcloud-img');
    const transcriptText = document.getElementById('transcript-text');
    
    // Lexicon Counts
    const posCount = document.getElementById('pos-count');
    const negCount = document.getElementById('neg-count');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const url = urlInput.value.trim();
        if (!url) return;

        // Reset UI
        errorMessage.style.display = 'none';
        resultsPanel.style.display = 'none';
        analyzeBtn.disabled = true;
        btnText.style.display = 'none';
        loader.style.display = 'block';

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url: url })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to analyze video');
            }

            // Display Results
            conclusionText.textContent = data.conclusion;
            wordCount.textContent = data.word_count;
            polarityScore.textContent = data.polarity.toFixed(2);
            
            // Populate Lexicon counts
            posCount.textContent = data.positive_words || 0;
            negCount.textContent = data.negative_words || 0;
            
            // Color code polarity
            if (data.polarity > 0.1) {
                polarityScore.style.color = 'var(--positive-color)';
            } else if (data.polarity < -0.1) {
                polarityScore.style.color = 'var(--negative-color)';
            } else {
                polarityScore.style.color = 'var(--primary-color)';
            }

            // Render Emotions
            emotionsList.innerHTML = '';
            if (data.top_emotions && data.top_emotions.length > 0) {
                data.top_emotions.forEach(emotion => {
                    const li = document.createElement('li');
                    li.className = 'emotion-badge';
                    li.innerHTML = `<span>${emotion.emotion}</span> <span class="emotion-score">${emotion.score}%</span>`;
                    emotionsList.appendChild(li);
                });
            } else {
                emotionsList.innerHTML = '<li>No strong emotions detected.</li>';
            }

            // Render Word Cloud
            if (data.wordcloud_url) {
                // Append timestamp to prevent caching old images
                wordcloudImg.src = data.wordcloud_url + '?t=' + new Date().getTime();
                wordcloudBox.style.display = 'block';
            } else {
                wordcloudBox.style.display = 'none';
            }

            transcriptText.textContent = data.transcript;
            
            resultsPanel.style.display = 'flex';
            
            // Scroll to results
            resultsPanel.scrollIntoView({ behavior: 'smooth' });

        } catch (error) {
            errorMessage.textContent = error.message;
            errorMessage.style.display = 'block';
        } finally {
            // Restore button state
            analyzeBtn.disabled = false;
            btnText.style.display = 'block';
            loader.style.display = 'none';
        }
    });
});
