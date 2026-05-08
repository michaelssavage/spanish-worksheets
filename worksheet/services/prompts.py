# flake8: noqa
import logging

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You generate Spanish-learning worksheets for intermediate and advanced learners. "
    "Use natural, idiomatic Spanish in realistic contexts, especially work and technology.\n\n"
    "avoid vague sentences. Avoid leaning on common regular verbs like hablar, trabajar, necesitar. "
    "Use many irregular and subjunctive verbs in conjugation sections.\n\n"
    "Ensure all Spanish is correct and natural. Do not use 'ir a + infinitive' in any form.\n\n"
    'Output: each exercise is a JSON object with two fields: "prompt" (string) and "answer". '
    'For translation items, "answer" is one full correct Spanish sentence as a string. '
    'For conjugation items (blanks), "answer" is a JSON array of strings. Never omit either field.\n'
    '- For conjugation items (blanks), each string in "answer" is ONLY a correctly conjugated '
    "verb or auxiliary + participle when the tense requires it — never the full sentence.\n"
    "- For conjugation, if several forms are acceptable, put each form as its own string in the array. Do not "
    'join alternatives with " | " inside one string.\n'
    "- Conjugation prompts must include an explicit subject so person and number are clear: "
    "either a subject pronoun (Yo, Tú, Él, Ella, Usted, Nosotros/as, Vosotros/as, Ellos/as, "
    "Ustedes) or a noun phrase that fixes person and number (e.g. Mi jefa, Los clientes). "
    "Do not omit the subject in a way that leaves who conjugates unclear.\n"
    "- If ambiguity is intentional, it must be grammatical only (e.g. acceptable tense/aspect "
    "alternates), not from a missing subject; include every acceptable conjugation as a "
    'separate string in "answer".\n\n'
    "Follow the user's JSON schema and section instructions exactly. Output valid JSON only when asked."
)

THEME_POOLS = [
    ["reuniones", "decisiones de equipo", "conflictos laborales"],
    ["plazos", "entregas urgentes", "errores en proyectos"],
    ["bugs", "debugging", "errores en producción"],
    ["deportes", "partidos", "juegos en equipo"],
    ["revisiones de código", "pull requests", "comentarios"],
    ["finanzas personales", "gastos imprevistos", "deudas"],
    ["mensajes malinterpretados", "falta de comunicación", "urgencias"],
    ["clientes", "negociaciones", "contratos"],
    ["problemas de salud", "cansancio extremo", "falta de sueño"],
    ["pagos", "facturas", "retrasos"],
    ["errores graves", "decisiones difíciles", "consecuencias"],
    ["el tiempo libre", "planes cancelados a última hora", "quedadas improvisadas"],
    ["cumpleaños en la oficina", "pasteles traídos de casa", "vaquinas para regalos"],
    ["la resaca del lunes", "el viernes por la tarde", "sobrevivir hasta las 6"],
]


