def compare_words(correct, typed):
    correct = correct.lower()
    typed = typed.lower()
    errors = []
    for i in range(min(len(correct), len(typed))):
        if correct[i] != typed[i]:
            errors.append((i, typed[i], correct[i]))
    return errors
