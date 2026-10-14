def format_turn(question: str, answer: str) -> str:
    """One history entry, in the format the retriever and the prompt expect."""
    return f"Question:{question}-Answer:{answer}"
