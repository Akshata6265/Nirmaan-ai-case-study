/**
 * Frontend JavaScript for Communication Skills Scoring System
 * Handles user interactions and API communication
 */

// API Base URL
const API_BASE_URL = window.location.origin;

// DOM Elements
const transcriptInput = document.getElementById('transcriptInput');
const wordCountDisplay = document.getElementById('wordCount');
const scoreBtn = document.getElementById('scoreBtn');
const loadSampleBtn = document.getElementById('loadSampleBtn');
const clearBtn = document.getElementById('clearBtn');
const loadingIndicator = document.getElementById('loadingIndicator');
const resultsSection = document.getElementById('resultsSection');
const errorMessage = document.getElementById('errorMessage');
const overallScoreDisplay = document.getElementById('overallScore');
const scoreCategoryDisplay = document.getElementById('scoreCategory');
const totalWordCountDisplay = document.getElementById('totalWordCount');
const timestampDisplay = document.getElementById('timestamp');
const criteriaContainer = document.getElementById('criteriaContainer');
const scoreCircleFill = document.getElementById('scoreCircleFill');
const exportJsonBtn = document.getElementById('exportJsonBtn');
const printBtn = document.getElementById('printBtn');
const sampleModal = document.getElementById('sampleModal');
const closeModalBtn = document.getElementById('closeModalBtn');
const sampleList = document.getElementById('sampleList');

// State
let currentResult = null;
let sampleTranscripts = [];

// Event Listeners
transcriptInput.addEventListener('input', updateWordCount);
scoreBtn.addEventListener('click', handleScoreTranscript);
loadSampleBtn.addEventListener('click', handleLoadSample);
clearBtn.addEventListener('click', handleClear);
exportJsonBtn.addEventListener('click', handleExportJson);
printBtn.addEventListener('click', handlePrint);
closeModalBtn.addEventListener('click', closeModal);

// Initialize
updateWordCount();
checkAPIHealth();

/**
 * Update word count display
 */
function updateWordCount() {
    const text = transcriptInput.value.trim();
    const wordCount = text ? text.split(/\s+/).filter(w => w.length > 0).length : 0;
    wordCountDisplay.textContent = `${wordCount} words`;
}

/**
 * Check API health status
 */
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        const data = await response.json();
        console.log('API Status:', data.status);
    } catch (error) {
        console.error('API health check failed:', error);
    }
}

/**
 * Handle score transcript button click
 */
async function handleScoreTranscript() {
    const transcript = transcriptInput.value.trim();
    
    // Validate input
    if (!transcript) {
        showError('Please enter a transcript to score.');
        return;
    }
    
    const wordCount = transcript.split(/\s+/).length;
    if (wordCount < 10) {
        showError(`Transcript is too short (${wordCount} words). Minimum 10 words required.`);
        return;
    }
    
    // Show loading, hide results and errors
    showLoading();
    hideResults();
    hideError();
    
    try {
        // Call API
        const response = await fetch(`${API_BASE_URL}/api/score`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ transcript })
        });
        
        const result = await response.json();
        
        if (!response.ok || !result.success) {
            throw new Error(result.error || 'Failed to score transcript');
        }
        
        // Store result
        currentResult = result.data;
        
        // Display results
        displayResults(result.data);
        
    } catch (error) {
        console.error('Error scoring transcript:', error);
        showError(`Error: ${error.message}`);
    } finally {
        hideLoading();
    }
}

/**
 * Display scoring results
 */
