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
    "subjunctive",
    "por vs para",
    "prepositions",
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
    "subjunctive": (
        "Distribute across the 5 items: presente de subjuntivo, imperfecto "
        "de subjuntivo (-ra/-se), pretérito pluscuamperfecto de subjuntivo, "
        "presente perfecto de subjuntivo. Prefer triggers that naturally "
        "call for the subjunctive (dudar que, es importante que, ojalá, "
        "aunque, para que, sin que, emotion/judgment/wish, etc.). Answer is "
        "the conjugated verb form only."
    ),
    "por vs para": (
        "Each blank is exactly 'por' or 'para', whichever fits the context "
        "(cause, purpose, exchange, duration, destination, deadline, etc.). "
        "Answer is 'por' or 'para' only — not a full phrase."
    ),
    "prepositions": (
        "Each blank is the single correct preposition for the context (a, "
        "de, en, con, sobre, entre, hacia, desde, hasta, etc.), especially "
        "verb + preposition combinations learners often get wrong. Answer "
        "is the preposition only."
    ),
    "irregular verbs": (
        "Each blank is the correctly conjugated form of a common irregular "
        "verb (ser, estar, ir, tener, hacer, poder, querer, decir, venir, "
        "poner, saber, dar, etc.), in whichever tense/mood fits the "
        "context. Answer is the conjugated verb form only."
    ),
}
