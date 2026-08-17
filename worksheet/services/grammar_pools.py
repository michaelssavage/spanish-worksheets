"""Grammar pools used to vary the conjugation section of a worksheet.

Each pool is a grammar point the LLM can build fill-in-the-blank exercises
around. Some are verb tenses (the blank is a conjugated verb); others are
non-verb grammar points (the blank is a preposition, pronoun, connector, or
similar). GRAMMAR_POOL_GUIDANCE tells the LLM what the blank/answer should be
for each pool.
"""

GRAMMAR_POOLS = [
    "past tenses",
    "present forms",
    "future tenses",
    "subjunctive",
    "por vs para",
    "irregular verbs",
]

GRAMMAR_POOL_GUIDANCE = {
    "past tenses": (
        "Distribute across the 5 items: pretérito indefinido, pretérito "
        "imperfecto, pretérito perfecto, pluscuamperfecto. Answer is the "
        "conjugated verb form (or auxiliary + participle) only."
    ),
    "present forms": (
        "Distribute across the 5 items: presente de indicativo, presente "
        "perfecto, presente progresivo. Answer is the conjugated verb form "
        "(or auxiliary + participle) only."
    ),
    "future tenses": (
        "Distribute across the 5 items: futuro simple, futuro perfecto. "
        "Answer is the conjugated verb form (or auxiliary + participle) "
        "only."
    ),
    "subjunctive": (
        "Distribute across the 5 items: presente de subjuntivo, imperfecto "
        "de subjuntivo (-ra/-se), pretérito pluscuamperfecto de subjuntivo, "
        "presente perfecto de subjuntivo. Prefer triggers that naturally "
        "call for the subjunctive. Answer is the conjugated verb form only."
    ),
    "por vs para": (
        "Each blank is exactly 'por' or 'para', whichever fits the context "
        "(cause, purpose, exchange, duration, destination, deadline, etc.). "
        "Answer is 'por' or 'para' only — not a full phrase."
    ),
    "irregular verbs": (
        "Each blank is the correctly conjugated form of a common irregular "
        "verb, in whichever tense/mood fits the context. Answer is the "
        "conjugated verb form only."
    ),
}
