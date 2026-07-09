"""Smoke test: python -m modules.proactive.test_context_deepening"""

from modules.proactive.context_deepening import (
    detect_decision_event,
    follow_up_question,
    is_skip_response,
)


def main() -> None:
    ev = detect_decision_event("I'm declining Sarah's birthday party invitation")
    assert ev is not None
    assert "?" in follow_up_question(ev)
    assert is_skip_response("rather not say")
    assert detect_decision_event("hello") is None
    print("context deepening smoke OK")


if __name__ == "__main__":
    main()
