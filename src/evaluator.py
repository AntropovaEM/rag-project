def _tokenize(text):
    return set(text.lower().split())


def evaluate_answer(answer, contexts, question):
    if not answer or not contexts:
        return {"faithfulness": 0.0, "relevancy": 0.0, "precision": 0.0}
    
    answer_words = _tokenize(answer)
    context_words = set()
    for ctx in contexts:
        context_words.update(_tokenize(ctx))
    
    faithfulness = len(answer_words & context_words) / max(len(answer_words), 1)
    
    question_words = _tokenize(question)
    relevancy = len(answer_words & question_words) / max(len(question_words), 1)
    
    precision = min(1.0, len(contexts) / 4)
    
    return {
        "faithfulness": round(faithfulness, 2),
        "relevancy": round(relevancy, 2),
        "precision": round(precision, 2)
    }