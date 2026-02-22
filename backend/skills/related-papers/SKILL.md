---
name: related-papers
description: Find semantically similar papers based on the current paper
icon: search
category: search
requires_paper: true
metadata:
  {
    "xivmind": {
      "input_schema": {
        "type": "object",
        "properties": {
          "top_k": {
            "type": "integer",
            "default": 5,
            "minimum": 1,
            "maximum": 20,
            "description": "Number of related papers to return"
          }
        }
      }
    }
  }
---

# Related Papers Skill

Find semantically similar papers based on the current paper.

## Usage

This skill requires paper context. It will find papers that are semantically similar to the provided paper(s).

## Parameters

- `top_k`: Number of related papers to return (1-20, default: 5)

## Template

```prompt
Find {top_k} papers that are semantically related to the following paper:

Title: {paper.title}
Abstract: {paper.abstract}
Authors: {paper.authors}
Categories: {paper.categories}

Use semantic search to find papers with similar topics, methodologies, or research questions.
Return the most relevant papers with their titles, authors, and brief relevance explanation.
```
