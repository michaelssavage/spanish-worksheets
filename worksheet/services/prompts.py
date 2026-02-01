import logging

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You generate Spanish-learning worksheets for intermediate/advanced learners. "
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
- Do NOT use obvious mistakes like "yo sabo" or "yo cabo".

Sections:

Past tenses (7 sentences):
- Pretérito indefinido
- Pretérito imperfecto
- Pretérito perfecto
- Pluscuamperfecto
- Each sentence MUST contain exactly ONE blank written as: ___ (infinitive)
- The blank replaces a verb that should be correctly conjugated in the appropriate past tense.
- No sentence may contain more than one blank.

Present tenses (7 sentences):
- Presente de indicativo
- Presente perfecto
- Presente progresivo
- Each sentence MUST contain exactly ONE blank written as: ___ (infinitive)
- The blank replaces a verb that should be correctly conjugated in the appropriate present tense.
- No sentence may contain more than one blank.

Future tenses (7 sentences):
- Futuro simple
- Condicional simple
- Each sentence MUST contain exactly ONE blank written as: ___ (infinitive)
- The blank replaces a verb that should be correctly conjugated in the appropriate future or conditional tense.
- No sentence may contain more than one blank.

Error correction (7 sentences):
- Do NOT use blanks.
- Do NOT use parentheses.
- Each sentence must be fully written.
- Each sentence must contain exactly ONE incorrect verb form.
- The incorrect verb must be a real Spanish verb form, but wrong for the context
  (wrong tense or wrong irregular conjugation).
- All other verbs and structures in the sentence must be correct and natural.
- Write only the sentence containing the error.
- Do NOT include corrections, hints, explanations, or notes.
- If any sentence in this section contains "___" or parentheses, the output is invalid.

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
    ""
  ],
  "present": [
    "",
    "",
    "",
    "",
    "",
    "",
    ""
  ],
  "future": [
    "",
    "",
    "",
    "",
    "",
    "",
    ""
  ],
  "error_correction": [
    "",
    "",
    "",
    "",
    "",
    "",
    ""
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
