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
    const transcriptText = document.getElementById('transcript-text');
    
    // Lexicon Counts
    const posCount = document.getElementById('pos-count');
    const negCount = document.getElementById('neg-count');

    // Quotes
    const posQuote = document.getElementById('pos-quote');
    const negQuote = document.getElementById('neg-quote');

    // Visuals
    const wordcloudBox = document.getElementById('wordcloud-box');
    const syuzhetBox = document.getElementById('syuzhet-box');
    const wordcloudCanvas = document.getElementById('wordcloud-canvas');
    const syuzhetCanvas = document.getElementById('syuzhet-chart');
    
    let chartInstance = null; // To keep track and destroy previous chart instances

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

            // Populate Quotes
            posQuote.textContent = `"${data.top_pos_quote || 'N/A'}"`;
            negQuote.textContent = `"${data.top_neg_quote || 'N/A'}"`;
            
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

            // Render Interactive Word Cloud
            if (data.wordcloud_data && data.wordcloud_data.length > 0) {
                wordcloudBox.style.display = 'block';
                // Adjust sizes for wordcloud2 (scale based on max freq)
                const maxFreq = data.wordcloud_data[0][1];
                const weightFactor = 100 / maxFreq; 
                
                WordCloud(wordcloudCanvas, { 
                    list: data.wordcloud_data,
                    weightFactor: weightFactor,
                    fontFamily: 'Inter, sans-serif',
                    color: 'random-light',
                    backgroundColor: 'transparent',
                    rotateRatio: 0.5,
                    rotationSteps: 2,
                    gridSize: 8,
                    shape: 'circle'
                });
            } else {
                wordcloudBox.style.display = 'none';
            }

            // Render Interactive Chart.js Plot
            if (data.syuzhet_data && data.syuzhet_data.length > 0) {
                syuzhetBox.style.display = 'block';
                
                if (chartInstance) {
                    chartInstance.destroy();
                }

                const labels = data.syuzhet_data.map((_, index) => `Chunk ${index + 1}`);

                chartInstance = new Chart(syuzhetCanvas, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Sentiment Polarity',
                            data: data.syuzhet_data,
                            borderColor: '#3b82f6',
                            backgroundColor: 'rgba(59, 130, 246, 0.2)',
                            pointBackgroundColor: '#8b5cf6',
                            pointBorderColor: '#fff',
                            pointHoverBackgroundColor: '#fff',
                            pointHoverBorderColor: '#8b5cf6',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.4 // smooth curve
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        interaction: {
                            mode: 'index',
                            intersect: false,
                        },
                        scales: {
                            y: {
                                grid: {
                                    color: 'rgba(255, 255, 255, 0.1)'
                                },
                                ticks: {
                                    color: '#94a3b8'
                                }
                            },
                            x: {
                                grid: {
                                    display: false
                                },
                                ticks: {
                                    color: '#94a3b8',
                                    maxTicksLimit: 10
                                }
                            }
                        },
                        plugins: {
                            legend: {
                                display: false
                            },
                            tooltip: {
                                backgroundColor: 'rgba(15, 23, 42, 0.9)',
                                titleColor: '#fff',
                                bodyColor: '#fff',
                                borderColor: '#334155',
                                borderWidth: 1
                            }
                        }
                    }
                });
            } else {
                syuzhetBox.style.display = 'none';
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
