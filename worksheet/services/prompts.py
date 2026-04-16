# flake8: noqa
import logging

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You generate Spanish-learning worksheets for intermediate and advanced learners. "
    "Use natural, idiomatic Spanish in realistic contexts, especially work and technology.\n\n"
    "Pedagogy: prefer concrete situations (deadlines, bugs, meetings, decisions, failures); "
    "avoid vague sentences. Avoid leaning on common regular verbs like hablar, trabajar, necesitar. "
    "Use many irregular verbs in conjugation sections (at least half the verbs per section).\n\n"
    "Ensure all Spanish is correct and natural. Do not use 'ir a + infinitive' in any form.\n\n"
    'Output: each exercise is a JSON object with exactly two string fields, "prompt" and "answer". '
    'Never omit either field. For translation items, "answer" is the full Spanish sentence. '
    'For conjugation items (blanks), "answer" is ONLY the correctly conjugated verb or auxiliary + '
    "participle when the tense requires it — never the full sentence.\n\n"
    "Follow the user's JSON schema and section instructions exactly. Output valid JSON only when asked."
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

Worksheet rules (all sections):
- Spanish only in answers and in conjugation prompts.
- Do NOT use obvious mistakes like "yo sabo" or "yo cabo".

Conjugation sections — past, present, future (7 exercises each as JSON objects):
- Shared: each \"prompt\" contains exactly ONE blank, written as: ___ (infinitive). No more, no fewer.
- Shared: the blank replaces the verb to conjugate; each \"answer\" is ONLY that conjugated form (or auxiliary + participle if the tense requires it), not the full sentence.

Past (distribute across the 7 items):
- Pretérito indefinido, pretérito imperfecto, pretérito perfecto, pluscuamperfecto

Present (distribute across the 7 items):
- Presente de indicativo, presente perfecto, presente progresivo

Future (distribute across the 7 items):
- Futuro simple, condicional simple

Translation — English → Spanish (7 exercises as JSON objects):
- Each item forces production (full translation), not recognition; one main verb or tense choice.
- When specifying a verb, prefer irregular verbs (ser, ir, estar, tener, hacer, poder, decir,
  venir, poner, querer, ver, dar, saber, traer, etc.).
- \"prompt\": one string with (1) a complete English sentence, then (2) exactly ONE constraint
  in Spanish in parentheses.
- The constraint is exactly ONE of:
  a) Required verb: (usar: infinitivo) e.g. (usar: poner)
  b) Required tense: (usar: nombre del tiempo) e.g. (usar: pretérito indefinido)
- \"answer\": the full correct Spanish translation, obeying the constraint.
- Do NOT put the Spanish translation in \"prompt\". Do NOT use ___ in translation prompts.
- Do NOT include more than one constraint per item.

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