def build_user_prompt(themes: list[str]) -> str:
    theme_block = ", ".join(themes)

    prompt = f"""
Themes:
{theme_block}

Worksheet rules (all sections):
- Spanish only in answers and in conjugation prompts.
- Do NOT use obvious mistakes like "yo sabo" or "yo cabo".
- In past/present/future sections, each \"answer\" is a JSON array of non-empty strings (one or more).
- In translation, each \"answer\" is exactly one non-empty string, not an array.

Conjugation sections — past, present, future (8 exercises each as JSON objects):
- Shared: each \"prompt\" contains exactly ONE blank, written as: ___ (infinitive). No more, no fewer.
- Shared: the blank replaces the verb to conjugate; each string in \"answer\" is ONLY that conjugated form (or auxiliary + participle if the tense requires it), not the full sentence. If multiple conjugations are acceptable, use multiple strings in \"answer\" (never one string with \" | \").
- Explicit subject: each conjugation \"prompt\" must show who acts — subject pronoun
  (Yo, Tú, Él, …) or a noun phrase that fixes person and number. Do not drop the subject in a way that makes the expected conjugation ambiguous.
- Intentional ambiguity only when grammatical (e.g. tense/aspect alternates); then list every acceptable form in \"answer\".

Past (distribute across the 8 items):
- Pretérito indefinido, pretérito imperfecto, pretérito perfecto, pluscuamperfecto

Present (distribute across the 8 items):
- Presente de indicativo, presente perfecto, presente progresivo

Future (distribute across the 8 items):
- Futuro simple, condicional simple

Translation — English → Spanish (8 exercises as JSON objects):
- Each item forces production (full translation), not recognition; one main verb or tense choice.
- When specifying a verb, prefer irregular verbs (ser, ir, estar, tener, hacer, poder, decir,
  venir, poner, querer, ver, dar, saber, traer, etc.).
- \"prompt\": one string with (1) a complete English sentence, then (2) exactly ONE constraint
  in Spanish in parentheses.
- The constraint is exactly ONE of:
  a) Required verb: (usar: infinitivo) e.g. (usar: poner)
  b) Required tense: (usar: nombre del tiempo) e.g. (usar: pretérito indefinido)
- \"answer\": one full correct Spanish translation string obeying the constraint. Choose one best wording; do not return an array.
- Do NOT put the Spanish translation in \"prompt\". Do NOT use ___ in translation prompts.
- Do NOT include more than one constraint per item.

Fill in the following JSON exactly.
Do not add, remove, or rename keys.
Do not add text outside the JSON.

{{
  "past": [
    {{"prompt": "", "answer": [""]}},
    {{"prompt": "", "answer": [""]}},
    {{"prompt": "", "answer": [""]}},
    {{"prompt": "", "answer": [""]}},
    {{"prompt": "", "answer": [""]}},
    {{"prompt": "", "answer": [""]}},
    {{"prompt": "", "answer": [""]}},
    {{"prompt": "", "answer": [""]}}
  ],
  "present": [
    {{"prompt": "", "answer": [""]}},
    {{"prompt": "", "answer": [""]}},
    {{"prompt": "", "answer": [""]}},
    {{"prompt": "", "answer": [""]}},
    {{"prompt": "", "answer": [""]}},
    {{"prompt": "", "answer": [""]}},
    {{"prompt": "", "answer": [""]}},
    {{"prompt": "", "answer": [""]}}
  ],
  "future": [
    {{"prompt": "", "answer": [""]}},
    {{"prompt": "", "answer": [""]}},
    {{"prompt": "", "answer": [""]}},
    {{"prompt": "", "answer": [""]}},
    {{"prompt": "", "answer": [""]}},
    {{"prompt": "", "answer": [""]}},
    {{"prompt": "", "answer": [""]}},
    {{"prompt": "", "answer": [""]}}
  ],
  "translation": [
    {{"prompt": "", "answer": ""}},
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


def build_custom_user_prompt(request_text: str) -> str:
    prompt = f"""
Custom exercise request:
{request_text}

Create exactly 8 Spanish conjugation exercises matching the request.

Rules:
- Use natural, idiomatic Spanish in realistic contexts.
- Each "prompt" must be Spanish only.
- Each "prompt" must contain exactly ONE blank, written as: ___ (infinitive).
- The blank replaces the verb to conjugate.
- Each prompt must include an explicit subject so person and number are clear.
- Each "answer" must be a JSON array of one or more non-empty strings.
- Each answer string is ONLY the correctly conjugated verb, or auxiliary + participle if required.
- If several forms are acceptable, put each form as its own string in the array.
- Do not include full sentences in "answer".
- Do not use "ir a + infinitive" in any form.
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


def build_custom_payload(request_text: str) -> list[dict]:
    logger.debug("Building custom payload for request: %s", request_text)

    payload = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_custom_user_prompt(request_text)},
    ]

    logger.info("Custom payload built successfully")
    return payload
