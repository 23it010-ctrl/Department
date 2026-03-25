"""
api_checker.py - External API Safety & Quality Checks (Mocked)
===============================================================
Simulates external API checks for content moderation:
  - Profanity/inappropriate content filter
  - Plagiarism detection (mocked)
  - Content safety check

In production, these would call real APIs like:
  - Google Perspective API (toxicity)
  - Copyscape API (plagiarism)
  - AWS Comprehend (sentiment/language)

For now, we use local rule-based checks to simulate API responses.
"""

import re


# ── Profanity / Inappropriate Words List (basic) ────────────────────────────
# NOTE: This is a minimal list for demonstration. Production systems should
# use comprehensive dictionaries or API-based solutions.
INAPPROPRIATE_WORDS = [
    'hate', 'stupid', 'idiot', 'fool', 'dumb', 'kill', 'attack',
    'abuse', 'violence', 'racist', 'sexist', 'harass'
]

# ── Known Plagiarism Patterns (mocked) ──────────────────────────────────────
# In production, you'd compare against existing content in the database
KNOWN_PLAGIARISM_PHRASES = [
    'lorem ipsum dolor sit amet',
    'the quick brown fox jumps over',
    'copy paste from internet',
    'this is a sample text for testing'
]


def check_content_safety(title, content):
    """
    Check content for inappropriate language (simulates Google Perspective API).
    
    Args:
        title (str): Content title
        content (str): Content body
    
    Returns:
        dict: {
            'safe': bool,
            'safety_score': float (0-100, higher = safer),
            'issues': list of issue descriptions,
            'api_name': str
        }
    """
    combined = f"{title} {content}".lower()
    issues = []
    score = 100

    # Check for inappropriate words
    found_words = [w for w in INAPPROPRIATE_WORDS if w in combined]
    if found_words:
        score -= min(50, len(found_words) * 12)
        issues.append(f"Inappropriate language detected: {', '.join(found_words[:3])}")

    # Check for excessive aggression markers
    exclamation_count = combined.count('!')
    if exclamation_count > 5:
        score -= 10
        issues.append("Aggressive tone detected (excessive exclamation marks)")

    # Check for ALL CAPS sections (more than 30 chars of caps)
    caps_sections = re.findall(r'[A-Z]{30,}', f"{title} {content}")
    if caps_sections:
        score -= 10
        issues.append("Large blocks of capital letters (shouting)")

    score = max(0, min(100, score))

    return {
        'safe': score >= 60,
        'safety_score': score,
        'issues': issues,
        'api_name': 'Content Safety Filter (Local)'
    }


def check_plagiarism(content):
    """
    Check for potential plagiarism (simulates Copyscape API).
    
    Args:
        content (str): Content body to check
    
    Returns:
        dict: {
            'is_original': bool,
            'originality_score': float (0-100),
            'matched_phrases': list,
            'api_name': str
        }
    """
    content_lower = (content or '').lower()
    matched = []

    for phrase in KNOWN_PLAGIARISM_PHRASES:
        if phrase in content_lower:
            matched.append(phrase)

    # Calculate originality score
    if matched:
        originality = max(10, 100 - (len(matched) * 30))
    else:
        originality = 95  # Default high originality (can't fully verify without real API)

    return {
        'is_original': len(matched) == 0,
        'originality_score': originality,
        'matched_phrases': matched,
        'api_name': 'Plagiarism Checker (Local)'
    }


def run_all_api_checks(title, content):
    """
    Run all external API checks and return a combined API score.
    
    Args:
        title (str): Content title
        content (str): Content body
    
    Returns:
        dict: {
            'api_score': float (0-100),
            'safety': dict (from check_content_safety),
            'plagiarism': dict (from check_plagiarism),
            'passed': bool
        }
    """
    safety = check_content_safety(title, content)
    plagiarism = check_plagiarism(content)

    # Combined API score: 60% safety + 40% originality
    api_score = (safety['safety_score'] * 0.6) + (plagiarism['originality_score'] * 0.4)
    api_score = round(api_score, 2)

    return {
        'api_score': api_score,
        'safety': safety,
        'plagiarism': plagiarism,
        'passed': safety['safe'] and plagiarism['is_original']
    }
