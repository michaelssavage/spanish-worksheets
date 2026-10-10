# flake8: noqa
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from worksheet.services.languages import LanguageConfig

logger = logging.getLogger(__name__)

SPANISH_SYSTEM_PROMPT = (
    "You generate Spanish-learning worksheets for intermediate and advanced learners. "
    "Use natural, idiomatic Spanish in realistic contexts, especially work and technology.\n\n"
    "avoid vague sentences. Avoid leaning on common regular verbs like hablar, trabajar, necesitar. "
    "Use many irregular and subjunctive verbs in verb-based sections.\n\n"
    "Ensure all Spanish is correct and natural. Do not use 'ir a + infinitive' in any form. "
    "Never use the obsolete future subjunctive, either simple (e.g. cantare) or compound "
    "(e.g. hubiere cantado); use the natural modern tense required by the context instead. "
    "The future perfect indicative (e.g. habré cantado) is allowed.\n\n"
    'Output: each exercise is a JSON object with two fields: "prompt" (string) and "answer". '
    '"answer" is a JSON array of strings. Never omit either field.\n'
    '- For blank-fill sections (every section except "translation"), each string in "answer" is '
    "ONLY the exact word(s) that fill the blank — a correctly conjugated verb or auxiliary + "
    "participle for verb-based grammar points, or the correct preposition/pronoun/connector/word "
    "otherwise — never the full sentence.\n"
    '- For the "translation" section, there is no blank: "prompt" is a short English clause — a '
    'subject with a conjugated verb (e.g. "He arrived"), or a subject with a conjugated verb plus '
    'one other word or short complement (e.g. "We left the card", "He began to feel tired") — and '
    'each string in "answer" is its natural Spanish translation (e.g. "Llegó", "Dejamos la '
    'tarjeta", "Empezó a sentirse cansado"), matching the same short length. Never a longer, '
    "multi-clause sentence.\n"
    "- If several forms are acceptable, put each form as its own string in the array. Do not "
    'join alternatives with " | " inside one string.\n'
    "- When the blank is a conjugated verb, the prompt must include an explicit subject so "
    "person and number are clear: either a subject pronoun (Yo, Tú, Él, Ella, Usted, "
    "Nosotros/as, Vosotros/as, Ellos/as, Ustedes) or a noun phrase that fixes person and number "
    "(e.g. Mi jefa, Los clientes). Do not omit the subject in a way that leaves who conjugates "
    "unclear.\n"
    "- If ambiguity is intentional, it must be grammatical only (e.g. acceptable tense/aspect "
    "alternates), not from a missing subject; include every acceptable answer as a separate "
    'string in "answer".\n\n'
    "Follow the user's JSON schema and section instructions exactly. Output valid JSON only when asked."
)

