"""
voting_engine.py - Community Voting / Crowd Intelligence System
================================================================
Implements weighted voting for content that falls into the 'pending' category.

How it works:
  - Content with confidence score 50-80 goes to community voting
  - Users can vote: 'approve' or 'reject' (one vote per user per submission)
  - Votes are weighted by user trust level:
      * Normal user (student)  = weight 1
      * Trusted user (faculty) = weight 3
      * Admin                  = weight 5

Decision Rules:
  - If approve votes > 10 AND >80% weighted → auto-approve
  - If reject votes dominate (>70% weighted) → auto-reject
  - Otherwise → keep as pending for admin review
"""


# ── Vote Weight Configuration ───────────────────────────────────────────────
VOTE_WEIGHTS = {
    'student': 1,
    'faculty': 3,
    'admin': 5
}

# ── Decision Thresholds ────────────────────────────────────────────────────
MIN_VOTES_FOR_DECISION = 5          # Minimum total votes before auto-deciding
APPROVE_THRESHOLD_PERCENT = 80      # % weighted approval needed to auto-approve
REJECT_THRESHOLD_PERCENT = 70       # % weighted rejection needed to auto-reject


def get_vote_weight(user_role):
    """
    Get the voting weight for a given user role.
    
    Args:
        user_role (str): Role of the user ('student', 'faculty', 'admin')
    
    Returns:
        int: Weight value for the vote
    """
    return VOTE_WEIGHTS.get(user_role, 1)


def cast_vote(submission_id, user_id, user_role, vote_type, get_col_func):
    """
    Cast a vote for a pending submission.
    
    Args:
        submission_id (str): ID of the submitted content
        user_id (str): ID of the voting user
        user_role (str): Role of the user ('student', 'faculty', 'admin')
        vote_type (str): 'approve' or 'reject'
        get_col_func (callable): Function to get database collection
    
    Returns:
        dict: {
            'success': bool,
            'message': str,
            'vote_weight': int,
            'current_status': dict (vote tally)
        }
    """
    votes_col = get_col_func('votes')

    # ── Check: Only one vote per user per submission ─────────────────────────
    existing_vote = votes_col.find_one({
        'submission_id': str(submission_id),
        'user_id': str(user_id)
    })

    if existing_vote:
        return {
            'success': False,
            'message': 'You have already voted on this submission',
            'vote_weight': 0,
            'current_status': get_vote_tally(submission_id, get_col_func)
        }

    # ── Cast the vote ────────────────────────────────────────────────────────
    weight = get_vote_weight(user_role)
    
    votes_col.insert_one({
        'submission_id': str(submission_id),
        'user_id': str(user_id),
        'user_role': user_role,
        'vote_type': vote_type,  # 'approve' or 'reject'
        'weight': weight
    })

    # ── Get updated tally and check if decision threshold is reached ─────────
    tally = get_vote_tally(submission_id, get_col_func)
    decision = evaluate_votes(tally)

    # If a decision has been reached, update the submission status
    if decision['decided']:
        submissions_col = get_col_func('submitted_content')
        try:
            from bson.objectid import ObjectId
            query = {'_id': ObjectId(submission_id)}
            if not submissions_col.find_one(query):
                query = {'_id': submission_id}
        except Exception:
            query = {'_id': submission_id}

        submissions_col.update_one(query, {'$set': {
            'status': decision['new_status'],
            'decided_by': 'community_vote',
            'decision_reason': decision['reason']
        }})

    return {
        'success': True,
        'message': f'Vote recorded successfully (weight: {weight})',
        'vote_weight': weight,
        'current_status': tally,
        'decision': decision
    }


def get_vote_tally(submission_id, get_col_func):
    """
    Get the current vote tally for a submission.
    
    Args:
        submission_id (str): ID of the submission
        get_col_func (callable): Function to get database collection
    
    Returns:
        dict: {
            'total_votes': int,
            'approve_votes': int,
            'reject_votes': int,
            'weighted_approve': int,
            'weighted_reject': int,
            'approve_percent': float,
            'reject_percent': float
        }
    """
    votes_col = get_col_func('votes')
    all_votes = list(votes_col.find({'submission_id': str(submission_id)}))

    approve_votes = [v for v in all_votes if v['vote_type'] == 'approve']
    reject_votes = [v for v in all_votes if v['vote_type'] == 'reject']

    weighted_approve = sum(v.get('weight', 1) for v in approve_votes)
    weighted_reject = sum(v.get('weight', 1) for v in reject_votes)
    total_weighted = weighted_approve + weighted_reject

    return {
        'total_votes': len(all_votes),
        'approve_votes': len(approve_votes),
        'reject_votes': len(reject_votes),
        'weighted_approve': weighted_approve,
        'weighted_reject': weighted_reject,
        'approve_percent': round((weighted_approve / total_weighted * 100), 1) if total_weighted > 0 else 0,
        'reject_percent': round((weighted_reject / total_weighted * 100), 1) if total_weighted > 0 else 0
    }


def evaluate_votes(tally):
    """
    Evaluate if enough votes have been cast to make a decision.
    
    Args:
        tally (dict): Vote tally from get_vote_tally()
    
    Returns:
        dict: {
            'decided': bool,
            'new_status': str or None,
            'reason': str
        }
    """
    if tally['total_votes'] < MIN_VOTES_FOR_DECISION:
        return {
            'decided': False,
            'new_status': None,
            'reason': f"Need at least {MIN_VOTES_FOR_DECISION} votes ({tally['total_votes']} so far)"
        }

    if tally['approve_percent'] >= APPROVE_THRESHOLD_PERCENT:
        return {
            'decided': True,
            'new_status': 'approved',
            'reason': f"Community approved ({tally['approve_percent']}% weighted approval)"
        }

    if tally['reject_percent'] >= REJECT_THRESHOLD_PERCENT:
        return {
            'decided': True,
            'new_status': 'rejected',
            'reason': f"Community rejected ({tally['reject_percent']}% weighted rejection)"
        }

    return {
        'decided': False,
        'new_status': None,
        'reason': 'No clear consensus — awaiting more votes or admin review'
    }
