"""Grammar pools used to vary the conjugation section of a worksheet.

Each pool is a grammar point the LLM can build fill-in-the-blank exercises
around. Some are verb tenses (the blank is a conjugated verb); others are
non-verb grammar points (the blank is a preposition, pronoun, connector, or
similar). The *_GRAMMAR_POOL_GUIDANCE dicts tell the LLM what the blank/answer should be
for each pool. Spanish and Catalan each have their own pools.
"""

SPANISH_GRAMMAR_POOLS = [
    "past tenses",
    "present forms",
    "subjunctive",
    "por vs para",
    "lo que vs el que vs lo cual",
    "irregular verbs",
]

SPANISH_GRAMMAR_POOL_GUIDANCE = {
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
        "call for the subjunctive. Answer is the conjugated verb form only."
    ),
    "por vs para": (
        "Each blank is exactly 'por' or 'para', whichever fits the context "
        "(cause, purpose, exchange, duration, destination, deadline, etc.). "
        "Answer is 'por' or 'para' only — not a full phrase."
    ),
    "lo que vs el que vs lo cual": (
        "Each blank is a relative pronoun: 'lo que', 'el que' (or 'la que', "
        "'los que', 'las que'), or 'lo cual', whichever fits the context. "
        "Mix all three across the 5 items, including at least one 'lo cual' "
        "referring back to a whole preceding clause (after a comma) and at "
        "least one 'el/la/los/las que' after a preposition with a specific "
        "antecedent. If both 'lo que' and 'lo cual' are grammatical, list "
        "both. Answer is the relative pronoun only."
    ),
    "irregular verbs": (
        "Each blank is the correctly conjugated form of a less common irregular "
        "or stem-changing verb (not A1 basics like tener or saber), in "
        "whichever tense/mood fits the context. Answer is the "
        "conjugated verb form only."
    ),
}

CATALAN_GRAMMAR_POOLS = [
    "past tenses",
    "present forms",
    "future and conditional",
    "subjunctive",
    "per vs per a",
    "irregular verbs",
]

CATALAN_GRAMMAR_POOL_GUIDANCE = {
    "past tenses": (
        "Distribute across the 5 items: passat perifràstic (e.g. vaig anar), "
        "pretèrit perfet (e.g. he anat), pretèrit imperfet, plusquamperfet. "
        "Answer is the conjugated verb form (or auxiliary + infinitive/"
        "participle) only."
    ),
    "present forms": (
        "Distribute across the 5 items: present d'indicatiu (include "
        "irregular first-person forms such as faig, dic, visc, crec) and "
        "estar + gerundi. Answer is the conjugated verb form (or auxiliary "
        "+ gerund) only."
    ),
    "future and conditional": (
        "Distribute across the 5 items: futur simple, futur perfet, "
        "condicional simple, condicional perfet. Answer is the conjugated "
        "verb form (or auxiliary + participle) only."
    ),
    "subjunctive": (
        "Distribute across the 5 items: present de subjuntiu, imperfet de "
        "subjuntiu, perfet de subjuntiu, plusquamperfet de subjuntiu. "
        "Prefer triggers that naturally call for the subjunctive. Answer is "
        "the conjugated verb form only."
    ),
    "per vs per a": (
        "Each blank is exactly 'per' or 'per a', whichever fits the context "
        "under current normative Catalan (cause, means, duration vs. "
        "purpose, destination, recipient). Answer is 'per' or 'per a' only "
        "— not a full phrase."
    ),
    "irregular verbs": (
        "Each blank is the correctly conjugated form of a common irregular "
        "verb (e.g. fer, dir, venir, tenir, voler, poder, saber, ser, "
        "estar, viure, beure, conèixer), in whichever tense/mood fits the "
        "context. Answer is the conjugated verb form only."
    ),
}
