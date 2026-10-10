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
    "future tenses",
    "subjunctive",
    "por vs para",
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

CATALAN_GRAMMAR_POOLS = [
    "past tenses",
    "present forms",
    "future and conditional",
    "subjunctive",
    "pronoms febles",
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
    "pronoms febles": (
        "Each blank is a weak pronoun or pronoun combination (e.g. en, hi, "
        "el, la, els, li, ho, l'hi, n'hi, me'n, se'l) in its correct form "
        "and position for the context. No parenthetical hint. Answer is the "
        "pronoun(s) only, with apostrophes/hyphens exactly as written."
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
