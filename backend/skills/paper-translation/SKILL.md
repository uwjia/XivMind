---
name: paper-translation
description: Translate paper content to different languages
icon: languages
category: writing
requires_paper: true
metadata:
  {
    "xivmind": {
      "input_schema": {
        "type": "object",
        "properties": {
          "target_language": {
            "type": "string",
            "default": "Chinese",
            "description": "Target language for translation"
          },
          "content_type": {
            "type": "string",
            "enum": ["abstract", "full", "title"],
            "default": "abstract",
            "description": "Which content to translate"
          }
        }
      }
    }
  }
---

# Paper Translation Skill

Translate paper content to different languages.

## Usage

This skill requires paper context. It will translate the specified content of the paper.

## Parameters

- `target_language`: Target language for translation (e.g., Chinese, Japanese, German)
- `content_type`: Which content to translate
  - `abstract`: Translate only the abstract
  - `full`: Translate abstract and title with detailed explanation
  - `title`: Translate only the title

## Template

```prompt
Please translate the following paper {content_type} to {target_language}:

Title: {paper.title}
Abstract: {paper.abstract}

{if content_type == "full"}
Please provide:
1. Translated title
2. Translated abstract
3. Key terms and their translations (if translating to Chinese, provide Chinese characters only, no Pinyin)
4. Brief explanation of the main contribution in {target_language}

IMPORTANT: If translating to Chinese, output only Chinese characters (汉字). Do NOT include Pinyin romanization or pronunciation guides.
{elif content_type == "title"}
Please provide only the translated title.

IMPORTANT: If translating to Chinese, output only Chinese characters (汉字). Do NOT include Pinyin romanization or pronunciation guides.
{else}
Please provide:
1. Translated title
2. Translated abstract

Maintain the academic tone and technical accuracy.

IMPORTANT: If translating to Chinese, output only Chinese characters (汉字). Do NOT include Pinyin romanization or pronunciation guides.
{endif}
```
