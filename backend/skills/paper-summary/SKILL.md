---
name: paper-summary
description: Generate a concise summary including research question, methodology, key findings, and conclusions
icon: file-text
category: analysis
requires_paper: true
metadata:
  {
    "xivmind": {
      "input_schema": {
        "type": "object",
        "properties": {
          "detail_level": {
            "type": "string",
            "enum": ["brief", "detailed"],
            "default": "brief",
            "description": "Level of detail for the summary"
          }
        }
      }
    }
  }
---

# Paper Summary Skill

Generate a concise summary of academic papers.

## Usage

This skill requires paper context. It will summarize the provided paper(s).

## Parameters

- `detail_level`: Level of detail for the summary
  - `brief`: Short summary with key points
  - `detailed`: Comprehensive summary with all sections

## Template

```prompt
Please provide a {detail_level} summary of the following paper:

Title: {paper.title}
Abstract: {paper.abstract}

{if detail_level == "detailed"}
Please include:
1. Research Question/Objective
2. Background and Motivation
3. Methodology/Approach
4. Key Findings and Results
5. Contributions and Significance
6. Limitations
7. Conclusions and Future Work

Format the response in clear sections with markdown headings.
{else}
Please include:
1. Research Question
2. Methodology
3. Key Findings
4. Conclusions

Keep the summary concise and to the point.
{endif}
```
