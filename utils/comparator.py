def compare_words(correct, typed):
    correct = correct.lower()
    typed = typed.lower()

    # Se os comprimentos são diferentes, há erro
    if len(correct) != len(typed):
        return ["length_mismatch"]

    errors = []
    for i in range(len(correct)):
        if correct[i] != typed[i]:
            errors.append((i, typed[i], correct[i]))

    # Retorna None se não houver erros, lista de erros caso contrário
    return errors if errors else None