import json
import re
import unicodedata
from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Optional, TypeVar

T = TypeVar('T')


class CodePlatform(Enum):
    GITHUB = "github"
    GITLAB = "gitlab"
    BITBUCKET = "bitbucket"
    HUGGINGFACE = "huggingface"
    GITHUB_PAGES = "github_pages"
    OTHER = "other"


@dataclass
class CodeUrlInfo:
    url: str
    platform: CodePlatform
    owner: Optional[str] = None
    repo: Optional[str] = None


def extract_code_urls(text: str) -> List[CodeUrlInfo]:
    """
    Extract all code repository URLs from text.
    
    Supports:
    - GitHub: https://github.com/owner/repo
    - GitHub Pages: https://owner.github.io/ or https://owner.github.io/project
    - GitLab: https://gitlab.com/owner/repo
    - Bitbucket: https://bitbucket.org/owner/repo
    - Hugging Face: https://huggingface.co/owner/repo
    
    Returns list of CodeUrlInfo with platform, owner, repo info.
    """
    if not text:
        return []
    
    results = []
    seen_urls = set()
    
    patterns = [
        (r'https?://github\.com/([a-zA-Z0-9_-]+)/([a-zA-Z0-9._-]+)', CodePlatform.GITHUB),
        (r'https?://([a-zA-Z0-9_-]+)\.github\.io/?([a-zA-Z0-9._-]*)', CodePlatform.GITHUB_PAGES),
        (r'https?://gitlab\.com/([a-zA-Z0-9_-]+)/([a-zA-Z0-9._-]+)', CodePlatform.GITLAB),
        (r'https?://bitbucket\.org/([a-zA-Z0-9_-]+)/([a-zA-Z0-9._-]+)', CodePlatform.BITBUCKET),
        (r'https?://huggingface\.co/([a-zA-Z0-9_-]+)/([a-zA-Z0-9._-]+)', CodePlatform.HUGGINGFACE),
    ]
    
    for pattern, platform in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if platform == CodePlatform.GITHUB_PAGES:
                owner = match[0]
                repo = match[1] if match[1] else None
                url = f"https://{owner}.github.io"
                if repo:
                    url += f"/{repo}"
            else:
                owner = match[0]
                repo = match[1]
                if platform == CodePlatform.GITHUB:
                    url = f"https://github.com/{owner}/{repo}"
                elif platform == CodePlatform.GITLAB:
                    url = f"https://gitlab.com/{owner}/{repo}"
                elif platform == CodePlatform.BITBUCKET:
                    url = f"https://bitbucket.org/{owner}/{repo}"
                elif platform == CodePlatform.HUGGINGFACE:
                    url = f"https://huggingface.co/{owner}/{repo}"
                else:
                    continue
            
            url = re.sub(r'[.,;:!?)\]}>]+$', '', url)
            url = url.split('?')[0].split('#')[0].rstrip('/')
            
            if url in seen_urls:
                continue
            seen_urls.add(url)
            
            results.append(CodeUrlInfo(
                url=url,
                platform=platform,
                owner=owner,
                repo=repo if repo else None,
            ))
    
    return results


def safe_json_loads(value: Optional[str], default: Optional[T] = None) -> Any:
    """
    Safely parse JSON string with error handling.
    
    Args:
        value: JSON string to parse
        default: Default value to return on error (defaults to empty list)
    
    Returns:
        Parsed JSON value or default on error
    """
    if not value:
        return default if default is not None else []
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return default if default is not None else []


def normalize_author_name(author: str) -> List[str]:
    """
    Normalize author name for search.
    
    Returns a list of variations to try:
    - Original name (if has special chars, placed first)
    - ASCII-folded version (removes diacritics like á -> a)
    - NFC normalized
    - NFD normalized (for decomposed characters)
    - Unicode escape sequence form (e.g., \\u00e1 for á)
    
    This helps match author names that may be stored differently in databases,
    e.g., "Piotr Dollár" vs "Piotr Dollar" vs "Piotr Doll\\u00e1r".
    """
    has_special_chars = any(ord(c) > 127 for c in author)
    
    if not has_special_chars:
        return [author]
    
    author_nfc = unicodedata.normalize('NFC', author)
    author_nfd = unicodedata.normalize('NFD', author)
    
    author_ascii = ''.join(
        c for c in author_nfd
        if not unicodedata.combining(c)
    )
    
    def escape_char(c: str) -> str:
        if ord(c) > 127:
            return f'\\u{ord(c):04x}'
        return c
    
    author_escaped = ''.join(escape_char(c) for c in author)
    
    variations = [author, author_escaped, author_ascii, author_nfc, author_nfd]
    return list(dict.fromkeys(variations))
