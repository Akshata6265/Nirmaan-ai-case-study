"""
Utility functions for the scoring system
"""
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional


def load_rubric(file_path: str = None) -> pd.DataFrame:
    """
    Load rubric data from Excel file
    
    Args:
        file_path: Path to Excel file (default: data/Case study for interns.xlsx)
        
    Returns:
        DataFrame with rubric data
    """
    if file_path is None:
        file_path = Path(__file__).parent.parent / "data" / "Case study for interns.xlsx"
    
    try:
        df = pd.read_excel(file_path, sheet_name='Rubric')
        return df
    except FileNotFoundError:
        raise FileNotFoundError(f"Rubric file not found at {file_path}")
    except Exception as e:
        raise Exception(f"Error loading rubric: {str(e)}")


def load_sample_transcripts(file_path: str = None) -> pd.DataFrame:
    """
    Load sample transcripts from Excel file
    
    Args:
        file_path: Path to Excel file (default: data/Case study for interns.xlsx)
        
    Returns:
        DataFrame with transcript data
    """
    if file_path is None:
        file_path = Path(__file__).parent.parent / "data" / "Case study for interns.xlsx"
    
    try:
        df = pd.read_excel(file_path, sheet_name='Transcripts')
        return df
    except FileNotFoundError:
        raise FileNotFoundError(f"Transcripts file not found at {file_path}")
    except Exception as e:
        raise Exception(f"Error loading transcripts: {str(e)}")


def parse_keywords(keyword_string: str) -> List[str]:
    """
    Parse comma-separated keyword string into list
    
    Args:
        keyword_string: Comma-separated keywords
        
    Returns:
        List of individual keywords
    """
    if pd.isna(keyword_string) or not keyword_string:
        return []
    
    keywords = [k.strip() for k in str(keyword_string).split(',')]
    return [k for k in keywords if k]


def normalize_score(score: float, min_val: float = 0, max_val: float = 100) -> float:
    """
    Normalize score to be within min and max range
    
    Args:
        score: Raw score
        min_val: Minimum value
        max_val: Maximum value
        
    Returns:
        Normalized score
    """
    return max(min_val, min(max_val, score))


def calculate_weighted_average(scores: List[float], weights: List[float]) -> float:
    """
    Calculate weighted average of scores
    
    Args:
        scores: List of scores
        weights: List of weights (same length as scores)
        
    Returns:
        Weighted average
    """
    if not scores or not weights or len(scores) != len(weights):
        return 0.0
    
    total_weight = sum(weights)
    if total_weight == 0:
        return 0.0
    
    weighted_sum = sum(s * w for s, w in zip(scores, weights))
    return weighted_sum / total_weight


def format_feedback(criterion: str, score: float, keywords_found: List[str], 
                    keywords_missing: List[str], semantic_similarity: float,
                    word_count: int, min_words: int, max_words: int) -> str:
    """
    Generate human-readable feedback for a criterion
    
    Args:
        criterion: Criterion name
        score: Score for this criterion (0-100)
        keywords_found: List of keywords found
        keywords_missing: List of keywords missing
        semantic_similarity: Semantic similarity score (0-1)
        word_count: Word count for this section
        min_words: Minimum expected words
        max_words: Maximum expected words
        
    Returns:
        Formatted feedback string
    """
    feedback_parts = []
    
    # Overall assessment
    if score >= 90:
        feedback_parts.append("Excellent performance.")
    elif score >= 75:
        feedback_parts.append("Good performance.")
    elif score >= 60:
        feedback_parts.append("Satisfactory performance.")
    elif score >= 40:
        feedback_parts.append("Needs improvement.")
    else:
        feedback_parts.append("Requires significant improvement.")
    
    # Keyword feedback
    if keywords_found:
        if len(keywords_found) > 3:
            feedback_parts.append(f"Strong keyword coverage with terms like '{keywords_found[0]}', '{keywords_found[1]}', and {len(keywords_found)-2} more.")
        else:
            feedback_parts.append(f"Found keywords: {', '.join(keywords_found[:3])}.")
    
    if keywords_missing and len(keywords_missing) <= 3:
        feedback_parts.append(f"Consider including: {', '.join(keywords_missing)}.")
    elif keywords_missing:
        feedback_parts.append(f"Missing {len(keywords_missing)} suggested keywords.")
    
    # Semantic similarity feedback
    if semantic_similarity >= 0.75:
        feedback_parts.append("Strong semantic alignment with criterion.")
    elif semantic_similarity >= 0.5:
        feedback_parts.append("Moderate semantic relevance.")
    elif semantic_similarity < 0.5:
        feedback_parts.append("Consider addressing this aspect more directly.")
    
    # Word count feedback
    if min_words > 0 and max_words < 999:
        if word_count < min_words:
            feedback_parts.append(f"Content is brief ({word_count} words). Consider expanding (recommended: {min_words}+ words).")
        elif word_count > max_words:
            feedback_parts.append(f"Content is lengthy ({word_count} words). Consider being more concise (recommended: under {max_words} words).")
        else:
            feedback_parts.append(f"Good length ({word_count} words).")
    
    return " ".join(feedback_parts)


def get_word_count_status(word_count: int, min_words: int, max_words: int) -> str:
    """
    Determine word count status
    
    Args:
        word_count: Actual word count
        min_words: Minimum expected
        max_words: Maximum expected
        
    Returns:
        Status string: 'too_short', 'within_range', 'too_long', or 'no_limit'
    """
    if min_words == 0 and max_words >= 999:
        return 'no_limit'
    
    if word_count < min_words:
        return 'too_short'
    elif word_count > max_words:
        return 'too_long'
    else:
        return 'within_range'


def validate_transcript(transcript: str) -> Dict[str, Any]:
    """
    Validate transcript input
    
    Args:
        transcript: Input transcript text
        
    Returns:
        Dictionary with validation result and message
    """
    if not transcript or not transcript.strip():
        return {
            'valid': False,
            'message': 'Transcript is empty'
        }
    
    word_count = len(transcript.split())
    
    if word_count < 10:
        return {
            'valid': False,
            'message': f'Transcript too short ({word_count} words). Minimum 10 words required.'
        }
    
    if word_count > 5000:
        return {
            'valid': False,
            'message': f'Transcript too long ({word_count} words). Maximum 5000 words allowed.'
        }
    
    return {
        'valid': True,
        'message': 'Transcript is valid',
        'word_count': word_count
    }


def get_score_category(score: float) -> str:
    """
    Categorize score into performance level
    
    Args:
        score: Score value (0-100)
        
    Returns:
        Category string
    """
    if score >= 90:
        return 'Excellent'
    elif score >= 80:
        return 'Very Good'
    elif score >= 70:
        return 'Good'
    elif score >= 60:
        return 'Satisfactory'
    elif score >= 50:
        return 'Fair'
    else:
        return 'Needs Improvement'


def format_timestamp() -> str:
    """
    Get current timestamp in ISO format
    
    Returns:
        ISO formatted timestamp string
    """
    from datetime import datetime
    return datetime.utcnow().isoformat() + 'Z'
