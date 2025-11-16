SYSTEM_PROMPT = (
    "You generate Spanish-learning worksheets. "
    "Produce clear, accurate Spanish examples suitable for intermediate learners. "
    "Avoid repeating any forbidden content."
)

THEME_POOLS = [
    ["familia", "comida", "rutinas diarias"],
    ["viajes", "hoteles", "transporte público"],
    ["compras", "dinero", "tiendas"],
    ["clima", "estaciones", "naturaleza"],
    ["salud", "actividad física", "deportes"],
    ["tecnología", "oficina", "estudio"],
]


def build_user_prompt(forbidden_sentences, themes):
    """
    forbidden_sentences: list of strings
    Returns a structured user prompt as a single string.
    """

    forbidden_block = "\n".join(f"- {s}" for s in forbidden_sentences) or "None."
    theme_block = ", ".join(themes)

    # Build the prompt
    prompt = f"""
Generate a Spanish worksheet.

Themes for this worksheet:
{theme_block}

Forbidden sentences:
{forbidden_block}

Sections required:
1. Past tense: 10 sentences with a missing verb (user fills the correct past form).
2. Present or future tense: 10 sentences with a missing verb.
3. Vocabulary expansion: 10 natural sentences with mixed vocabulary.

Output format:
JSON only.
Use this structure:

{{
  "past": ["sentence1", "..."],
  "present_future": ["sentence1", "..."],
  "vocab": ["sentence1", "..."]
}}

Rules:
- No English.
- No repetition of forbidden sentences.
- Exactly 10 sentences per section.
- No explanations.
    """.strip()

    return prompt


def build_payload(forbidden_sentences, themes):
    """
    Returns the full model payload for OpenAI or DeepSeek (depending on client).
    """

    user_prompt = build_user_prompt(forbidden_sentences, themes)

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
