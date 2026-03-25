"""
content_analyzer.py - Content Feature Extraction & Analysis
============================================================
Extracts features from user-submitted content (notes, achievements, news tips)
and generates a quality score based on text analysis.

Features checked:
  - Content length (too short = low quality)
  - Presence of forbidden/spam words
  - Proper capitalization
  - Duplicate detection
  - File type validation (for uploads)
"""

import re
import os

# ── Spam / Forbidden Words List ──────────────────────────────────────────────
SPAM_KEYWORDS = [
    'buy now', 'click here', 'free money', 'winner', 'congratulations',
    'act now', 'limited time', 'subscribe now', 'earn money', 'make money',
    'casino', 'lottery', 'prize', 'discount', 'cheap', 'viagra',
    'bitcoin', 'crypto scam', 'investment opportunity'
]

# ── Allowed File Extensions for Uploads ──────────────────────────────────────
ALLOWED_EXTENSIONS = {
    'notes': {'.pdf', '.doc', '.docx', '.ppt', '.pptx', '.txt', '.xlsx'},
    'achievements': {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.pdf'},
    'news': {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
}


def analyze_text_content(title, content, content_type='general'):
    """
    Analyze text content and return a quality score (0-100) with detailed flags.
    
    Args:
        title (str): Title of the submission
        content (str): Body/description text
        content_type (str): Type of content ('notes', 'achievements', 'news')
    
    Returns:
        dict: {
            'score': int (0-100),
            'flags': list of warning strings,
            'is_spam': bool,
            'quality_level': str ('high', 'medium', 'low')
        }
    """
    score = 100  # Start with perfect score, deduct for issues
    flags = []

    # ── 1. Title Checks ──────────────────────────────────────────────────────
    if not title or len(title.strip()) < 5:
        score -= 25
        flags.append("Title is too short (minimum 5 characters)")
    elif len(title.strip()) > 200:
        score -= 10
        flags.append("Title is excessively long")

    # ── 2. Content Length Checks ─────────────────────────────────────────────
    content_text = content or ''
    word_count = len(content_text.split())
    
    if word_count < 10:
        score -= 30
        flags.append(f"Content too short ({word_count} words, minimum 10 recommended)")
    elif word_count < 25:
        score -= 15
        flags.append(f"Content is brief ({word_count} words)")

    # ── 3. Spam Detection ────────────────────────────────────────────────────
    combined_text = f"{title} {content_text}".lower()
    spam_found = [kw for kw in SPAM_KEYWORDS if kw in combined_text]
    
    if spam_found:
        score -= min(40, len(spam_found) * 15)  # Cap penalty at 40
        flags.append(f"Spam keywords detected: {', '.join(spam_found[:3])}")

    # ── 4. Excessive Capitalization / Shouting ───────────────────────────────
    if title and len(title) > 10:
        upper_ratio = sum(1 for c in title if c.isupper()) / len(title)
        if upper_ratio > 0.7:
            score -= 10
            flags.append("Excessive use of capital letters in title")

    # ── 5. Repetitive Characters ─────────────────────────────────────────────
    if re.search(r'(.)\1{4,}', combined_text):
        score -= 15
        flags.append("Repetitive characters detected (e.g., 'aaaaaa')")

    # ── 6. URL/Link Spam ─────────────────────────────────────────────────────
    url_count = len(re.findall(r'https?://\S+', combined_text))
    if url_count > 3:
        score -= 15
        flags.append(f"Too many URLs in content ({url_count} links)")

    # ── 7. Special Character Overuse ─────────────────────────────────────────
    special_ratio = sum(1 for c in combined_text if c in '!@#$%^&*') / max(len(combined_text), 1)
    if special_ratio > 0.1:
        score -= 10
        flags.append("Excessive use of special characters")

    # Ensure score stays within bounds
    score = max(0, min(100, score))

    # Determine quality level
    if score >= 80:
        quality_level = 'high'
    elif score >= 50:
        quality_level = 'medium'
    else:
        quality_level = 'low'

    return {
        'score': score,
        'flags': flags,
        'is_spam': len(spam_found) > 0,
        'quality_level': quality_level,
        'word_count': word_count
    }


def validate_file_upload(filename, content_type='notes'):
    """
    Validate uploaded file by checking extension.
    
    Args:
        filename (str): Name of the uploaded file
        content_type (str): Type of content ('notes', 'achievements', 'news')
    
    Returns:
        dict: {'valid': bool, 'reason': str}
    """
    if not filename:
        return {'valid': False, 'reason': 'No file provided'}

    ext = os.path.splitext(filename)[1].lower()
    allowed = ALLOWED_EXTENSIONS.get(content_type, ALLOWED_EXTENSIONS['notes'])

    if ext not in allowed:
        return {
            'valid': False,
            'reason': f"File type '{ext}' not allowed. Accepted: {', '.join(sorted(allowed))}"
        }

    return {'valid': True, 'reason': 'File type accepted'}


def check_duplicate(title, collection_func, content_type='general'):
    """
    Check if content with a similar title already exists.
    
    Args:
        title (str): Title to check
        collection_func: Function that returns the MongoDB collection
        content_type (str): Used for messaging
    
    Returns:
        dict: {'is_duplicate': bool, 'existing_title': str or None}
    """
    col = collection_func()
    if col is None:
        return {'is_duplicate': False, 'existing_title': None}

    # Check for exact match (case-insensitive via normalized comparison)
    normalized_title = title.strip().lower()
    
    all_docs = list(col.find())
    for doc in all_docs:
        existing_title = doc.get('title', '').strip().lower()
        if existing_title == normalized_title:
            return {
                'is_duplicate': True,
                'existing_title': doc.get('title', '')
            }

    return {'is_duplicate': False, 'existing_title': None}
