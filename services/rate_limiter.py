"""
rate_limiter.py - Simple Rate Limiting for Anti-Spam
=====================================================
Prevents abuse by limiting submissions per user per day.

Uses an in-memory store (or a DB collection) to track submission counts.
Default limit: 5 submissions per day per user.
"""

from datetime import datetime, timedelta

# ── In-Memory Rate Limit Store ──────────────────────────────────────────────
# Format: { 'user_id': [timestamp1, timestamp2, ...] }
_rate_store = {}

# ── Configuration ───────────────────────────────────────────────────────────
MAX_SUBMISSIONS_PER_DAY = 5
WINDOW_HOURS = 24


def check_rate_limit(user_id):
    """
    Check if a user has exceeded their submission rate limit.
    
    Args:
        user_id (str): ID of the user
    
    Returns:
        dict: {
            'allowed': bool,
            'remaining': int (submissions remaining),
            'message': str,
            'reset_in': str (human-readable time until reset)
        }
    """
    now = datetime.utcnow()
    window_start = now - timedelta(hours=WINDOW_HOURS)

    # Clean up old entries and get recent submissions
    if user_id in _rate_store:
        _rate_store[user_id] = [
            ts for ts in _rate_store[user_id] if ts > window_start
        ]
    else:
        _rate_store[user_id] = []

    current_count = len(_rate_store[user_id])

    if current_count >= MAX_SUBMISSIONS_PER_DAY:
        # Calculate when the oldest entry expires
        oldest = _rate_store[user_id][0]
        reset_time = oldest + timedelta(hours=WINDOW_HOURS)
        time_left = reset_time - now
        hours_left = int(time_left.total_seconds() / 3600)
        mins_left = int((time_left.total_seconds() % 3600) / 60)

        return {
            'allowed': False,
            'remaining': 0,
            'message': f'Rate limit exceeded. Maximum {MAX_SUBMISSIONS_PER_DAY} submissions per day.',
            'reset_in': f'{hours_left}h {mins_left}m'
        }

    return {
        'allowed': True,
        'remaining': MAX_SUBMISSIONS_PER_DAY - current_count,
        'message': 'OK',
        'reset_in': 'N/A'
    }


def record_submission(user_id):
    """
    Record a new submission for rate limiting tracking.
    
    Args:
        user_id (str): ID of the user
    """
    now = datetime.utcnow()
    if user_id not in _rate_store:
        _rate_store[user_id] = []
    _rate_store[user_id].append(now)
