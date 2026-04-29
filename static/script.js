document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('analyze-form');
    const urlInput = document.getElementById('youtube-url');
    const analyzeBtn = document.getElementById('analyze-btn');
    const btnText = analyzeBtn.querySelector('.btn-text');
    const loader = analyzeBtn.querySelector('.loader');
    const errorMessage = document.getElementById('error-message');
    const resultsPanel = document.getElementById('results-panel');
    const analysisText = document.getElementById('analysis-text');
    const transcriptText = document.getElementById('transcript-text');

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
            analysisText.textContent = data.analysis;
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
