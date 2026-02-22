from .summary_skill import SummarySkill
from .translation_skill import TranslationSkill
from .citation_skill import CitationSkill
from .related_skill import RelatedPapersSkill
from ..registry import SkillRegistry

SkillRegistry.register(SummarySkill)
SkillRegistry.register(TranslationSkill)
SkillRegistry.register(CitationSkill)
SkillRegistry.register(RelatedPapersSkill)

__all__ = ["SummarySkill", "TranslationSkill", "CitationSkill", "RelatedPapersSkill"]
