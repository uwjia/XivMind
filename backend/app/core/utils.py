import unicodedata
from typing import List


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
