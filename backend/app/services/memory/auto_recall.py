import logging
from typing import List, Dict, Any
from collections import defaultdict

from .types import (
    MemoryConfig,
    MemoryContext,
    MemorySearchResult,
    MemoryCategory,
)
from .retriever import MemoryRetriever

logger = logging.getLogger(__name__)


class AutoRecallService:
    def __init__(self):
        self.retriever = MemoryRetriever()

    async def recall_for_query(
        self,
        query: str,
        user_id: str,
        config: MemoryConfig,
    ) -> MemoryContext:
        if not config.auto_recall:
            return MemoryContext(memories=[], context_string="")

        try:
            memories = await self.retriever.retrieve_relevant_memories(
                query=query,
                user_id=user_id,
                top_k=config.recall_top_k,
                min_score=config.recall_min_score,
            )

            context_string = self._build_context(memories)

            logger.debug(f"Auto-recalled {len(memories)} memories for query")
            return MemoryContext(
                memories=memories,
                context_string=context_string
            )

        except Exception as e:
            logger.error(f"Failed to auto-recall memories: {e}")
            return MemoryContext(memories=[], context_string="")

    def _build_context(self, memories: List[MemorySearchResult]) -> str:
        if not memories:
            return ""

        parts = []

        by_category = defaultdict(list)
        for m in memories:
            by_category[m.category.value].append(m)

        if by_category.get("preference"):
            prefs = by_category["preference"]
            pref_lines = [f"- {p.content[:200]}{'...' if len(p.content) > 200 else ''}" for p in prefs[:3]]
            parts.append(f"[User Preferences]\n" + "\n".join(pref_lines))

        if by_category.get("fact"):
            facts = by_category["fact"]
            fact_lines = [f"- {f.content[:200]}{'...' if len(f.content) > 200 else ''}" for f in facts[:3]]
            parts.append(f"[Important Facts]\n" + "\n".join(fact_lines))

        if by_category.get("context"):
            contexts = by_category["context"]
            ctx_lines = [f"- {c.content[:200]}{'...' if len(c.content) > 200 else ''}" for c in contexts[:2]]
            parts.append(f"[Related Context]\n" + "\n".join(ctx_lines))

        if by_category.get("insight"):
            insights = by_category["insight"]
            insight_lines = [f"- {i.content[:200]}{'...' if len(i.content) > 200 else ''}" for i in insights[:2]]
            parts.append(f"[Insights]\n" + "\n".join(insight_lines))

        if by_category.get("task"):
            tasks = by_category["task"]
            task_lines = [f"- {t.content[:200]}{'...' if len(t.content) > 200 else ''}" for t in tasks[:2]]
            parts.append(f"[Task History]\n" + "\n".join(task_lines))

        return "\n\n".join(parts)

    async def recall_by_category(
        self,
        query: str,
        user_id: str,
        category: MemoryCategory,
        top_k: int = 3,
    ) -> List[MemorySearchResult]:
        try:
            all_memories = await self.retriever.retrieve_relevant_memories(
                query=query,
                user_id=user_id,
                top_k=top_k * 3,
            )

            filtered = [m for m in all_memories if m.category == category]
            return filtered[:top_k]

        except Exception as e:
            logger.error(f"Failed to recall by category: {e}")
            return []

    def inject_context_to_prompt(
        self,
        prompt: str,
        context: MemoryContext,
    ) -> str:
        if not context.context_string:
            return prompt

        memory_header = """## User Memory Context
The following information has been recalled from the user's memory. Use it to provide personalized responses.

{context}
---

"""
        return memory_header.format(context=context.context_string) + prompt
