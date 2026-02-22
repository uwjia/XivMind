---
name: citation-generator
description: Generate citations in various academic formats (APA, MLA, IEEE, BibTeX)
icon: quote
category: writing
requires_paper: true
metadata:
  {
    "xivmind": {
      "input_schema": {
        "type": "object",
        "properties": {
          "format": {
            "type": "string",
            "enum": ["apa", "mla", "ieee", "bibtex"],
            "default": "apa",
            "description": "Citation format"
          }
        }
      }
    }
  }
---

# Citation Generator Skill

Generate citations in various academic formats.

## Usage

This skill requires paper context. It will generate citations for the provided paper(s).

## Parameters

- `format`: Citation format
  - `apa`: APA 7th edition
  - `mla`: MLA 9th edition
  - `ieee`: IEEE format
  - `bibtex`: BibTeX format

## Template

```prompt
Generate a citation for the following paper in {format} format:

Title: {paper.title}
Authors: {paper.authors}
Published: {paper.published}
arXiv ID: {paper.id}
URL: {paper.abs_url}

{if format == "apa"}
Use APA 7th edition format:
Author, A. A., & Author, B. B. (Year). Title of article. Source.
{elif format == "mla"}
Use MLA 9th edition format:
Author, A. A., and B. B. Author. "Title of Article." Source, Year.
{elif format == "ieee"}
Use IEEE format:
[1] A. A. Author and B. B. Author, "Title of article," Source, Year.
{else}
Use BibTeX format:
@article{key,
  author = {...},
  title = {...},
  journal = {...},
  year = {...}
}
{endif}
```
