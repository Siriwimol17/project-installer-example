"""Text analysis independent of the HTTP layer."""

import re
from collections import Counter

MAX_TEXT_LENGTH = 100_000
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "but", "by", "for",
    "from", "had", "has", "have", "he", "her", "his", "i", "in", "is", "it",
    "its", "of", "on", "or", "our", "she", "that", "the", "their", "them",
    "there", "they", "this", "to", "was", "we", "were", "will", "with", "you",
    "your", "และ", "เป็น", "การ", "ก็", "กับ", "ของ", "ค่ะ", "ครับ", "ความ", "คือ",
    "จะ", "จาก", "ได้", "ที่", "นี้", "นั้น", "ไม่", "มี", "มา", "ว่า", "ให้", "ใน", "แล้ว",
}
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['’][A-Za-z0-9]+)?|[\u0E00-\u0E7F]+", re.UNICODE)
SENTENCE_RE = re.compile(r"[^.!?。！？\n]+", re.UNICODE)


def _tokens(text: str) -> list[str]:
    if re.search(r"[\u0E00-\u0E7F]", text):
        try:
            from pythainlp.tokenize import word_tokenize

            return [word for word in word_tokenize(text, engine="newmm") if word.strip()]
        except ImportError:
            # Basic fallback: Thai text is grouped by whitespace, as documented.
            return WORD_RE.findall(text)
    return WORD_RE.findall(text)


def analyze_text(text: str) -> dict[str, object]:
    words = _tokens(text)
    keywords = Counter(word.casefold() for word in words if word.casefold() not in STOPWORDS)
    sentences = [part for part in SENTENCE_RE.findall(text) if part.strip()]
    return {
        "charCount": len(text),
        "wordCount": len(words),
        "sentenceCount": len(sentences),
        "topKeywords": [
            {"word": word, "count": count}
            for word, count in sorted(keywords.items(), key=lambda item: (-item[1], item[0]))[:10]
        ],
    }
