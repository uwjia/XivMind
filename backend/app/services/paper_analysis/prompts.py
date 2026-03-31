
ANALYSIS_PROMPTS = {
    "summary": {
        "en": """Analyze the following academic paper and generate a comprehensive summary. YOU MUST RESPOND IN ENGLISH.

Paper Title: {title}
Authors: {authors}
Abstract: {abstract}

Please provide:
1. A clear and concise summary of the paper (2-3 paragraphs)
2. Focus on the main contributions and findings
3. Explain the significance of the work

Respond in JSON format:
{{
    "summary": "Your comprehensive summary here..."
}}""",
        "zh": """请用中文分析以下学术论文并生成综合摘要。你必须用中文回复。

论文标题：{title}
作者：{authors}
摘要：{abstract}

请提供：
1. 清晰简洁的论文摘要（2-3段）
2. 重点说明主要贡献和发现
3. 解释工作的重要性

请以JSON格式回复：
{{
    "summary": "您的综合摘要..."
}}"""
    },
    "keypoints": {
        "en": """Analyze the following academic paper and extract the key points. YOU MUST RESPOND IN ENGLISH.

Paper Title: {title}
Authors: {authors}
Abstract: {abstract}

Please extract:
1. 3-5 key points/contributions of the paper
2. For each key point, provide a title, description, and importance level (high/medium/low)

Respond in JSON format:
{{
    "key_points": [
        {{
            "title": "Key point title",
            "description": "Detailed description",
            "importance": "high"
        }}
    ]
}}""",
        "zh": """请用中文分析以下学术论文并提取关键点。你必须用中文回复。

论文标题：{title}
作者：{authors}
摘要：{abstract}

请提取：
1. 3-5个论文的关键点/贡献
2. 每个关键点需提供标题、描述和重要程度（高/中/低）

请以JSON格式回复：
{{
    "key_points": [
        {{
            "title": "关键点标题",
            "description": "详细描述",
            "importance": "high"
        }}
    ]
}}"""
    },
    "methodology": {
        "en": """Analyze the following academic paper and describe its methodology. YOU MUST RESPOND IN ENGLISH.

Paper Title: {title}
Authors: {authors}
Abstract: {abstract}

Please analyze:
1. The research methodology used
2. Key techniques or approaches
3. Datasets or experimental setup (if mentioned)
4. Evaluation methods

Respond in JSON format:
{{
    "methodology": "Detailed methodology analysis..."
}}""",
        "zh": """请用中文分析以下学术论文并描述其方法论。你必须用中文回复。

论文标题：{title}
作者：{authors}
摘要：{abstract}

请分析：
1. 使用的研究方法
2. 关键技术或方法
3. 数据集或实验设置（如有提及）
4. 评估方法

请以JSON格式回复：
{{
    "methodology": "详细的方法论分析..."
}}"""
    },
    "questions_conclusions": {
        "en": """Analyze the following academic paper and identify research questions and conclusions. YOU MUST RESPOND IN ENGLISH.

Paper Title: {title}
Authors: {authors}
Abstract: {abstract}

Please identify:
1. The main research questions addressed in the paper
2. The corresponding conclusions for each question

Respond in JSON format:
{{
    "questions_and_conclusions": [
        {{
            "question": "Research question 1",
            "conclusion": "Main conclusion for this question"
        }}
    ]
}}""",
        "zh": """请用中文分析以下学术论文并识别研究问题和结论。你必须用中文回复。

论文标题：{title}
作者：{authors}
摘要：{abstract}

请识别：
1. 论文解决的主要研究问题
2. 每个问题对应的结论

请以JSON格式回复：
{{
    "questions_and_conclusions": [
        {{
            "question": "研究问题1",
            "conclusion": "该问题的主要结论"
        }}
    ]
}}"""
    },
    "full": {
        "en": """Analyze the following academic paper comprehensively. YOU MUST RESPOND IN ENGLISH.

Paper Title: {title}
Authors: {authors}
Abstract: {abstract}

Please provide a comprehensive analysis including:
1. A clear summary of the paper
2. 3-5 key points/contributions
3. Methodology analysis
4. Research questions and conclusions

Respond in JSON format:
{{
    "summary": "Comprehensive summary...",
    "key_points": [
        {{
            "title": "Key point title",
            "description": "Detailed description",
            "importance": "high"
        }}
    ],
    "methodology": "Methodology analysis...",
    "questions_and_conclusions": [
        {{
            "question": "Research question",
            "conclusion": "Main conclusion"
        }}
    ]
}}""",
        "zh": """请用中文全面分析以下学术论文。你必须用中文回复。

论文标题：{title}
作者：{authors}
摘要：{abstract}

请提供全面分析，包括：
1. 清晰的论文摘要
2. 3-5个关键点/贡献
3. 方法论分析
4. 研究问题和结论

请以JSON格式回复：
{{
    "summary": "综合摘要...",
    "key_points": [
        {{
            "title": "关键点标题",
            "description": "详细描述",
            "importance": "high"
        }}
    ],
    "methodology": "方法论分析...",
    "questions_and_conclusions": [
        {{
            "question": "研究问题",
            "conclusion": "主要结论"
        }}
    ]
}}"""
    }
}