CATALAN_SYSTEM_PROMPT = (
    "You generate Catalan-learning worksheets for intermediate and advanced learners. "
    "Use natural, idiomatic standard Central Catalan (as spoken in Barcelona) in realistic "
    "contexts, especially work and technology.\n\n"
    "avoid vague sentences. Avoid leaning on common regular verbs like parlar, treballar, necessitar. "
    "Use many irregular and subjunctive verbs in verb-based sections.\n\n"
    "Ensure all Catalan is correct, normative and natural. Never use Castilianisms (e.g. bueno, "
    "vale, entonces, tenir que, pues). Do not use 'anar a + infinitive' to express the future; "
    "the passat perifràstic (e.g. vaig anar) is correct and encouraged. Write apostrophes, "
    "hyphenated weak pronouns (e.g. dona-m'ho) and the punt volat (e.g. col·legi) exactly, and "
    "use Central Catalan accents (e.g. què, cafè, això).\n\n"
    'Output: each exercise is a JSON object with two fields: "prompt" (string) and "answer". '
    '"answer" is a JSON array of strings. Never omit either field.\n'
    '- For blank-fill sections (every section except "translation"), each string in "answer" is '
    "ONLY the exact word(s) that fill the blank — a correctly conjugated verb or auxiliary + "
    "infinitive/participle for verb-based grammar points, or the correct preposition/pronoun/word "
    "otherwise — never the full sentence.\n"
    '- For the "translation" section, there is no blank: "prompt" is a short English clause — a '
    'subject with a conjugated verb (e.g. "He arrived"), or a subject with a conjugated verb plus '
    'one other word or short complement (e.g. "We left the card", "He began to feel tired") — and '
    'each string in "answer" is its natural Catalan translation (e.g. "Va arribar", "Vam deixar '
    'la targeta", "Va començar a sentir-se cansat"), matching the same short length. Never a '
    "longer, multi-clause sentence.\n"
    "- If several forms are acceptable, put each form as its own string in the array. Do not "
    'join alternatives with " | " inside one string.\n'
    "- When the blank is a conjugated verb, the prompt must include an explicit subject so "
    "person and number are clear: either a subject pronoun (Jo, Tu, Ell, Ella, Vostè, "
    "Nosaltres, Vosaltres, Ells, Elles, Vostès) or a noun phrase that fixes person and number "
    "(e.g. La meva cap, Els clients). Do not omit the subject in a way that leaves who conjugates "
    "unclear.\n"
    "- If ambiguity is intentional, it must be grammatical only (e.g. acceptable tense/aspect "
    "alternates such as passat perifràstic vs. pretèrit perfet), not from a missing subject; "
    'include every acceptable answer as a separate string in "answer".\n\n'
    "Follow the user's JSON schema and section instructions exactly. Output valid JSON only when asked."
)

ITEMS_PER_POOL = 5

TRANSLATION_KEY = "translation"
TRANSLATION_ITEMS = 5

SPANISH_TRANSLATION_EXAMPLES = (
    '"Llegó", "Dejamos la tarjeta", "Empezó a sentirse cansado"'
)
CATALAN_TRANSLATION_EXAMPLES = (
    '"Va arribar", "Vam deixar la targeta", "Va començar a sentir-se cansat"'
)


def translation_guidance(language: LanguageConfig) -> str:
    return (
        'Each "prompt" is a short English clause (no blank) — a subject with a conjugated verb (e.g. '
        '"He arrived"), or a subject with a conjugated verb plus one other word or short complement '
        '(e.g. "We left the card", "He began to feel tired") — related to the themes above. Each '
        f'string in "answer" is its natural {language.name} translation (e.g. '
        f"{language.translation_examples}) — add alternate natural phrasings as extra strings if "
        "more than one exists. Never a longer, multi-clause sentence."
    )


_EMPTY_ITEM = '{"prompt": "", "answer": [""]}'


def _schema_section(key: str, item_count: int) -> str:
    items = ",\n    ".join([_EMPTY_ITEM] * item_count)
    return f'"{key}": [\n    {items}\n  ]'


