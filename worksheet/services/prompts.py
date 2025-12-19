import logging

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You generate Spanish-learning worksheets for intermediate learners. "
    "Produce clear, natural, idiomatic Spanish. "
    "Prioritize the use of irregular verbs across all tenses. "
    "(e.g., ser, ir, estar, tener, hacer, poder, decir, venir, poner, querer). "
    "Sentences should sound natural and realistic, not artificial drills."
)


THEME_POOLS = [
    ["familia", "comida", "rutinas diarias"],
    ["viajes", "hoteles", "transporte público"],
    ["compras", "dinero", "tiendas"],
    ["clima", "estaciones", "naturaleza"],
    ["salud", "actividad física", "deportes"],
    ["tecnología", "oficina", "estudio"],
]


def build_user_prompt(themes):
    """
    Returns a structured user prompt as a single string.
    """

    theme_block = ", ".join(themes)

    prompt = f"""
Generate a Spanish worksheet.

Themes for this worksheet:
{theme_block}

General requirements:
- Use many irregular verbs (at least half of the sentences per section).
- Each sentence must contain one or two blanks marked with "___".
- A sentence may NOT contain more than two blanks.
- Blanks may appear in the same verb phrase or in different verbs.
- Spanish only.

Sections required:

1. Past tenses:
   - 10 sentences total.
   - Mix of:
     - Pretérito indefinido
     - Pretérito imperfecto
     - Pretérito perfecto
     - Pluscuamperfecto
   - Each sentence must clearly indicate which tense is required from context.

2. Present tenses:
   - 10 sentences total.
   - Mix of:
     - Presente de indicativo
     - Presente perfecto
     - Presente progresivo
   - Focus on common irregular present forms.

3. Future tenses:
   - 10 sentences total.
   - Mix of:
     - Futuro simple
     - Futuro próximo (ir a + infinitivo)
     - Condicional simple
   - Emphasize irregular future and conditional stems.

4. Vocabulary expansion:
   - 10 complete sentences (no blanks).
   - Natural usage of vocabulary from the themes.
   - Include a variety of tenses.

Output format:
JSON only.
Use this structure exactly:

{{
  "past": ["sentence1", "..."],
  "present": ["sentence1", "..."],
  "future": ["sentence1", "..."],
  "vocab": ["sentence1", "..."]
}}

Rules:
- Exactly 10 sentences per section.
- No explanations.
- No metadata.
- No English.
    """.strip()

    return prompt


def build_payload(themes):
    """
    Returns the full model payload for DeepSeek.
    """
    logger.debug(f"Building payload with themes: {themes}")
    user_prompt = build_user_prompt(themes)

    payload = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
    logger.info("Payload built successfully")
    return payload
