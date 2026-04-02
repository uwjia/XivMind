DAILY_SUMMARY_PROMPT_EN = """You are an expert research analyst. Analyze the following {count} papers from arXiv for {date}.

Papers (title and abstract only):
{papers}

Provide a concise daily summary (2-3 paragraphs) covering:
1. What are the main research themes today?
2. What are the emerging trends or notable advances?
3. Any interesting patterns or observations?

IMPORTANT: Write your summary in English. All text content must be in English.

FORMAT: Return pure JSON object directly. Do NOT use markdown code blocks (no ```json or ```). Do NOT add any prefix text.

Return format:
{{
  "summary": "Your summary here...",
  "main_themes": ["theme1", "theme2", "theme3"],
  "paper_count": {count}
}}
"""

TREND_ANALYSIS_PROMPT_EN = """Analyze the following papers and identify 3-5 major research trends.

Papers:
{papers}

For each trend, provide:
1. Trend name (concise, 2-4 words)
2. Brief description (1 sentence)
3. Paper count
4. List of paper IDs (copy from the paper list)

CRITICAL - DATA INTEGRITY:
- For each trend, copy the paper_id values EXACTLY from the paper list above
- DO NOT invent, modify, or truncate any paper_id

IMPORTANT: All text content (names, descriptions) must be in English.

FORMAT: Return pure JSON object directly. Do NOT use markdown code blocks (no ```json or ```). Do NOT add any prefix text.

Return format:
{{
  "trends": [
    {{
      "name": "Efficient Attention",
      "description": "Methods to reduce attention computation complexity",
      "paper_count": 15,
      "paper_ids": ["2401.12345", "2401.12346", "2401.12347"]
    }}
  ]
}}
"""

HIGH_VALUE_PROMPT_EN = """Identify the top 5 most innovative/valuable papers from the following list.

Papers:
{papers}

Consider:
1. Novel methodology or approach
2. Significant improvements over existing methods
3. New problem formulations
4. Interesting cross-domain applications

CRITICAL - DATA INTEGRITY:
- For each paper in your response, you MUST copy the paper_id and title values EXACTLY from the paper list above
- Example: If paper list shows paper_id: "2401.12345" and title: "Some Paper Title", your response MUST use these exact values
- DO NOT invent, modify, or truncate any paper_id or title
- paper_id and title MUST come from the SAME paper entry in the list

FORMAT: Return pure JSON object directly. Do NOT use markdown code blocks (no ```json or ```). Do NOT add any prefix text.

Return format:
{{
  "high_value_papers": [
    {{
      "paper_id": "COPY FROM paper_id FIELD IN PAPER LIST",
      "title": "COPY FROM title FIELD IN PAPER LIST",
      "innovation_type": "novel_method|significant_improvement|new_problem|cross_domain",
      "innovation_description": "Brief description of what makes this paper innovative",
      "confidence": 0.85
    }}
  ]
}}
"""

SINGLE_PAPER_HIGH_VALUE_PROMPT_EN = """Analyze this paper to determine its innovation and value.

Paper:
paper_id: "{paper_id}"
title: "{title}"
abstract: "{abstract}"

Consider:
1. Novel methodology or approach
2. Significant improvements over existing methods
3. New problem formulations
4. Interesting cross-domain applications

FORMAT: Return pure JSON object directly. Do NOT use markdown code blocks (no ```json or ```). Do NOT add any prefix text.

Return format:
{{
  "innovation_type": "novel_method|significant_improvement|new_problem|cross_domain",
  "innovation_description": "Brief description of what makes this paper innovative",
  "confidence": 0.85
}}
"""

