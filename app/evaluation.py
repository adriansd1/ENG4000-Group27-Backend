from .orchestrator import generate_sql_for_question
from .llm import call_ollama

# A small list of example questions for us to test SQL generation with.
# We can expand this list over time.
TEST_QUESTIONS = [
    "What is the total dg1kwh for site 101?",
    "Which sites had High Temp alarms yesterday?",
    "List sites with only one AC unit.",
]

def quick_sql_smoke_test():
    """
    Running a quick test of SQL generation for all sample questions.

    This helps us:
    - See how the LLM responds to different question types
    - Validate SQL formatting and correctness (even without a database)
    - Identify which prompts need improvement
    """
    for q in TEST_QUESTIONS:
        sql = generate_sql_for_question(q)
        print("\nQ:", q)
        print("SQL:", sql)
        
if __name__ == "__main__":
    # This runs when you do: python -m app.evaluation
    quick_sql_smoke_test()