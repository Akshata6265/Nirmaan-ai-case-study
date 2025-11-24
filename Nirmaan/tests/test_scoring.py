"""
Unit tests for the scoring system
Run with: python -m pytest tests/test_scoring.py
Or: python tests/test_scoring.py
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import unittest
from backend.scoring_engine import ScoringEngine
from backend.nlp_processor import NLPProcessor
from backend.utils import (
    parse_keywords, normalize_score, calculate_weighted_average,
    validate_transcript, get_score_category
)


class TestNLPProcessor(unittest.TestCase):
    """Test NLP processing functions"""
    
    @classmethod
    def setUpClass(cls):
        cls.nlp = NLPProcessor()
    
    def test_preprocess_text(self):
        """Test text preprocessing"""
        text = "  Hello   world!  Extra   spaces.  "
        result = self.nlp.preprocess_text(text)
        self.assertEqual(result, "Hello world! Extra spaces.")
    
    def test_count_words(self):
        """Test word counting"""
        text = "Hello world, this is a test!"
        count = self.nlp.count_words(text)
        self.assertEqual(count, 6)
    
    def test_calculate_similarity(self):
        """Test semantic similarity calculation"""
        text1 = "I love programming in Python"
        text2 = "I enjoy coding with Python"
        similarity = self.nlp.calculate_similarity(text1, text2)
        self.assertGreater(similarity, 0.5)
        self.assertLessEqual(similarity, 1.0)
    
    def test_find_keyword_matches(self):
        """Test keyword matching"""
        text = "Hello my name is John and I love programming"
        keywords = ["hello", "name", "programming", "missing"]
        result = self.nlp.find_keyword_matches(text, keywords)
        
        self.assertIn("hello", result['found'])
        self.assertIn("name", result['found'])
        self.assertIn("programming", result['found'])
        self.assertIn("missing", result['missing'])


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions"""
    
    def test_parse_keywords(self):
        """Test keyword parsing"""
        keyword_string = "hello, world, test, python"
        result = parse_keywords(keyword_string)
        self.assertEqual(len(result), 4)
        self.assertIn("hello", result)
        self.assertIn("python", result)
    
    def test_normalize_score(self):
        """Test score normalization"""
        self.assertEqual(normalize_score(50), 50)
        self.assertEqual(normalize_score(-10), 0)
        self.assertEqual(normalize_score(150), 100)
    
    def test_calculate_weighted_average(self):
        """Test weighted average calculation"""
        scores = [80, 90, 70]
        weights = [2, 3, 1]
        avg = calculate_weighted_average(scores, weights)
        expected = (80*2 + 90*3 + 70*1) / (2+3+1)
        self.assertAlmostEqual(avg, expected, places=2)
    
    def test_validate_transcript_valid(self):
        """Test transcript validation with valid input"""
        transcript = "This is a valid transcript with more than ten words in it."
        result = validate_transcript(transcript)
        self.assertTrue(result['valid'])
    
    def test_validate_transcript_too_short(self):
        """Test transcript validation with short input"""
        transcript = "Too short"
        result = validate_transcript(transcript)
        self.assertFalse(result['valid'])
    
    def test_get_score_category(self):
        """Test score categorization"""
        self.assertEqual(get_score_category(95), 'Excellent')
        self.assertEqual(get_score_category(85), 'Very Good')
        self.assertEqual(get_score_category(75), 'Good')
        self.assertEqual(get_score_category(45), 'Needs Improvement')


class TestScoringEngine(unittest.TestCase):
    """Test scoring engine"""
    
    @classmethod
    def setUpClass(cls):
        cls.engine = ScoringEngine()
    
    def test_score_transcript_basic(self):
        """Test basic transcript scoring"""
        transcript = """
        Hello everyone! My name is Sarah Johnson, and I'm excited to introduce myself.
        I graduated from MIT with a degree in Computer Science. I have strong skills in
        Python, machine learning, and data analysis. My goal is to work as a software engineer
        where I can apply my knowledge to solve real-world problems. I'm passionate about
        technology and innovation. Thank you for your time!
        """
        
        result = self.engine.score_transcript(transcript)
        
        # Check that result has expected structure
        self.assertIn('overall_score', result)
        self.assertIn('criteria_scores', result)
        self.assertIn('word_count', result)
        
        # Check score is in valid range
        self.assertGreaterEqual(result['overall_score'], 0)
        self.assertLessEqual(result['overall_score'], 100)
        
        # Check criteria scores
        self.assertGreater(len(result['criteria_scores']), 0)
        
        for criterion in result['criteria_scores']:
            self.assertIn('criterion', criterion)
            self.assertIn('score', criterion)
            self.assertIn('weight', criterion)
            self.assertIn('feedback', criterion)
    
    def test_score_transcript_excellent(self):
        """Test scoring of excellent transcript"""
        transcript = """
        Good morning everyone! My name is Alex Thompson, and it's a pleasure to introduce myself today.
        I recently graduated with honors from Stanford University with a Bachelor's degree in Computer Science,
        specializing in Artificial Intelligence and Machine Learning. During my time at Stanford, I maintained
        a 3.9 GPA while actively participating in research projects focused on natural language processing.
        
        I have extensive experience with Python, TensorFlow, PyTorch, and various cloud technologies including
        AWS and Google Cloud Platform. I'm proficient in full-stack development, with strong skills in JavaScript,
        React, Node.js, and SQL databases. Additionally, I have hands-on experience with agile methodologies,
        version control systems like Git, and CI/CD pipelines.
        
        My career goal is to become a leading AI engineer where I can develop innovative solutions that make a
        positive impact on society. I'm particularly passionate about using machine learning for healthcare applications
        and environmental sustainability. I aspire to work on cutting-edge projects that push the boundaries of what's
        possible with AI while ensuring ethical considerations are at the forefront.
        
        Beyond technical skills, I'm confident in my ability to communicate complex ideas clearly, work effectively
        in teams, and adapt quickly to new challenges. I'm enthusiastic about continuous learning and staying updated
        with the latest technological advancements. I believe in the power of collaboration and am excited about
        opportunities to contribute to meaningful projects.
        
        Thank you very much for taking the time to listen to my introduction. I'm looking forward to connecting
        with you all and exploring how I can contribute to your organization. Please feel free to reach out if you
        have any questions or would like to discuss potential opportunities!
        """
        
        result = self.engine.score_transcript(transcript)
        
        # Excellent transcript should score high
        self.assertGreater(result['overall_score'], 70)
        
        # Should find many keywords
        for criterion in result['criteria_scores']:
            if len(criterion['keywords_found']) > 0:
                self.assertGreater(len(criterion['keywords_found']), 0)
    
    def test_score_transcript_poor(self):
        """Test scoring of poor transcript"""
        transcript = "Hi. I'm John. I studied computer science. Looking for a job."
        
        result = self.engine.score_transcript(transcript)
        
        # Poor transcript should score lower
        self.assertLess(result['overall_score'], 70)
    
    def test_get_rubric_info(self):
        """Test getting rubric information"""
        info = self.engine.get_rubric_info()
        
        self.assertIn('criteria_count', info)
        self.assertIn('total_weight', info)
        self.assertIn('criteria', info)
        
        self.assertGreater(info['criteria_count'], 0)
        self.assertGreater(info['total_weight'], 0)


def run_tests():
    """Run all tests"""
    print("=" * 60)
    print("Running Communication Skills Scoring System Tests")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestNLPProcessor))
    suite.addTests(loader.loadTestsFromTestCase(TestUtilityFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestScoringEngine))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success: {result.wasSuccessful()}")
    print("=" * 60)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