INTEREST_MATCHING_PROMPT_EN = """Match papers to user's research interests.

User's Research Interests:
{interests}

Papers:
{papers}

For each paper, calculate a relevance score (0-100) based on how well it matches the user's interests.
Return only papers with score >= 70.

CRITICAL - DATA INTEGRITY:
- For each paper in your response, you MUST copy the paper_id and title values EXACTLY from the paper list above
- Example: If paper list shows paper_id: "2401.12345" and title: "Some Paper Title", your response MUST use these exact values
- DO NOT invent, modify, or truncate any paper_id or title
- paper_id and title MUST come from the SAME paper entry in the list

FORMAT: Return pure JSON object directly. Do NOT use markdown code blocks (no ```json or ```). Do NOT add any prefix text.

Return format:
{{
  "recommendations": [
    {{
      "paper_id": "COPY FROM paper_id FIELD IN PAPER LIST",
      "title": "COPY FROM title FIELD IN PAPER LIST",
      "relevance_score": 95,
      "matched_interests": ["Machine Learning", "NLP"],
      "reason": "Brief explanation of why this paper matches"
    }}
  ],
  "total_matched": 10
}}
"""

SINGLE_PAPER_INTEREST_PROMPT_EN = """Analyze this paper to determine how well it matches the user's research interests.

User's Research Interests:
{interests}

Paper:
paper_id: "{paper_id}"
title: "{title}"
abstract: "{abstract}"

Calculate a relevance score (0-100) based on how well this paper matches the user's interests.

FORMAT: Return pure JSON object directly. Do NOT use markdown code blocks (no ```json or ```). Do NOT add any prefix text.

Return format:
{{
  "relevance_score": 85,
  "matched_interests": ["Machine Learning", "NLP"],
  "reason": "Brief explanation of why this paper matches the interests"
}}
"""

DAILY_SUMMARY_PROMPT_ZH = """你是一位专业的研究分析师。请分析以下来自 arXiv 的 {count} 篇论文（日期：{date}）。

论文（仅标题和摘要）：
{papers}

请提供一份简洁的每日摘要（2-3段），涵盖以下内容：
1. 今天的主要研究主题是什么？
2. 有哪些新兴趋势或显著进展？
3. 有什么有趣的模式或观察？

【重要】请务必使用中文撰写摘要内容。所有文本内容都必须是中文。

【格式要求】直接返回纯 JSON 对象，不要使用 markdown 代码块（不要用 ```json 或 ```），不要添加任何前缀文字。

返回格式：
{{
  "summary": "你的中文摘要内容...",
  "main_themes": ["中文主题1", "中文主题2", "中文主题3"],
  "paper_count": {count}
}}
"""

TREND_ANALYSIS_PROMPT_ZH = """分析以下论文并识别 3-5 个主要研究趋势。

论文：
{papers}

对于每个趋势，请提供：
1. 趋势名称（简洁，2-4个词）
2. 简要描述（一句话）
3. 论文数量
4. 论文ID列表（从论文列表中复制）

【关键 - 数据完整性】
- 每个趋势的 paper_ids 必须从上面的论文列表中逐字复制
- 禁止编造、修改或截断任何 paper_id

【重要】请务必使用中文撰写趋势名称和描述。

【格式要求】直接返回纯 JSON 对象，不要使用 markdown 代码块（不要用 ```json 或 ```），不要添加任何前缀文字。

返回格式：
{{
  "trends": [
    {{
      "name": "高效注意力机制",
      "description": "降低注意力计算复杂度的方法",
      "paper_count": 15,
      "paper_ids": ["2401.12345", "2401.12346", "2401.12347"]
    }}
  ]
}}
"""

HIGH_VALUE_PROMPT_ZH = """从以下列表中识别出 5 篇最具创新性/价值的论文。

论文：
{papers}

请考虑：
1. 新颖的方法或途径
2. 对现有方法的显著改进
3. 新的问题表述
4. 有趣的跨领域应用

【关键 - 数据完整性】
- 返回的每篇论文，必须从上面的论文列表中逐字复制 paper_id 和 title 的值
- 例如：如果论文列表显示 paper_id: "2401.12345" 和 title: "Some Paper Title"，你的回答必须使用这些完全相同的值
- 禁止编造、修改或截断任何 paper_id 或 title
- paper_id 和 title 必须来自论文列表中的同一条记录

【格式要求】直接返回纯 JSON 对象，不要使用 markdown 代码块（不要用 ```json 或 ```），不要添加任何前缀文字。

返回格式：
{{
  "high_value_papers": [
    {{
      "paper_id": "从论文列表的 paper_id 字段复制",
      "title": "从论文列表的 title 字段复制",
      "innovation_type": "novel_method|significant_improvement|new_problem|cross_domain",
      "innovation_description": "这篇论文的创新之处",
      "confidence": 0.85
    }}
  ]
}}
"""

