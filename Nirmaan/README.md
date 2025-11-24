# Communication Skills Scoring System

## Overview
An AI-powered tool to analyze and score students' spoken communication skills based on transcribed audio. The system uses a combination of rule-based methods, NLP-based semantic scoring, and data-driven rubric evaluation to provide comprehensive feedback.

## Features
- **Multi-approach Scoring**: Combines rule-based, NLP semantic analysis, and rubric-driven weighting
- **Real-time Analysis**: Instant scoring and feedback generation
- **Detailed Feedback**: Per-criterion scores with keyword matches and semantic similarity
- **User-friendly UI**: Simple web interface for transcript input and result display
- **Flexible Input**: Support for text paste and file upload

## Technology Stack
- **Backend**: Python 3.8+, Flask
- **NLP**: sentence-transformers (all-MiniLM-L6-v2), NLTK, spaCy
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Data Processing**: pandas, openpyxl
- **Deployment**: Flask development server (can be deployed to AWS, Heroku, or any cloud platform)

## Project Structure
```
Deepa Task/
├── backend/                           # Flask API Backend
│   ├── app.py                        # Main Flask application server
│   ├── scoring_engine.py             # Core scoring logic (3 approaches)
│   ├── nlp_processor.py              # NLP and semantic analysis
│   ├── utils.py                      # Helper functions
│   └── __init__.py                   # Package initializer
├── frontend/                          # Web Interface
│   ├── index.html                    # Main UI page
│   ├── styles.css                    # Responsive styling
│   └── script.js                     # Frontend logic & API calls
├── data/                              # Data Files
│   └── Case study for interns.xlsx   # Official rubric from Nirmaan AI
├── tests/                             # Test Suite
│   ├── test_scoring.py               # Unit tests
│   └── __init__.py                   # Package initializer
├── requirements.txt                   # Python dependencies
├── README.md                          # Main documentation (this file)
├── START_HERE.md                      # Quick start guide
├── DEPLOYMENT.md                      # Deployment instructions
└── .gitignore                         # Git ignore rules
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Local Setup

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd "Deepa Task"
```

2. **Create a virtual environment**
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Download required NLP models**
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger')"
```

4. **Run the application**
```bash
cd backend
python app.py
```

5. **Access the application**
Open your browser and navigate to: `http://localhost:5000`

## Usage

1. **Open the web interface** at `http://localhost:5000`
2. **Paste or type** a transcript in the text area
3. **Click "Score Transcript"** to analyze
4. **View results**:
   - Overall score (0-100)
   - Per-criterion breakdown
   - Keyword matches
   - Semantic similarity scores
   - Feedback and suggestions

## Scoring Formula

The system uses a weighted combination of three approaches:

### 1. Rule-Based Scoring (40%)
- **Keyword Matching**: Checks presence of required keywords from rubric
- **Word Count Validation**: Verifies transcript meets min/max word limits
- **Exact Match Bonus**: Additional points for exact phrase matches

### 2. NLP-Based Semantic Scoring (40%)
- **Sentence Embeddings**: Uses sentence-transformers (all-MiniLM-L6-v2)
- **Cosine Similarity**: Measures semantic similarity between transcript and criterion description
- **Contextual Understanding**: Captures meaning beyond exact keywords

### 3. Rubric-Driven Weighting (20%)
- **Criterion Weights**: Applied from Excel rubric
- **Normalization**: Ensures final score is 0-100
- **Balanced Evaluation**: Combines all signals proportionally

**Final Score Calculation**:
```
For each criterion:
  criterion_score = (rule_score * 0.4) + (semantic_score * 0.4) + (rubric_score * 0.2)
  weighted_score = criterion_score * criterion_weight

Overall Score = sum(weighted_scores) / sum(weights) * 100
```

## API Endpoints

### POST `/api/score`
Analyzes transcript and returns scores.

**Request Body**:
```json
{
  "transcript": "string"
}
```

**Response**:
```json
{
  "overall_score": 85.5,
  "word_count": 150,
  "criteria_scores": [
    {
      "criterion": "Introduction & Greeting",
      "score": 90,
      "weight": 15,
      "keywords_found": ["hello", "name is"],
      "keywords_missing": [],
      "semantic_similarity": 0.87,
      "feedback": "Strong introduction with clear greeting and name mention.",
      "word_count_status": "within_range"
    }
  ],
  "timestamp": "2025-11-23T10:30:00Z"
}
```

## Rubric Structure

The Excel file (`data/Case study for interns.xlsx`) contains the official Nirmaan AI rubric:

**Evaluation Criteria (Total: 100 points)**

| Criterion | Weight | Description |
|-----------|--------|-------------|
| **Content & Structure** | 40% | |
| - Salutation | 5% | Quality of greeting (Hello, Good morning, etc.) |
| - Key Information | 30% | Name, age, school, family, hobbies (must-have + good-to-have) |
| - Flow | 5% | Logical order of information |
| **Speech Rate** | 10% | Words per minute (WPM) - ideal range 111-140 |
| **Language & Grammar** | 10% | Grammar correctness using error detection |
| **Vocabulary Richness** | 10% | Type-Token Ratio (TTR) for vocabulary diversity |
| **Clarity** | 15% | Filler word rate (um, uh, like, etc.) |
| **Engagement** | 15% | Sentiment analysis for positivity and enthusiasm |

**Sample Transcript Included**: The rubric sheet includes a sample student self-introduction with expected score of 86/100.

## Testing

Run the test suite:
```bash
python -m pytest tests/
```

Or test manually:
```bash
python tests/test_scoring.py
```

## Deployment

### Local Development
Already covered in Installation section above.

### Cloud Deployment (AWS/Heroku/etc.)
See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

### Docker (Optional)
```bash
docker build -t comm-scoring .
docker run -p 5000:5000 comm-scoring
```

## Future Enhancements
- [ ] Audio file upload with automatic transcription
- [ ] Speech rate calculation from audio duration
- [ ] Grammar error detection using LanguageTool API
- [ ] Advanced sentiment analysis (VADER)
- [ ] User authentication and history tracking
- [ ] Comparative analytics and progress tracking
- [ ] Export reports as PDF
- [ ] Multi-language support

## Troubleshooting

**Issue**: ModuleNotFoundError
- **Solution**: Ensure all dependencies are installed: `pip install -r requirements.txt`

**Issue**: Port 5000 already in use
- **Solution**: Change port in `backend/app.py` or kill the process using port 5000

**Issue**: Slow first load
- **Solution**: First-time model download takes time; subsequent runs are faster

## Contributing
Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License
MIT License - See LICENSE file for details

## Quick Start

For a streamlined setup experience, see [START_HERE.md](START_HERE.md) which provides step-by-step instructions for:
- Testing the application locally
- Creating and pushing to GitHub
- Recording demonstration video
- Final submission checklist

## GitHub Repository Setup

1. **Initialize repository**
```bash
cd "Deepa Task"
git init
git add .
git commit -m "Initial commit: Communication Skills Scoring System"
```

2. **Push to GitHub**
```bash
# Create a new repository on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

3. **Repository Settings**
- Ensure repository is **public**
- Add topics: `ai`, `nlp`, `flask`, `python`, `nirmaan-ai`, `scoring-system`
- Add description: "AI-powered communication skills scoring system for Nirmaan AI case study"

## Contact
For questions or support, please open an issue on GitHub.

## Acknowledgments
- sentence-transformers for semantic embeddings
- NLTK and spaCy for NLP processing
- Flask for the web framework
- Nirmaan AI for the case study opportunity
