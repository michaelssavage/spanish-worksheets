# flake8: noqa
import logging

from worksheet.services.grammar_pools import GRAMMAR_POOL_GUIDANCE

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You generate Spanish-learning worksheets for intermediate and advanced learners. "
    "Use natural, idiomatic Spanish in realistic contexts, especially work and technology.\n\n"
    "avoid vague sentences. Avoid leaning on common regular verbs like hablar, trabajar, necesitar. "
    "Use many irregular and subjunctive verbs in verb-based sections.\n\n"
    "Ensure all Spanish is correct and natural. Do not use 'ir a + infinitive' in any form.\n\n"
    'Output: each exercise is a JSON object with two fields: "prompt" (string) and "answer". '
    '"answer" is a JSON array of strings. Never omit either field.\n'
    '- For blank-fill sections (every section except "translation"), each string in "answer" is '
    "ONLY the exact word(s) that fill the blank — a correctly conjugated verb or auxiliary + "
    "participle for verb-based grammar points, or the correct preposition/pronoun/connector/word "
    "otherwise — never the full sentence.\n"
    '- For the "translation" section, there is no blank: "prompt" is a full English sentence and '
    'each string in "answer" is a full, natural Spanish translation of it.\n'
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

THEME_POOLS = [
    # Daily life
    ["la rutina diaria", "las tareas de casa", "los horarios"],
    ["la comida", "cocinar", "hacer la compra"],
    ["el transporte", "el tráfico", "los viajes en tren"],
    ["el tiempo", "las estaciones", "la ropa"],
    # Social life
    ["la familia", "las reuniones familiares", "los recuerdos"],
    ["los amigos", "quedar", "hacer planes"],
    ["cumpleaños", "fiestas", "regalos"],
    ["las vacaciones", "los hoteles", "las excursiones"],
    # Work
    ["reuniones", "decisiones de equipo", "conflictos laborales"],
    ["clientes", "negociaciones", "contratos"],
    ["plazos", "prioridades", "cambios de última hora"],
    ["entrevistas de trabajo", "compañeros", "teletrabajo"],
    # Software
    ["bugs", "debugging", "errores en producción"],
    ["revisiones de código", "pull requests", "comentarios"],
    ["despliegues", "pruebas", "automatización"],
    # Health
    ["el médico", "los síntomas", "los medicamentos"],
    ["el deporte", "el ejercicio", "las lesiones"],
    ["el sueño", "el estrés", "el cansancio"],
    # Money
    ["finanzas personales", "ahorrar", "gastos imprevistos"],
    ["el banco", "pagos", "facturas"],
    ["compras", "ofertas", "devoluciones"],
    # Communication
    ["mensajes malinterpretados", "malentendidos", "discusiones"],
    ["dar consejos", "pedir ayuda", "explicar un problema"],
    # Decisions
    ["errores", "decisiones difíciles", "consecuencias"],
    ["riesgos", "oportunidades", "cambios importantes"],
    # Free time
    ["películas", "series", "libros"],
    ["videojuegos", "juegos de mesa", "aficiones"],
    ["música", "conciertos", "festivales"],
    # Travel
    ["el aeropuerto", "el hotel", "hacer turismo"],
    ["viajes por carretera", "mapas", "imprevistos"],
    # Home
    ["la casa", "las reparaciones", "los vecinos"],
    ["mudanzas", "decoración", "muebles"],
    # Shopping
    ["la ropa", "las tallas", "devolver un producto"],
    ["el supermercado", "la lista de la compra", "las ofertas"],
    # Education
    ["aprender idiomas", "los exámenes", "los profesores"],
]


ITEMS_PER_POOL = 5

TRANSLATION_KEY = "translation"
TRANSLATION_ITEMS = 5
TRANSLATION_GUIDANCE = (
    'Each "prompt" is a natural English sentence (no blank) that fits the themes above. Each '
    'string in "answer" is a complete, natural Spanish translation of that sentence — add '
    "alternate natural phrasings as extra strings if more than one exists."
)

_EMPTY_ITEM = '{"prompt": "", "answer": [""]}'


def _schema_section(key: str, item_count: int) -> str:
    items = ",\n    ".join([_EMPTY_ITEM] * item_count)
    return f'"{key}": [\n    {items}\n  ]'


def build_user_prompt(themes: list[str], grammar_pools: list[str]) -> str:
    theme_block = ", ".join(themes)
    pool_instructions = "\n\n".join(
        f'"{pool}" ({ITEMS_PER_POOL} exercises) — {GRAMMAR_POOL_GUIDANCE[pool]}'
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
- {TRANSLATION_GUIDANCE}

Worksheet rules (grammar-point sections above, NOT "{TRANSLATION_KEY}"):
- Spanish only in prompts and answers.
- Do NOT use obvious mistakes like "yo sabo" or "yo cabo".
- Each \"answer\" is a JSON array of non-empty strings (one or more).
- Each \"prompt\" contains exactly ONE blank, written as: ___ (with a parenthetical infinitive
  hint when the blank is a verb, e.g. ___ (hacer); no parenthetical when it isn't). No more, no
  fewer than one blank.
- The blank replaces only the missing word(s) described above for that section; each string in
  \"answer\" is ONLY those word(s), not the full sentence. If multiple answers are acceptable, use
  multiple strings in \"answer\" (never one string with \" | \").
- Intentional ambiguity only when grammatical (e.g. acceptable tense/aspect alternates or
  synonymous connectors); then list every acceptable answer in \"answer\".

Translation section rules:
- "{TRANSLATION_KEY}" prompts are English, contain NO blank, and are unrelated to the grammar
  points above.
- "{TRANSLATION_KEY}" answers are Spanish only, each a full sentence translation.
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


def build_payload(themes: list[str], grammar_pools: list[str]) -> list[dict]:
    logger.debug(
        "Building payload with themes: %s, grammar_pools: %s", themes, grammar_pools
    )

    payload = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_prompt(themes, grammar_pools)},
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
