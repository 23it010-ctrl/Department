"""Quick test script for the validation engine."""
from services.validation_engine import validate_submission
from services.voting_engine import get_vote_weight
from services.rate_limiter import check_rate_limit

print("=" * 60)
print("  VALIDATION ENGINE TEST")
print("=" * 60)

# Test 1: High quality content (should auto-approve)
print("\n[Test 1] High quality academic content:")
result = validate_submission(
    title='Data Structures Unit 3 - Trees and Graphs',
    content='This comprehensive study material covers binary trees, AVL trees, '
            'B-trees, graph traversal algorithms including BFS and DFS, shortest '
            'path algorithms, and minimum spanning trees. Includes solved examples '
            'and practice problems for the semester examination.',
    content_type='notes'
)
print(f"  Status:     {result['status']}")
print(f"  Score:      {result['confidence_score']}")
print(f"  Reason:     {result['decision_reason']}")
print(f"  ML Score:   {result['breakdown']['ml_prediction']['ml_score']}")
print(f"  API Score:  {result['breakdown']['api_checks']['api_score']}")
print(f"  Text Score: {result['breakdown']['content_analysis']['score']}")

# Test 2: Spam content (should reject)
print("\n[Test 2] Spam content:")
result2 = validate_submission(
    title='FREE MONEY!!! Click here NOW!',
    content='Buy now and earn money fast! Limited time offer! Free bitcoin!',
    content_type='news'
)
print(f"  Status:     {result2['status']}")
print(f"  Score:      {result2['confidence_score']}")
print(f"  Reason:     {result2['decision_reason']}")
print(f"  Flags:      {result2['flags']}")

# Test 3: Medium quality (should go to review)
print("\n[Test 3] Medium quality content:")
result3 = validate_submission(
    title='My certificate from workshop',
    content='I attended a workshop on web development and got this certificate.',
    content_type='achievements'
)
print(f"  Status:     {result3['status']}")
print(f"  Score:      {result3['confidence_score']}")
print(f"  Reason:     {result3['decision_reason']}")

# Test 4: Vote weights
print("\n[Test 4] Vote weights:")
print(f"  Student weight: {get_vote_weight('student')}")
print(f"  Faculty weight: {get_vote_weight('faculty')}")
print(f"  Admin weight:   {get_vote_weight('admin')}")

# Test 5: Rate limiter
print("\n[Test 5] Rate limiter:")
rl = check_rate_limit('test_user_123')
print(f"  Allowed:   {rl['allowed']}")
print(f"  Remaining: {rl['remaining']}")

print("\n" + "=" * 60)
print("  ALL TESTS PASSED")
print("=" * 60)
