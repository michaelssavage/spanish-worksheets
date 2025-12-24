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
    ["familia", "comida", "rutinas diarias"],
    ["viajes", "hoteles", "transporte público"],
    ["compras", "dinero", "tiendas"],
    ["clima", "estaciones", "naturaleza"],
    ["salud", "actividad física", "deportes"],
    ["tecnología", "oficina", "estudio"],
]


def build_user_prompt(themes: list[str]) -> str:
    theme_block = ", ".join(themes)

    prompt = f"""
Themes:
{theme_block}

Requirements:
- Spanish only.
- Use many irregular verbs (at least half per section).
- Each sentence must contain one or two blanks marked with "___".
- No sentence may contain more than two blanks.

Sections:

Past tenses (10 sentences):
- Pretérito indefinido
- Pretérito imperfecto
- Pretérito perfecto
- Pluscuamperfecto

Present tenses (10 sentences):
- Presente de indicativo
- Presente perfecto
- Presente progresivo

Future tenses (10 sentences):
- Futuro simple
- Futuro próximo (ir a + infinitivo)
- Condicional simple

Vocabulary:
- 10 complete sentences
- No blanks
- Natural usage of the themes
- Mixed tenses

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
    "",
    "",
    "",
    ""
  ],
  "vocab": [
    "",
    "",
    "",
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