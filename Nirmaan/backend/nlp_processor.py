"""
NLP Processor Module
Handles natural language processing tasks including:
- Sentence embeddings
- Semantic similarity calculation
- Text preprocessing
"""
import re
from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

# Download required NLTK data (will only download if not present)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)


class NLPProcessor:
    """Handles NLP operations for transcript analysis"""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize NLP processor with sentence transformer model
        
        Args:
            model_name: Name of the sentence-transformers model to use
        """
        print(f"Loading NLP model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.stop_words = set(stopwords.words('english'))
        print("✓ NLP model loaded successfully")
    
    def preprocess_text(self, text: str) -> str:
        """
        Clean and preprocess text
        
        Args:
            text: Raw text input
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        return text.strip()
    
    def count_words(self, text: str) -> int:
        """
        Count words in text
        
        Args:
            text: Input text
            
        Returns:
            Number of words
        """
        words = word_tokenize(text.lower())
        return len([w for w in words if w.isalnum()])
    
    def extract_keywords(self, text: str, remove_stopwords: bool = True) -> List[str]:
        """
        Extract keywords from text
        
        Args:
            text: Input text
            remove_stopwords: Whether to remove common stopwords
            
        Returns:
            List of keywords
        """
        words = word_tokenize(text.lower())
        if remove_stopwords:
            keywords = [w for w in words if w.isalnum() and w not in self.stop_words]
        else:
            keywords = [w for w in words if w.isalnum()]
        return keywords
    
    def get_embedding(self, text: str) -> np.ndarray:
        """
        Get sentence embedding for text
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        return self.model.encode(text, convert_to_numpy=True)
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate cosine similarity between two texts
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        # Get embeddings
        emb1 = self.get_embedding(text1)
        emb2 = self.get_embedding(text2)
        
        # Calculate cosine similarity
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        
        # Ensure value is between 0 and 1
        return float(max(0.0, min(1.0, similarity)))
    
    def find_keyword_matches(self, text: str, keywords: List[str]) -> Dict[str, Any]:
        """
        Find which keywords from a list are present in text
        
        Args:
            text: Text to search in
            keywords: List of keywords to search for
            
        Returns:
            Dictionary with found and missing keywords
        """
        text_lower = text.lower()
        text_words = set(word_tokenize(text_lower))
        
        found = []
        missing = []
        
        for keyword in keywords:
            # Check both exact phrase and individual words
            if keyword.lower() in text_lower:
                found.append(keyword)
            elif keyword.lower() in text_words:
                found.append(keyword)
            else:
                missing.append(keyword)
        
        return {
            'found': found,
            'missing': missing,
            'match_rate': len(found) / len(keywords) if keywords else 0
        }
    
    def analyze_text_quality(self, text: str) -> Dict[str, Any]:
        """
        Analyze various quality metrics of text
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with quality metrics
        """
        sentences = sent_tokenize(text)
        words = word_tokenize(text)
        
        return {
            'word_count': len([w for w in words if w.isalnum()]),
            'sentence_count': len(sentences),
            'avg_sentence_length': len(words) / len(sentences) if sentences else 0,
            'unique_words': len(set(w.lower() for w in words if w.isalnum())),
            'vocabulary_richness': len(set(w.lower() for w in words if w.isalnum())) / len([w for w in words if w.isalnum()]) if words else 0
        }
    
    def extract_phrases(self, text: str, phrase_length: int = 2) -> List[str]:
        """
        Extract n-gram phrases from text
        
        Args:
            text: Input text
            phrase_length: Length of phrases (n-grams)
            
        Returns:
            List of phrases
        """
        words = word_tokenize(text.lower())
        words = [w for w in words if w.isalnum()]
        
        phrases = []
        for i in range(len(words) - phrase_length + 1):
            phrase = ' '.join(words[i:i+phrase_length])
            phrases.append(phrase)
        
        return phrases
    
    def score_semantic_relevance(self, text: str, reference_texts: List[str]) -> float:
        """
        Score how semantically relevant text is to a set of references
        
        Args:
            text: Text to evaluate
            reference_texts: List of reference texts to compare against
            
        Returns:
            Average similarity score (0-1)
        """
        if not reference_texts:
            return 0.0
        
        similarities = [self.calculate_similarity(text, ref) for ref in reference_texts]
        return float(np.mean(similarities))


# Singleton instance
_nlp_processor = None

def get_nlp_processor() -> NLPProcessor:
    """Get or create singleton NLP processor instance"""
    global _nlp_processor
    if _nlp_processor is None:
        _nlp_processor = NLPProcessor()
    return _nlp_processor
