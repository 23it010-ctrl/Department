"""
validation_engine.py - Main Content Validation Orchestrator
=============================================================
This is the CORE ENGINE that ties together all validation services.

When a user submits content (notes, achievements, news tips), this engine:
  1. Runs content analysis (content_analyzer.py)
  2. Runs ML quality prediction (ml_engine.py)
  3. Runs external API checks (api_checker.py)
  4. Combines all scores into a final confidence score

Scoring Formula:
  confidence_score = (ml_score * 0.5) + (api_score * 0.3) + (content_score * 0.2)

Decision Rules:
  >= 80  → Auto-approve and publish directly
  50-79  → Send to community voting/admin review
  < 50   → Auto-reject as low quality / spam
"""

from services.content_analyzer import analyze_text_content, validate_file_upload, check_duplicate
from services.ml_engine import predict_quality
from services.api_checker import run_all_api_checks


def validate_submission(title, content, content_type='general',
                        filename=None, collection_func=None):
    """
    Main validation pipeline for any content submission.
    
    This function orchestrates all checks and produces a final decision.
    
    Args:
        title (str): Title of the submission
        content (str): Body/description text
        content_type (str): Type ('notes', 'achievements', 'news')
        filename (str): Uploaded filename (optional)
        collection_func (callable): Function that returns DB collection (for duplicate check)
    
    Returns:
        dict: {
            'status': str ('approved', 'pending', 'rejected'),
            'confidence_score': float (0-100),
            'decision_reason': str,
            'breakdown': {
                'content_analysis': dict,
                'ml_prediction': dict,
                'api_checks': dict,
                'file_validation': dict or None,
                'duplicate_check': dict or None
            },
            'flags': list of all warning flags
        }
    
    Example Response:
        {
            'status': 'approved',
            'confidence_score': 87.5,
            'decision_reason': 'High quality content - auto-approved',
            'breakdown': { ... },
            'flags': []
        }
    """

    all_flags = []

    # ── Step 1: Content Analysis ─────────────────────────────────────────────
    content_result = analyze_text_content(title, content, content_type)
    all_flags.extend(content_result.get('flags', []))

    # ── Step 2: ML Quality Prediction ────────────────────────────────────────
    ml_result = predict_quality(title, content)

    # ── Step 3: External API Checks ──────────────────────────────────────────
    api_result = run_all_api_checks(title, content)
    # Add API issues to flags
    all_flags.extend(api_result.get('safety', {}).get('issues', []))
    if not api_result.get('plagiarism', {}).get('is_original', True):
        all_flags.append("Potential plagiarism detected")

    # ── Step 4: File Validation (if applicable) ──────────────────────────────
    file_result = None
    if filename:
        file_result = validate_file_upload(filename, content_type)
        if not file_result['valid']:
            all_flags.append(f"File issue: {file_result['reason']}")

    # ── Step 5: Duplicate Check (if collection provided) ─────────────────────
    duplicate_result = None
    if collection_func and title:
        duplicate_result = check_duplicate(title, collection_func, content_type)
        if duplicate_result['is_duplicate']:
            all_flags.append(f"Duplicate detected: '{duplicate_result['existing_title']}'")

    # ── Step 6: Calculate Final Confidence Score ─────────────────────────────
    # Formula: (ml_score * 0.5) + (api_score * 0.3) + (content_score * 0.2)
    ml_score = ml_result['ml_score']
    api_score = api_result['api_score']
    content_score = content_result['score']

    confidence_score = round(
        (ml_score * 0.5) + (api_score * 0.3) + (content_score * 0.2),
        2
    )

    # ── Step 7: Make Decision ────────────────────────────────────────────────
    # Override: If file is invalid or content is duplicate, reject/flag
    if file_result and not file_result['valid']:
        status = 'rejected'
        decision_reason = f"Invalid file type: {file_result['reason']}"
    elif duplicate_result and duplicate_result['is_duplicate']:
        status = 'rejected'
        decision_reason = f"Duplicate content already exists: '{duplicate_result['existing_title']}'"
    elif content_result.get('is_spam'):
        status = 'rejected'
        decision_reason = 'Content flagged as spam'
    elif confidence_score >= 80:
        status = 'approved'
        decision_reason = 'High quality content — auto-approved'
    elif confidence_score >= 50:
        status = 'pending'
        decision_reason = 'Content needs community review or admin approval'
    else:
        status = 'rejected'
        decision_reason = 'Low quality content — does not meet minimum standards'

    return {
        'status': status,
        'confidence_score': confidence_score,
        'decision_reason': decision_reason,
        'breakdown': {
            'content_analysis': content_result,
            'ml_prediction': ml_result,
            'api_checks': api_result,
            'file_validation': file_result,
            'duplicate_check': duplicate_result
        },
        'flags': all_flags
    }
