"""
ml_engine.py - Machine Learning Content Quality Prediction
============================================================
Uses a simple scoring model (simulated ML) to predict content quality.
In production, this would use a trained Random Forest or Logistic Regression model.

For this implementation, we use a rule-based scoring system that mimics
ML predictions based on extracted features — making it beginner-friendly
and easy to understand without needing scikit-learn installed.

Features used for prediction:
  - Word count of content
  - Title length
  - Has proper structure (paragraphs, punctuation)
  - Sentiment indicators
  - Content relevance to department context
"""

import re
import math

# ── Department-Related Keywords (positive signals) ───────────────────────────
DEPARTMENT_KEYWORDS = [
    'computer', 'science', 'engineering', 'research', 'project', 'semester',
    'exam', 'lab', 'faculty', 'student', 'lecture', 'assignment', 'grade',
    'placement', 'internship', 'hackathon', 'workshop', 'seminar',
    'certificate', 'achievement', 'award', 'publication', 'paper',
    'algorithm', 'programming', 'database', 'network', 'software',
    'machine learning', 'artificial intelligence', 'data structure',
    'operating system', 'web development', 'cyber security', 'cloud',
    'department', 'university', 'college', 'campus', 'academic',
    'syllabus', 'curriculum', 'course', 'module', 'class', 'tutorial',
    'notes', 'study', 'education', 'learning', 'teaching'
]


def extract_features(title, content):
    """
    Extract numerical features from content for ML prediction.
    
    Args:
        title (str): Content title
        content (str): Content body
    
    Returns:
        dict: Dictionary of extracted features with float values
    """
    title = title or ''
    content = content or ''
    combined = f"{title} {content}".lower()
    words = combined.split()
    sentences = re.split(r'[.!?]+', content)

    features = {}

    # Feature 1: Word count (normalized to 0-1 scale, optimal around 50-200 words)
    word_count = len(words)
    features['word_count_score'] = min(1.0, word_count / 100.0)

    # Feature 2: Title quality (length 10-80 chars is ideal)
    title_len = len(title.strip())
    if 10 <= title_len <= 80:
        features['title_quality'] = 1.0
    elif 5 <= title_len < 10 or 80 < title_len <= 120:
        features['title_quality'] = 0.6
    else:
        features['title_quality'] = 0.2

    # Feature 3: Sentence structure (avg words per sentence)
    valid_sentences = [s.strip() for s in sentences if len(s.strip()) > 3]
    if valid_sentences:
        avg_words = sum(len(s.split()) for s in valid_sentences) / len(valid_sentences)
        # Optimal: 10-20 words per sentence
        if 8 <= avg_words <= 25:
            features['sentence_structure'] = 1.0
        elif 5 <= avg_words < 8 or 25 < avg_words <= 35:
            features['sentence_structure'] = 0.6
        else:
            features['sentence_structure'] = 0.3
    else:
        features['sentence_structure'] = 0.1

    # Feature 4: Department relevance
    keyword_matches = sum(1 for kw in DEPARTMENT_KEYWORDS if kw in combined)
    features['relevance_score'] = min(1.0, keyword_matches / 5.0)

    # Feature 5: Punctuation usage (proper writing)
    punctuation_count = sum(1 for c in content if c in '.,:;!?')
    features['punctuation_score'] = min(1.0, punctuation_count / max(1, word_count / 10))

    # Feature 6: Capitalization (proper sentence starts)
    proper_caps = sum(1 for s in valid_sentences if s and s[0].isupper())
    features['capitalization_score'] = proper_caps / max(1, len(valid_sentences))

    return features


def predict_quality(title, content):
    """
    Predict content quality using a weighted scoring model.
    Simulates an ML prediction (like Random Forest output).
    
    Args:
        title (str): Content title
        content (str): Content body text
    
    Returns:
        dict: {
            'ml_score': float (0-100),
            'confidence': float (0-1),
            'prediction': str ('approved', 'review', 'rejected'),
            'features': dict of extracted features
        }
    """
    features = extract_features(title, content)

    # ── Weighted scoring (simulates trained model weights) ───────────────────
    weights = {
        'word_count_score': 0.20,      # 20% weight - content length matters
        'title_quality': 0.15,          # 15% weight - good titles important
        'sentence_structure': 0.20,     # 20% weight - readability
        'relevance_score': 0.25,        # 25% weight - must be relevant
        'punctuation_score': 0.10,      # 10% weight - writing quality
        'capitalization_score': 0.10    # 10% weight - proper formatting
    }

    # Calculate weighted sum
    raw_score = sum(features[k] * weights[k] for k in weights)
    
    # Scale to 0-100
    ml_score = round(raw_score * 100, 2)
    
    # Confidence is higher when features are more uniform (less variance)
    feature_values = list(features.values())
    mean_val = sum(feature_values) / len(feature_values)
    variance = sum((v - mean_val) ** 2 for v in feature_values) / len(feature_values)
    confidence = round(1.0 - min(1.0, math.sqrt(variance)), 2)

    # Determine prediction category
    if ml_score >= 70:
        prediction = 'approved'
    elif ml_score >= 40:
        prediction = 'review'
    else:
        prediction = 'rejected'

    return {
        'ml_score': ml_score,
        'confidence': confidence,
        'prediction': prediction,
        'features': features
    }
