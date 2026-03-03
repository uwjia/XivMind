MEMORY_EXTRACTION_PROMPT = """You are a memory extraction assistant. Please analyze the following conversation and extract user preferences, research interests, and important information.

## Current User Profile
{current_profile}

## Conversation Content
User: {user_message}
Assistant: {assistant_message}

## Task
Please analyze this conversation and extract the following information (if any):

1. **User Preferences**: Any preferences expressed by the user, such as language preference, summary style preference, etc.
2. **Research Interests**: User's research areas, topics of interest, etc.
3. **Important Facts**: Any important information mentioned by the user that should be remembered

## Output Format
Please output in JSON format with the following fields:
```json
{{
    "user_preferences": ["preference1", "preference2"],
    "research_interests": ["interest1", "interest2"],
    "important_facts": ["fact1", "fact2"],
    "should_update_core": true/false,
    "importance_score": 0.0-1.0
}}
```

Notes:
- If no information is extracted for a category, return an empty array for that field
- should_update_core indicates whether the user's core profile needs to be updated
- importance_score indicates the importance of this conversation (between 0-1)
- Output only JSON, no other content
"""

MEMORY_CONTEXT_INJECTION_PROMPT = """## User Memory Context

The following is known information about the user, please refer to it when responding:

{memory_context}

---
"""

CORE_MEMORY_SYSTEM_PROMPT = """You are an academic paper assistant. The following is the user's personal preferences and background information, please refer to it when responding:

{core_memory_context}

Please adjust your response style and content according to the user's preferences.
"""

RECALL_MEMORY_SEARCH_PROMPT = """Based on the user's conversation history, the following is the most relevant historical information to the current question:

{recall_context}

Please refer to this historical information when responding to maintain conversation continuity.
"""

ARCHIVAL_MEMORY_SEARCH_PROMPT = """The user's knowledge base contains the following relevant information:

{archival_context}

Please refer to this knowledge when responding to provide more accurate and personalized answers.
"""

MEMORY_SUMMARY_PROMPT = """Please merge the following memory entries into a concise summary:

{memories}

Requirements:
1. Keep key information
2. Remove duplicate content
3. Sort by importance
4. Output no more than 200 words

Summary:
"""

MEMORY_FORGET_CRITERIA = """
Criteria for determining whether a memory should be forgotten:
1. Information is outdated or no longer relevant
2. User explicitly states it's no longer needed
3. Duplicate with other memories
4. Importance score below threshold and not accessed for a long time
"""

MEMORY_IMPORTANCE_SCORING_PROMPT = """Please evaluate the importance of the following conversation content:

Conversation Content:
{content}

Please give an importance score between 0-1 based on the following criteria:
- 0.0-0.3: General greetings or small talk
- 0.3-0.5: Routine Q&A
- 0.5-0.7: Contains useful research information
- 0.7-0.9: Contains user preferences or important research background
- 0.9-1.0: Key research findings or information user explicitly asked to remember

Output only the score number, no other content.
"""