SINGLE_PAPER_HIGH_VALUE_PROMPT_ZH = """分析这篇论文的创新性和价值。

论文：
paper_id: "{paper_id}"
title: "{title}"
abstract: "{abstract}"

请考虑：
1. 新颖的方法或途径
2. 对现有方法的显著改进
3. 新的问题表述
4. 有趣的跨领域应用

【格式要求】直接返回纯 JSON 对象，不要使用 markdown 代码块（不要用 ```json 或 ```），不要添加任何前缀文字。

返回格式：
{{
  "innovation_type": "novel_method|significant_improvement|new_problem|cross_domain",
  "innovation_description": "这篇论文的创新之处",
  "confidence": 0.85
}}
"""

INTEREST_MATCHING_PROMPT_ZH = """将论文与用户的研究兴趣进行匹配。

用户的研究兴趣：
{interests}

论文：
{papers}

对于每篇论文，根据其与用户兴趣的匹配程度计算一个相关性分数（0-100）。
仅返回分数 >= 70 的论文。

【关键 - 数据完整性】
- 返回的每篇论文，必须从上面的论文列表中逐字复制 paper_id 和 title 的值
- 例如：如果论文列表显示 paper_id: "2401.12345" 和 title: "Some Paper Title"，你的回答必须使用这些完全相同的值
- 禁止编造、修改或截断任何 paper_id 或 title
- paper_id 和 title 必须来自论文列表中的同一条记录

【格式要求】直接返回纯 JSON 对象，不要使用 markdown 代码块（不要用 ```json 或 ```），不要添加任何前缀文字。

返回格式：
{{
  "recommendations": [
    {{
      "paper_id": "从论文列表的 paper_id 字段复制",
      "title": "从论文列表的 title 字段复制",
      "relevance_score": 95,
      "matched_interests": ["机器学习", "自然语言处理"],
      "reason": "这篇论文与您的研究兴趣有哪些关联"
    }}
  ],
  "total_matched": 10
}}
"""

SINGLE_PAPER_INTEREST_PROMPT_ZH = """分析这篇论文与用户研究兴趣的匹配程度。

用户的研究兴趣：
{interests}

论文：
paper_id: "{paper_id}"
title: "{title}"
abstract: "{abstract}"

根据论文与用户兴趣的匹配程度计算一个相关性分数（0-100）。

【格式要求】直接返回纯 JSON 对象，不要使用 markdown 代码块（不要用 ```json 或 ```），不要添加任何前缀文字。

返回格式：
{{
  "relevance_score": 85,
  "matched_interests": ["机器学习", "自然语言处理"],
  "reason": "简要说明这篇论文为什么与兴趣匹配"
}}
"""

PROMPTS = {
    "en": {
        "summary": DAILY_SUMMARY_PROMPT_EN,
        "trends": TREND_ANALYSIS_PROMPT_EN,
        "high_value": HIGH_VALUE_PROMPT_EN,
        "high_value_single": SINGLE_PAPER_HIGH_VALUE_PROMPT_EN,
        "recommend": INTEREST_MATCHING_PROMPT_EN,
        "recommend_single": SINGLE_PAPER_INTEREST_PROMPT_EN,
    },
    "zh": {
        "summary": DAILY_SUMMARY_PROMPT_ZH,
        "trends": TREND_ANALYSIS_PROMPT_ZH,
        "high_value": HIGH_VALUE_PROMPT_ZH,
        "high_value_single": SINGLE_PAPER_HIGH_VALUE_PROMPT_ZH,
        "recommend": INTEREST_MATCHING_PROMPT_ZH,
        "recommend_single": SINGLE_PAPER_INTEREST_PROMPT_ZH,
    },
}


def get_prompt(task_name: str, language: str = "en") -> str:
    return PROMPTS.get(language, PROMPTS["en"]).get(task_name)
