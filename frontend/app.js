
const API_BASE_URL = '';


const TEST_TYPE_LABELS = {
    'K': 'Knowledge & Skills',
    'P': 'Personality & Behavior',
    'C': 'Cognitive',
    'B': 'Behavioral'
};


const sampleQueries = [
    "I am hiring for Java developers who can also collaborate effectively with my business teams",
    "Looking to hire mid-level professionals who are proficient in Python, SQL and JavaScript",
    "I want to hire new graduates for a sales role in my company"
];


let queryInput, searchBtn, loading, error, errorMessage, results, resultsList, resultCount;

document.addEventListener('DOMContentLoaded', () => {

    queryInput = document.getElementById('query');
    searchBtn = document.getElementById('searchBtn');
    loading = document.getElementById('loading');
    error = document.getElementById('error');
    errorMessage = document.getElementById('errorMessage');
    results = document.getElementById('results');
    resultsList = document.getElementById('resultsList');
    resultCount = document.getElementById('resultCount');


    searchBtn.addEventListener('click', handleSearch);
    queryInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && e.ctrlKey) {
            handleSearch();
        }
    });

    const randomSample = sampleQueries[Math.floor(Math.random() * sampleQueries.length)];
    queryInput.value = randomSample;
    queryInput.placeholder = randomSample;
});

async function handleSearch() {
    const query = queryInput.value.trim();

    if (!query) {
        showError('Please enter a job description or query');
        return;
    }


    hideError();
    hideResults();
    showLoading();

    try {
        const response = await fetch(`${API_BASE_URL}/recommend`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: query,
                top_k: 10
            })
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();

        displayResults(data);

    } catch (err) {
        console.error('Error:', err);
        showError(`Failed to get recommendations: ${err.message}. Make sure the API is running on ${API_BASE_URL}`);
    } finally {
        hideLoading();
    }
}


function displayResults(data) {
    const recommendations = data.recommendations || [];

    if (recommendations.length === 0) {
        showError('No recommendations found for this query');
        return;
    }

    resultCount.textContent = `${recommendations.length} Results`;

    resultsList.innerHTML = '';


    recommendations.forEach((assessment, index) => {
        const card = createResultCard(assessment, index + 1);
        resultsList.appendChild(card);

        card.style.animationDelay = `${index * 0.05}s`;
    });

    showResults();
}


function createResultCard(assessment, rank) {
    const card = document.createElement('div');
    card.className = 'result-card';

    const testTypeLabel = TEST_TYPE_LABELS[assessment.test_type] || 'Unknown';
    const score = assessment.score !== undefined ? (assessment.score * 100).toFixed(1) : 'N/A';

    card.innerHTML = `
        <div class="result-header">
            <div class="result-rank">${rank}</div>
            <div style="flex: 1;">
                <div class="result-title">${escapeHtml(assessment.assessment_name)}</div>
                <div class="result-meta">
                    <span class="test-type-badge test-type-${assessment.test_type}">
                        ${testTypeLabel}
                    </span>
                    <span class="result-score">Relevance: ${score}%</span>
                </div>
            </div>
        </div>
        <a href="${escapeHtml(assessment.assessment_url)}" target="_blank" class="result-link">
            View Assessment →
        </a>
    `;

    return card;
}


function showLoading() {
    loading.classList.remove('hidden');
    searchBtn.disabled = true;
}

function hideLoading() {
    loading.classList.add('hidden');
    searchBtn.disabled = false;
}

function showError(message) {
    errorMessage.textContent = message;
    error.classList.remove('hidden');
}

function hideError() {
    error.classList.add('hidden');
}

function showResults() {
    results.classList.remove('hidden');
}

function hideResults() {
    results.classList.add('hidden');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
