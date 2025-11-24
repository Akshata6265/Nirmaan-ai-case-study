"""
Scoring Engine Module
Core logic for scoring transcripts based on rubric criteria
Combines rule-based, NLP-based, and rubric-driven approaches
"""
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from nlp_processor import get_nlp_processor
from utils import (
    load_rubric, parse_keywords, normalize_score, 
    calculate_weighted_average, format_feedback, get_word_count_status
)


class ScoringEngine:
    """Main scoring engine for transcript analysis"""
    
    def __init__(self):
        """Initialize scoring engine with NLP processor and rubric"""
        self.nlp = get_nlp_processor()
        self.rubric = load_rubric()
        print(f"✓ Scoring engine initialized with {len(self.rubric)} criteria")
    
    def score_transcript(self, transcript: str) -> Dict[str, Any]:
        """
        Score a transcript based on loaded rubric
        
        Args:
            transcript: Text of the transcript to score
            
        Returns:
            Dictionary with overall score and detailed per-criterion results
        """
        # Preprocess transcript
        transcript = self.nlp.preprocess_text(transcript)
        transcript_lower = transcript.lower()
        
        # Get overall text quality metrics
        text_quality = self.nlp.analyze_text_quality(transcript)
        
        # Score each criterion
        criteria_scores = []
        
        for _, row in self.rubric.iterrows():
            criterion_result = self._score_criterion(
                transcript=transcript,
                transcript_lower=transcript_lower,
                criterion_name=row['Criterion'],
                description=row['Description'],
                keywords=parse_keywords(row['Keywords']),
                weight=row['Weight'],
                min_words=row.get('Min_Words', 0),
                max_words=row.get('Max_Words', 999)
            )
            criteria_scores.append(criterion_result)
        
        # Calculate overall score
        scores = [c['score'] for c in criteria_scores]
        weights = [c['weight'] for c in criteria_scores]
        overall_score = calculate_weighted_average(scores, weights)
        
        # Compile final result
        result = {
            'overall_score': round(overall_score, 2),
            'word_count': text_quality['word_count'],
            'criteria_scores': criteria_scores,
            'text_quality': text_quality
        }
        
        return result
    
    def _score_criterion(self, transcript: str, transcript_lower: str, 
                        criterion_name: str, description: str, 
                        keywords: List[str], weight: float,
                        min_words: int = 0, max_words: int = 999) -> Dict[str, Any]:
        """
        Score a single criterion using multiple approaches
        
        Args:
            transcript: Full transcript text
            transcript_lower: Lowercase version for matching
            criterion_name: Name of the criterion
            description: Description of what the criterion measures
            keywords: List of keywords to check
            weight: Weight of this criterion
            min_words: Minimum expected words for this criterion
            max_words: Maximum expected words for this criterion
            
        Returns:
            Dictionary with criterion score and details
        """
        # 1. Rule-Based Scoring (40%)
        rule_score = self._rule_based_score(transcript_lower, keywords, min_words, max_words)
        
        # 2. NLP-Based Semantic Scoring (40%)
        semantic_score, similarity = self._semantic_score(transcript, description)
        
        # 3. Rubric-Driven Scoring (20%) - based on keyword density and coverage
        rubric_score = self._rubric_driven_score(transcript_lower, keywords)
        
        # Combine scores
        combined_score = (rule_score * 0.4) + (semantic_score * 0.4) + (rubric_score * 0.2)
        final_score = normalize_score(combined_score)
        
        # Find keyword matches
        keyword_matches = self.nlp.find_keyword_matches(transcript, keywords)
        
        # Get word count status
        word_count = self.nlp.count_words(transcript)
        word_count_status = get_word_count_status(word_count, min_words, max_words)
        
        # Generate feedback
        feedback = format_feedback(
            criterion=criterion_name,
            score=final_score,
            keywords_found=keyword_matches['found'],
            keywords_missing=keyword_matches['missing'],
            semantic_similarity=similarity,
            word_count=word_count,
            min_words=min_words,
            max_words=max_words
        )
        
        return {
            'criterion': criterion_name,
            'score': round(final_score, 2),
            'weight': weight,
            'keywords_found': keyword_matches['found'],
            'keywords_missing': keyword_matches['missing'],
            'keyword_match_rate': round(keyword_matches['match_rate'], 2),
            'semantic_similarity': round(similarity, 2),
            'word_count_status': word_count_status,
            'feedback': feedback,
            'score_breakdown': {
                'rule_based': round(rule_score, 2),
                'semantic': round(semantic_score, 2),
                'rubric_driven': round(rubric_score, 2)
            }
        }
    
    def _rule_based_score(self, transcript_lower: str, keywords: List[str], 
                         min_words: int, max_words: int) -> float:
        """
        Calculate score based on rules and exact matches
        
        Args:
            transcript_lower: Lowercase transcript
            keywords: Keywords to check
            min_words: Minimum word requirement
            max_words: Maximum word requirement
            
        Returns:
            Rule-based score (0-100)
        """
        score = 0.0
        
        # Keyword presence (70% of rule score)
        if keywords:
            matches = sum(1 for kw in keywords if kw.lower() in transcript_lower)
            keyword_score = (matches / len(keywords)) * 70
            score += keyword_score
        else:
            score += 35  # Base score if no keywords defined
        
        # Word count compliance (30% of rule score)
        word_count = len(transcript_lower.split())
        if min_words > 0 or max_words < 999:
            if min_words <= word_count <= max_words:
                score += 30
            elif word_count < min_words:
                # Partial credit based on how close to minimum
                ratio = word_count / min_words if min_words > 0 else 1
                score += 30 * min(ratio, 1.0)
            else:  # word_count > max_words
                # Slight penalty for being too verbose
                score += 20
        else:
            score += 30  # Full credit if no limits
        
        return normalize_score(score)
    
    def _semantic_score(self, transcript: str, description: str) -> tuple:
        """
        Calculate semantic similarity score using NLP
        
        Args:
            transcript: Full transcript
            description: Criterion description
            
        Returns:
            Tuple of (score, similarity) where score is 0-100 and similarity is 0-1
        """
        # Calculate semantic similarity
        similarity = self.nlp.calculate_similarity(transcript, description)
        
        # Convert similarity (0-1) to score (0-100) with a curve
        # We use a non-linear scaling to reward high similarity more
        if similarity >= 0.7:
            score = 70 + (similarity - 0.7) * 100  # 70-100 range for high similarity
        elif similarity >= 0.4:
            score = 40 + (similarity - 0.4) * 100  # 40-70 range for medium similarity
        else:
            score = similarity * 100  # 0-40 range for low similarity
        
        return normalize_score(score), similarity
    
    def _rubric_driven_score(self, transcript_lower: str, keywords: List[str]) -> float:
        """
        Calculate score based on rubric-specific criteria
        This includes keyword density and distribution
        
        Args:
            transcript_lower: Lowercase transcript
            keywords: List of keywords
            
        Returns:
            Rubric-driven score (0-100)
        """
        if not keywords:
            return 50.0  # Neutral score if no keywords
        
        score = 0.0
        
        # Count total keyword occurrences (not just unique)
        total_occurrences = sum(transcript_lower.count(kw.lower()) for kw in keywords)
        
        # Keyword density (50% of rubric score)
        # More occurrences = better, but with diminishing returns
        if total_occurrences > 0:
            density_score = min(50, total_occurrences * 10)  # Cap at 50
            score += density_score
        
        # Keyword coverage (50% of rubric score)
        # What percentage of keywords appear at least once
        present_keywords = sum(1 for kw in keywords if kw.lower() in transcript_lower)
        coverage = present_keywords / len(keywords)
        score += coverage * 50
        
        return normalize_score(score)
    
    def get_rubric_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded rubric
        
        Returns:
            Dictionary with rubric information
        """
        return {
            'criteria_count': len(self.rubric),
            'total_weight': self.rubric['Weight'].sum(),
            'criteria': [
                {
                    'name': row['Criterion'],
                    'weight': row['Weight'],
                    'keyword_count': len(parse_keywords(row['Keywords']))
                }
                for _, row in self.rubric.iterrows()
            ]
        }


# Singleton instance
_scoring_engine = None

def get_scoring_engine() -> ScoringEngine:
    """Get or create singleton scoring engine instance"""
    global _scoring_engine
    if _scoring_engine is None:
        _scoring_engine = ScoringEngine()
    return _scoring_engine
