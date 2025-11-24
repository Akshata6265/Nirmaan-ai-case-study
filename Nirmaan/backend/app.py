"""
Flask Backend API
Main application server for the Communication Skills Scoring System
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import traceback
from pathlib import Path
import sys

# Add backend directory to path for imports
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from scoring_engine import get_scoring_engine
from utils import validate_transcript, format_timestamp, load_sample_transcripts, get_score_category

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)  # Enable CORS for frontend-backend communication

# Initialize scoring engine (will load on first request)
scoring_engine = None

def init_scoring_engine():
    """Initialize scoring engine lazily"""
    global scoring_engine
    if scoring_engine is None:
        try:
            scoring_engine = get_scoring_engine()
            print("✓ Scoring engine initialized")
        except Exception as e:
            print(f"✗ Error initializing scoring engine: {str(e)}")
            traceback.print_exc()
            raise


@app.route('/')
def index():
    """Serve the main frontend page"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Communication Skills Scoring API is running',
        'timestamp': format_timestamp()
    })


@app.route('/api/rubric', methods=['GET'])
def get_rubric():
    """Get rubric information"""
    try:
        init_scoring_engine()
        rubric_info = scoring_engine.get_rubric_info()
        return jsonify({
            'success': True,
            'data': rubric_info,
            'timestamp': format_timestamp()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': format_timestamp()
        }), 500


@app.route('/api/samples', methods=['GET'])
def get_samples():
    """Get sample transcripts"""
    try:
        samples_df = load_sample_transcripts()
        samples = samples_df.to_dict('records')
        return jsonify({
            'success': True,
            'data': samples,
            'count': len(samples),
            'timestamp': format_timestamp()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': format_timestamp()
        }), 500


@app.route('/api/score', methods=['POST'])
def score_transcript():
    """
    Score a transcript
    
    Request body:
    {
        "transcript": "text to score"
    }
    
    Response:
    {
        "success": true,
        "data": {
            "overall_score": 85.5,
            "word_count": 150,
            "criteria_scores": [...],
            ...
        }
    }
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data or 'transcript' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing transcript in request body',
                'timestamp': format_timestamp()
            }), 400
        
        transcript = data['transcript']
        
        # Validate transcript
        validation = validate_transcript(transcript)
        if not validation['valid']:
            return jsonify({
                'success': False,
                'error': validation['message'],
                'timestamp': format_timestamp()
            }), 400
        
        # Initialize scoring engine if needed
        init_scoring_engine()
        
        # Score the transcript
        result = scoring_engine.score_transcript(transcript)
        
        # Add additional metadata
        result['timestamp'] = format_timestamp()
        result['score_category'] = get_score_category(result['overall_score'])
        
        return jsonify({
            'success': True,
            'data': result,
            'timestamp': format_timestamp()
        })
        
    except Exception as e:
        print(f"Error scoring transcript: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}',
            'timestamp': format_timestamp()
        }), 500


@app.route('/api/batch-score', methods=['POST'])
def batch_score():
    """
    Score multiple transcripts
    
    Request body:
    {
        "transcripts": ["text1", "text2", ...]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'transcripts' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing transcripts array in request body',
                'timestamp': format_timestamp()
            }), 400
        
        transcripts = data['transcripts']
        
        if not isinstance(transcripts, list):
            return jsonify({
                'success': False,
                'error': 'Transcripts must be an array',
                'timestamp': format_timestamp()
            }), 400
        
        # Initialize scoring engine
        init_scoring_engine()
        
        # Score each transcript
        results = []
        for i, transcript in enumerate(transcripts):
            validation = validate_transcript(transcript)
            if validation['valid']:
                try:
                    score_result = scoring_engine.score_transcript(transcript)
                    score_result['id'] = i + 1
                    score_result['score_category'] = get_score_category(score_result['overall_score'])
                    results.append(score_result)
                except Exception as e:
                    results.append({
                        'id': i + 1,
                        'error': str(e)
                    })
            else:
                results.append({
                    'id': i + 1,
                    'error': validation['message']
                })
        
        return jsonify({
            'success': True,
            'data': results,
            'count': len(results),
            'timestamp': format_timestamp()
        })
        
    except Exception as e:
        print(f"Error in batch scoring: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}',
            'timestamp': format_timestamp()
        }), 500


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'timestamp': format_timestamp()
    }), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'timestamp': format_timestamp()
    }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("Communication Skills Scoring System - Backend Server")
    print("=" * 60)
    print("\nStarting server...")
    print("This may take a moment on first run (downloading NLP models)")
    print("\nOnce started, open your browser to: http://localhost:5000")
    print("\nPress CTRL+C to stop the server")
    print("=" * 60)
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