function displayResults(data) {
    // Overall score
    const score = Math.round(data.overall_score);
    overallScoreDisplay.textContent = score;
    scoreCategoryDisplay.textContent = data.score_category || getCategoryFromScore(score);
    totalWordCountDisplay.textContent = data.word_count;
    
    // Format timestamp
    if (data.timestamp) {
        const date = new Date(data.timestamp);
        timestampDisplay.textContent = date.toLocaleString();
    }
    
    // Animate score circle
    animateScoreCircle(score);
    
    // Display criteria scores
    displayCriteriaScores(data.criteria_scores);
    
    // Show results section
    showResults();
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/**
 * Animate the score circle
 */
function animateScoreCircle(score) {
    const circumference = 2 * Math.PI * 90; // radius = 90
    const offset = circumference - (score / 100) * circumference;
    scoreCircleFill.style.strokeDashoffset = offset;
}

/**
 * Display criteria scores
 */
function displayCriteriaScores(criteria) {
    criteriaContainer.innerHTML = '';
    
    criteria.forEach((criterion, index) => {
        const criterionElement = createCriterionElement(criterion, index);
        criteriaContainer.appendChild(criterionElement);
    });
}

/**
 * Create a criterion element
 */
function createCriterionElement(criterion, index) {
    const div = document.createElement('div');
    div.className = 'criterion-item';
    div.style.animationDelay = `${index * 0.1}s`;
    
    const score = Math.round(criterion.score);
    const scoreColor = getScoreColor(score);
    
    div.innerHTML = `
        <div class="criterion-header">
            <div class="criterion-name">${criterion.criterion}</div>
            <div class="criterion-score" style="color: ${scoreColor}">${score}/100</div>
        </div>
        
        <div class="score-bar">
            <div class="score-bar-fill" style="width: ${score}%; background: ${scoreColor}"></div>
        </div>
        
        <div class="criterion-details">
            <div class="detail-row">
                <span class="detail-label">Weight:</span>
                <span class="detail-value">${criterion.weight}%</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Semantic Similarity:</span>
                <span class="detail-value">${(criterion.semantic_similarity * 100).toFixed(1)}%</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Keyword Match Rate:</span>
                <span class="detail-value">${(criterion.keyword_match_rate * 100).toFixed(1)}%</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Word Count Status:</span>
                <span class="detail-value">${formatWordCountStatus(criterion.word_count_status)}</span>
            </div>
        </div>
        
        ${criterion.keywords_found && criterion.keywords_found.length > 0 ? `
            <div class="detail-row">
                <span class="detail-label">Keywords Found:</span>
                <div class="keywords-list">
                    ${criterion.keywords_found.map(kw => `<span class="keyword-tag">${kw}</span>`).join('')}
                </div>
            </div>
        ` : ''}
        
        ${criterion.keywords_missing && criterion.keywords_missing.length > 0 && criterion.keywords_missing.length <= 5 ? `
            <div class="detail-row">
                <span class="detail-label">Suggested Keywords:</span>
                <div class="keywords-list">
                    ${criterion.keywords_missing.slice(0, 5).map(kw => `<span class="keyword-tag missing">${kw}</span>`).join('')}
                </div>
            </div>
        ` : ''}
        
        <div class="feedback-text">
            <strong>Feedback:</strong> ${criterion.feedback}
        </div>
        
        ${criterion.score_breakdown ? `
            <details style="margin-top: 1rem;">
                <summary style="cursor: pointer; color: var(--text-secondary); font-size: 0.9rem;">
                    View Score Breakdown
                </summary>
                <div style="margin-top: 0.5rem; padding: 0.5rem; background: var(--bg-primary); border-radius: var(--radius-sm);">
                    <div>Rule-based: ${criterion.score_breakdown.rule_based}</div>
                    <div>Semantic: ${criterion.score_breakdown.semantic}</div>
                    <div>Rubric-driven: ${criterion.score_breakdown.rubric_driven}</div>
                </div>
            </details>
        ` : ''}
    `;
    
    return div;
}

/**
 * Get color based on score
 */
function getScoreColor(score) {
    if (score >= 90) return '#10b981'; // green
    if (score >= 80) return '#3b82f6'; // blue
    if (score >= 70) return '#8b5cf6'; // purple
    if (score >= 60) return '#f59e0b'; // amber
    if (score >= 50) return '#f97316'; // orange
    return '#ef4444'; // red
}

/**
 * Get category from score
 */
function getCategoryFromScore(score) {
    if (score >= 90) return 'Excellent';
    if (score >= 80) return 'Very Good';
    if (score >= 70) return 'Good';
    if (score >= 60) return 'Satisfactory';
    if (score >= 50) return 'Fair';
    return 'Needs Improvement';
}

/**
 * Format word count status
 */
function formatWordCountStatus(status) {
    const statusMap = {
        'within_range': '✓ Within Range',
        'too_short': '⚠ Too Short',
        'too_long': '⚠ Too Long',
        'no_limit': '- No Limit'
    };
    return statusMap[status] || status;
}

/**
 * Handle load sample button click
 */
async function handleLoadSample() {
    try {
        // Load samples if not already loaded
        if (sampleTranscripts.length === 0) {
            const response = await fetch(`${API_BASE_URL}/api/samples`);
            const result = await response.json();
            
            if (result.success) {
                sampleTranscripts = result.data;
            } else {
                throw new Error('Failed to load samples');
            }
        }
        
        // Display samples in modal
        displaySampleModal();
        
    } catch (error) {
        console.error('Error loading samples:', error);
        showError('Failed to load sample transcripts');
    }
}

/**
 * Display sample modal
 */
function displaySampleModal() {
    sampleList.innerHTML = '';
    
    sampleTranscripts.forEach(sample => {
        const div = document.createElement('div');
        div.className = 'sample-item';
        div.innerHTML = `
            <div class="sample-header">
                <span class="sample-id">Sample #${sample.ID}</span>
                <span class="sample-score">Expected: ${sample.Expected_Score_Range}</span>
            </div>
            <div class="sample-preview">${sample.Transcript}</div>
            ${sample.Notes ? `<div style="margin-top: 0.5rem; font-size: 0.85rem; color: var(--text-secondary); font-style: italic;">${sample.Notes}</div>` : ''}
        `;
        
        div.addEventListener('click', () => {
            transcriptInput.value = sample.Transcript;
            updateWordCount();
            closeModal();
        });
        
        sampleList.appendChild(div);
    });
    
    sampleModal.classList.remove('hidden');
}

/**
 * Close modal
 */
function closeModal() {
    sampleModal.classList.add('hidden');
}

// Close modal when clicking outside
sampleModal.addEventListener('click', (e) => {
    if (e.target === sampleModal) {
        closeModal();
    }
});

/**
 * Handle clear button click
 */
function handleClear() {
    transcriptInput.value = '';
    updateWordCount();
    hideResults();
    hideError();
    currentResult = null;
}

/**
 * Handle export JSON button click
 */
function handleExportJson() {
    if (!currentResult) return;
    
    const dataStr = JSON.stringify(currentResult, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `communication-score-${Date.now()}.json`;
    link.click();
    
    URL.revokeObjectURL(url);
}

/**
 * Handle print button click
 */
function handlePrint() {
    window.print();
}

/**
 * Show/hide loading indicator
 */
function showLoading() {
    loadingIndicator.classList.remove('hidden');
    scoreBtn.disabled = true;
}

function hideLoading() {
    loadingIndicator.classList.add('hidden');
    scoreBtn.disabled = false;
}

/**
 * Show/hide results section
 */
function showResults() {
    resultsSection.classList.remove('hidden');
}

function hideResults() {
    resultsSection.classList.add('hidden');
}

/**
 * Show/hide error message
 */
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.remove('hidden');
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        hideError();
    }, 5000);
}

function hideError() {
    errorMessage.classList.add('hidden');
}

/**
 * Keyboard shortcuts
 */
document.addEventListener('keydown', (e) => {
    // Ctrl+Enter to score
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        handleScoreTranscript();
    }
    
    // Escape to close modal
    if (e.key === 'Escape') {
        closeModal();
    }
});

console.log('Communication Skills Scoring System - Frontend Loaded');
console.log('Tip: Press Ctrl+Enter to quickly score a transcript');
