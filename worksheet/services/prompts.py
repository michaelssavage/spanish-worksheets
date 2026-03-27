# flake8: noqa
import logging

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You generate Spanish-learning worksheets for intermediate and advanced learners. "
    "Write natural, idiomatic Spanish in realistic contexts, especially work and technology.\n\n"
    "Use a high density of irregular verbs (at least 60%). Prioritize:\n"
    "ser, ir, estar, tener, hacer, poder, decir, venir, poner, querer, ver, dar, saber, traer.\n"
    "Avoid relying on common regular verbs like hablar, trabajar, necesitar.\n\n"
    "Prefer concrete, specific situations (deadlines, bugs, meetings, decisions, failures). "
    "Avoid vague or generic sentences.\n\n"
    "Ensure all Spanish is correct and natural. Do not use 'ir a + infinitive'.\n\n"
    'Every exercise is a JSON object with exactly two string fields: "prompt" (what the learner sees) '
    'and "answer". For exercises with a blank (___), "answer" is ONLY the correctly conjugated verb '
    "(or verb phrase for compound tenses, e.g. ha hecho), never the full sentence. For translation "
    'exercises, "answer" is the full correct Spanish sentence. Never omit either field.\n\n'
    "Follow the user’s formatting and JSON instructions exactly."
)

THEME_POOLS = [
    ["reuniones", "decisiones de equipo", "conflictos laborales"],
    ["plazos", "entregas urgentes", "errores en proyectos"],
    ["bugs", "debugging", "errores en producción"],
    ["deploys", "fallos en servidores", "rollback"],
    ["revisiones de código", "pull requests", "comentarios"],
    ["trabajo remoto", "zonas horarias", "reuniones virtuales"],
    ["mensajes malinterpretados", "falta de comunicación", "urgencias"],
    ["clientes", "negociaciones", "contratos"],
    ["pagos", "facturas", "retrasos"],
    ["errores graves", "decisiones difíciles", "consecuencias"],
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

Past tenses (7 exercises as JSON objects):
- Pretérito indefinido
- Pretérito imperfecto
- Pretérito perfecto
- Pluscuamperfecto
- Each \"prompt\" MUST contain exactly ONE blank written as: ___ (infinitive)
- The blank replaces a verb that should be correctly conjugated in the appropriate past tense.
- No prompt may contain more than one blank.
- Each \"answer\" is ONLY the correctly conjugated verb (or auxiliary + participle if the tense requires it). Do not repeat the rest of the sentence.

Present tenses (7 exercises as JSON objects):
- Presente de indicativo
- Presente perfecto
- Presente progresivo
- Each \"prompt\" MUST contain exactly ONE blank written as: ___ (infinitive)
- The blank replaces a verb that should be correctly conjugated in the appropriate present tense.
- Each \"answer\" is ONLY the correctly conjugated verb (or auxiliary + participle if required). Do not repeat the rest of the sentence.

Future tenses (7 exercises as JSON objects):
- Futuro simple
- Condicional simple
- Each \"prompt\" MUST contain exactly ONE blank written as: ___ (infinitive)
- Each \"answer\" is ONLY the correctly conjugated verb (or auxiliary + participle if required). Do not repeat the rest of the sentence.

Translation — English → Spanish (7 exercises as JSON objects):
- Each item forces production (full translation), not recognition.
- Keep a one-verb focus: the learner’s main challenge is one target verb or one tense choice.
- When specifying a verb, prefer irregular verbs (ser, ir, estar, tener, hacer, poder, decir,
  venir, poner, querer, ver, dar, saber, traer, etc.).
- \"prompt\": one string containing (1) a complete sentence in English, then (2) exactly ONE constraint
  in Spanish in parentheses.
- The constraint must be exactly ONE of:
  a) A required verb in infinitive: (usar: infinitivo) e.g. (usar: poner)
  b) A required tense: (usar: nombre del tiempo) e.g. (usar: pretérito indefinido)
- \"answer\": the full correct Spanish translation of the English sentence, obeying the constraint.
- Do NOT put the Spanish translation in \"prompt\"; it belongs only in \"answer\".
- Do NOT include more than one constraint per item (no second verb hint, no extra tenses).
- Prompts must describe realistic work or technology situations.
- Keep prompts concise but require tense decisions (timing, cause, sequence).
- Do NOT use blanks (___) in translation prompts.

Fill in the following JSON exactly.
Do not add, remove, or rename keys.
Do not add text outside the JSON.

{{
  "past": [
    {{"prompt": "", "answer": ""}},
    {{"prompt": "", "answer": ""}},
    {{"prompt": "", "answer": ""}},
    {{"prompt": "", "answer": ""}},
    {{"prompt": "", "answer": ""}},
    {{"prompt": "", "answer": ""}},
    {{"prompt": "", "answer": ""}}
  ],
  "present": [
    {{"prompt": "", "answer": ""}},
    {{"prompt": "", "answer": ""}},
    {{"prompt": "", "answer": ""}},
    {{"prompt": "", "answer": ""}},
    {{"prompt": "", "answer": ""}},
    {{"prompt": "", "answer": ""}},
    {{"prompt": "", "answer": ""}}
  ],
  "future": [
    {{"prompt": "", "answer": ""}},
    {{"prompt": "", "answer": ""}},
    {{"prompt": "", "answer": ""}},
    {{"prompt": "", "answer": ""}},
    {{"prompt": "", "answer": ""}},
    {{"prompt": "", "answer": ""}},
    {{"prompt": "", "answer": ""}}
  ],
  "translation": [
    {{"prompt": "", "answer": ""}},
    {{"prompt": "", "answer": ""}},
    {{"prompt": "", "answer": ""}},
    {{"prompt": "", "answer": ""}},
    {{"prompt": "", "answer": ""}},
    {{"prompt": "", "answer": ""}},
    {{"prompt": "", "answer": ""}}
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