def build_user_prompt(
    language: LanguageConfig, themes: list[str], grammar_pools: list[str]
) -> str:
    theme_block = ", ".join(themes)
    pool_instructions = "\n\n".join(
        f'"{pool}" ({ITEMS_PER_POOL} exercises) — {language.grammar_pool_guidance[pool]}'
        for pool in grammar_pools
    )
    schema_sections = ",\n  ".join(
        [_schema_section(pool, ITEMS_PER_POOL) for pool in grammar_pools]
        + [_schema_section(TRANSLATION_KEY, TRANSLATION_ITEMS)]
    )

    prompt = f"""
Themes:
{theme_block}

Grammar points for this worksheet (one JSON section per point, {ITEMS_PER_POOL} exercises each):
{pool_instructions}

Translation section — "{TRANSLATION_KEY}" ({TRANSLATION_ITEMS} exercises):
- {translation_guidance(language)}

Worksheet rules (grammar-point sections above, NOT "{TRANSLATION_KEY}"):
- {language.name} only in prompts and answers.
- Do NOT use obvious mistakes like {language.obvious_mistakes}.
- Each \"answer\" is a JSON array of non-empty strings (one or more).
- Each \"prompt\" contains exactly ONE blank, written as: ___ (with a parenthetical infinitive
  hint when the blank is a verb, e.g. ___ ({language.hint_example}); no parenthetical when it
  isn't). No more, no fewer than one blank.
- The blank replaces only the missing word(s) described above for that section; each string in
  \"answer\" is ONLY those word(s), not the full sentence. If multiple answers are acceptable, use
  multiple strings in \"answer\" (never one string with \" | \").
- Intentional ambiguity only when grammatical (e.g. acceptable tense/aspect alternates or
  synonymous connectors); then list every acceptable answer in \"answer\".

Translation section rules:
- "{TRANSLATION_KEY}" prompts are short English clauses — a subject with a conjugated verb (e.g.
  "He arrived"), or a subject with a conjugated verb plus one other word or short complement (e.g.
  "We left the card", "He began to feel tired") — contain NO blank, and are unrelated to the
  grammar points above. Never a longer, multi-clause sentence.
- "{TRANSLATION_KEY}" answers are {language.name} only, each a short clause translation matching
  the same length as the prompt.
- Each \"answer\" is a JSON array of non-empty strings (one or more).

Fill in the following JSON exactly.
Do not add, remove, or rename keys.
Do not add text outside the JSON.

{{
  {schema_sections}
}}

Output valid JSON only.
""".strip()

    return prompt


def build_payload(
    language: LanguageConfig, themes: list[str], grammar_pools: list[str]
) -> list[dict]:
    logger.debug(
        "Building %s payload with themes: %s, grammar_pools: %s",
        language.code,
        themes,
        grammar_pools,
    )

    payload = [
        {"role": "system", "content": language.system_prompt},
        {
            "role": "user",
            "content": build_user_prompt(language, themes, grammar_pools),
        },
    ]

    logger.info("Payload built successfully")
    return payload


def build_custom_user_prompt(language: LanguageConfig, request_text: str) -> str:
    prompt = f"""
Custom exercise request:
{request_text}

Create exactly 8 {language.name} conjugation exercises matching the request.

Rules:
- Use natural, idiomatic {language.name} in realistic contexts.
- Each "prompt" must be {language.name} only.
- Each "prompt" must contain exactly ONE blank, written as: ___ (infinitive).
- The blank replaces the verb to conjugate.
- Each prompt must include an explicit subject so person and number are clear.
- Each "answer" must be a JSON array of one or more non-empty strings.
- Each answer string is ONLY the correctly conjugated verb, or auxiliary + participle if required.
- If several forms are acceptable, put each form as its own string in the array.
- Do not include full sentences in "answer".
- {language.periphrastic_rule}
- Do not add translations, explanations, markdown, or text outside the JSON.

Fill in the following JSON exactly.
Do not add, remove, or rename keys.

{{
  "exercises": [
    {{"prompt": "", "answer": [""]}},
    {{"prompt": "", "answer": [""]}},
    {{"prompt": "", "answer": [""]}},
    {{"prompt": "", "answer": [""]}},
    {{"prompt": "", "answer": [""]}},
    {{"prompt": "", "answer": [""]}},
    {{"prompt": "", "answer": [""]}},
    {{"prompt": "", "answer": [""]}}
  ]
}}

Output valid JSON only.
""".strip()

    return prompt


def build_custom_payload(language: LanguageConfig, request_text: str) -> list[dict]:
    logger.debug(
        "Building %s custom payload for request: %s", language.code, request_text
    )

    payload = [
        {"role": "system", "content": language.system_prompt},
        {
            "role": "user",
            "content": build_custom_user_prompt(language, request_text),
        },
    ]

    logger.info("Custom payload built successfully")
    return payload
