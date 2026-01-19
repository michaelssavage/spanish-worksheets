import logging

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You generate Spanish-learning worksheets for intermediate learners. "
    "Produce natural, idiomatic Spanish. "
    "Prioritize irregular verbs across all tenses "
    "(ser, ir, estar, tener, hacer, poder, decir, venir, poner, querer). "
    "Follow the output format strictly."
)

THEME_POOLS = [
    ["familia", "conflictos", "decisiones difíciles"],
    ["viajes", "retrasos", "problemas logísticos"],
    ["compras", "deudas", "devoluciones"],
    ["clima extremo", "planes cancelados", "emergencias"],
    ["salud", "lesiones", "cambios de hábitos"],
    ["tecnología", "fallos técnicos", "plazos"],
]

def build_user_prompt(themes: list[str]) -> str:
    theme_block = ", ".join(themes)

    prompt = f"""
Themes:
{theme_block}

Requirements:
- Spanish only.
- Use many irregular verbs (at least half per section).
- Do NOT use "ir a + infinitive" in any form.
- Each blank must be written exactly as: ___ (infinitive verb)
- The verb in parentheses must be the infinitive form of the missing verb.
- Every sentence must contain at least one blank with a verb in parentheses.
- No blank may appear without its corresponding verb in parentheses.
- No sentence may contain more than two blanks.
- In the error correction section, the error must be subtle
- (wrong tense or wrong irregular form), not spelling.
- Do not use obvious mistakes like "yo sabo" or "yo cabo".

Sections:

Past tenses (7 sentences):
- Pretérito indefinido
- Pretérito imperfecto
- Pretérito perfecto
- Pluscuamperfecto

Present tenses (7 sentences):
- Presente de indicativo
- Presente perfecto
- Presente progresivo

Future tenses (7 sentences):
- Futuro simple
- Condicional simple

Error correction (7 sentences):
- Each sentence must contain exactly ONE verb error.
- The error must be a tense or conjugation error.
- The incorrect verb must be an irregular verb.
- The rest of the sentence must be correct and natural.
- Do not mark or explain the error.

Fill in the following JSON exactly.
Do not add, remove, or rename keys.
Do not add text outside the JSON.

{{
  "past": [
    "",
    "",
    "",
    "",
    "",
    "",
    "",
  ],
  "present": [
    "",
    "",
    "",
    "",
    "",
    "",
    "",
  ],
  "future": [
    "",
    "",
    "",
    "",
    "",
    "",
    "",
  ],
  "vocab": [
    "",
    "",
    "",
    "",
    "",
    "",
    "",
  ]
}}

Output valid JSON only.
""".strip()

    return prompt


def build_payload(themes: list[str]) -> list[dict]:
    logger.debug("Building payload with themes: %s", themes)

    payload = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_prompt(themes)},
    ]

    logger.info("Payload built successfully")
    return payload
