"""Per-language worksheet configuration.

Everything that differs between Spanish and Catalan worksheets lives here so
prompts, rotators and generation can stay language-agnostic.
"""

from dataclasses import dataclass

from worksheet.models import Worksheet
from worksheet.services.grammar_pools import (
    CATALAN_GRAMMAR_POOL_GUIDANCE,
    CATALAN_GRAMMAR_POOLS,
    SPANISH_GRAMMAR_POOL_GUIDANCE,
    SPANISH_GRAMMAR_POOLS,
)
from worksheet.services.prompts import (
    CATALAN_SYSTEM_PROMPT,
    CATALAN_TRANSLATION_EXAMPLES,
    SPANISH_SYSTEM_PROMPT,
    SPANISH_TRANSLATION_EXAMPLES,
)
from worksheet.services.themes import CATALAN_THEME_POOLS, SPANISH_THEME_POOLS


@dataclass(frozen=True)
class LanguageConfig:
    code: str
    name: str
    system_prompt: str
    translation_examples: str
    obvious_mistakes: str
    hint_example: str
    periphrastic_rule: str
    theme_pools: list[list[str]]
    grammar_pools: list[str]
    grammar_pool_guidance: dict[str, str]
    grammar_index_key: str
    sends_email: bool


SPANISH = LanguageConfig(
    code=Worksheet.Language.SPANISH,
    name="Spanish",
    system_prompt=SPANISH_SYSTEM_PROMPT,
    translation_examples=SPANISH_TRANSLATION_EXAMPLES,
    obvious_mistakes='"yo sabo" or "yo cabo"',
    hint_example="hacer",
    periphrastic_rule='Do not use "ir a + infinitive" in any form.',
    theme_pools=SPANISH_THEME_POOLS,
    grammar_pools=SPANISH_GRAMMAR_POOLS,
    grammar_pool_guidance=SPANISH_GRAMMAR_POOL_GUIDANCE,
    grammar_index_key="grammar_pool_index",
    sends_email=True,
)

CATALAN = LanguageConfig(
    code=Worksheet.Language.CATALAN,
    name="Catalan",
    system_prompt=CATALAN_SYSTEM_PROMPT,
    translation_examples=CATALAN_TRANSLATION_EXAMPLES,
    obvious_mistakes='"jo sabo" or "jo fago"',
    hint_example="fer",
    periphrastic_rule=(
        'Do not use "anar a + infinitive" to express the future; the passat '
        "perifràstic (vaig + infinitive) is fine."
    ),
    theme_pools=CATALAN_THEME_POOLS,
    grammar_pools=CATALAN_GRAMMAR_POOLS,
    grammar_pool_guidance=CATALAN_GRAMMAR_POOL_GUIDANCE,
    grammar_index_key="grammar_pool_index_ca",
    sends_email=False,
)

LANGUAGES: dict[str, LanguageConfig] = {
    SPANISH.code: SPANISH,
    CATALAN.code: CATALAN,
}


def get_language(code: str) -> LanguageConfig:
    """Return the config for a language code; raises KeyError for unknown codes."""
    return LANGUAGES[code]
