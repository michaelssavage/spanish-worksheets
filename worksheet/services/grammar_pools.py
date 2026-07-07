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
    "ser vs estar",
    "por vs para",
    "prepositions",
    "relative pronouns",
    "object pronouns",
    "reflexive verbs",
    "periphrastic expressions",
    "connectors",
    "reported speech",
    "passive and impersonal",
    "idiomatic expressions",
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
    "ser vs estar": (
        "Each blank is a correctly conjugated form of ser or estar, "
        "whichever fits the context (location, state, identity, change, "
        "emotion, passive, etc.). Answer is the conjugated ser/estar form "
        "only."
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
    "relative pronouns": (
        "Each blank is the correct relative pronoun (que, quien/quienes, "
        "cuyo/a/os/as, el/la cual, donde, lo que, etc.) linking two clauses. "
        "Answer is the relative pronoun only."
    ),
    "object pronouns": (
        "Each blank is the correct direct, indirect, or combined object "
        "pronoun (lo, la, los, las, le, les, se, me, te, nos, or combined "
        "forms like se lo) referring to a previously mentioned noun. Answer "
        "is the pronoun (or pronoun combination) only."
    ),
    "reflexive verbs": (
        "Each blank is a correctly conjugated reflexive verb with its "
        "reflexive pronoun (levantarse, quejarse, arrepentirse, equivocarse, "
        "etc.). Answer is the pronoun + conjugated verb as a single string "
        "(e.g. 'se equivocó')."
    ),
    "periphrastic expressions": (
        "Each blank is a periphrastic verb construction (tener que + "
        "infinitivo, deber de + infinitivo, llevar + gerundio, acabar de + "
        "infinitivo, seguir/continuar + gerundio, ponerse a + infinitivo, "
        "etc.) — never 'ir a + infinitivo'. Answer is the full construction."
    ),
    "connectors": (
        "Each blank is a discourse connector fitting the logical "
        "relationship between clauses (sin embargo, por lo tanto, aunque, "
        "ya que, así que, además, no obstante, mientras que, etc.). Answer "
        "is the connector only."
    ),
    "reported speech": (
        "Each prompt reports what someone said (dijo que, comentó que, "
        "explicó que, etc.) and the blank is the correctly transformed verb "
        "form of the reported clause (tense/mood shift from direct to "
        "indirect speech). Answer is the conjugated verb form only."
    ),
    "passive and impersonal": (
        "Each blank is either a passive construction (ser + participio) or "
        "an impersonal 'se' construction (se dice que, se necesita, se "
        "prohíbe, etc.), whichever fits the prompt. Answer is the full verb "
        "form used in the blank."
    ),
    "idiomatic expressions": (
        "Each blank completes a natural Spanish idiom or fixed expression "
        "appropriate to the context (e.g. tomar una decisión, dar por "
        "hecho, echar de menos, tener en cuenta). Answer is the missing "
        "word(s) of the idiom only."
    ),
}
