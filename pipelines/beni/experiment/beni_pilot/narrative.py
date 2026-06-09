from __future__ import annotations

from dataclasses import dataclass

from utils import normalize_text


NARRATIVE_FORCE_LEXICON = {
    "crisis": [
        "সংকট",
        "চাপ",
        "ঝুঁকি",
        "অস্থিরতা",
        "ধস",
        "ঘাটতি",
        "বিপর্যয়",
        "বিপর্যয়",
    ],
    "burden": [
        "দুর্ভোগ",
        "কষ্ট",
        "ব্যয়",
        "ব্যয়",
        "জীবনযাত্রা",
        "ভোগান্তি",
        "চড়া",
        "চড়া",
    ],
    "blame": [
        "ব্যর্থতা",
        "দুর্নীতি",
        "সিন্ডিকেট",
        "অব্যবস্থাপনা",
        "দায়ী",
        "দায়ী",
        "অভিযোগ",
    ],
    "reform": [
        "সংস্কার",
        "নীতিমালা",
        "শৃঙ্খলা",
        "উদ্যোগ",
        "পদক্ষেপ",
        "পরিকল্পনা",
    ],
    "stability": [
        "স্থিতিশীল",
        "স্বস্তি",
        "উন্নতি",
        "নিয়ন্ত্রণ",
        "নিয়ন্ত্রণ",
        "সামাল",
    ],
    "uncertainty": [
        "অনিশ্চয়তা",
        "অনিশ্চয়তা",
        "আশঙ্কা",
        "শঙ্কা",
        "সন্দেহ",
        "প্রশ্ন",
    ],
    "resilience": [
        "ঘুরে দাঁড়ানো",
        "ঘুরে দাঁড়ানো",
        "সহনশীল",
        "প্রবৃদ্ধি",
        "সম্ভাবনা",
        "পুনরুদ্ধার",
    ],
}


VALUATION_TARGET_LEXICON = {
    "government": ["সরকার", "মন্ত্রণালয়", "মন্ত্রণালয়", "মন্ত্রী", "প্রশাসন"],
    "central_bank": ["বাংলাদেশ ব্যাংক", "কেন্দ্রীয় ব্যাংক", "কেন্দ্রীয় ব্যাংক"],
    "banks": ["ব্যাংক", "ঋণ", "আমানত", "তারল্য"],
    "businesses": ["ব্যবসায়ী", "ব্যবসায়ী", "শিল্প", "উদ্যোক্তা", "কারখানা"],
    "market_actors": ["বাজার", "সিন্ডিকেট", "ব্যবসায়ী", "মজুতদার"],
    "global_economy": ["বিশ্ববাজার", "আইএমএফ", "ডলার", "তেল", "আমদানি", "রপ্তানি"],
    "households": ["ভোক্তা", "পরিবার", "জনগণ", "মানুষ", "ক্রেতা"],
}


ECONOMIC_TOPIC_LEXICON = {
    "inflation": ["মূল্যস্ফীতি", "দাম", "মূল্য", "খাদ্য মূল্য", "ভোক্তা মূল্য"],
    "exchange_rate": ["ডলার", "টাকা", "বিনিময় হার", "বিনিময় হার"],
    "reserves": ["রিজার্ভ", "বৈদেশিক মুদ্রা"],
    "banking": ["ব্যাংক", "ঋণ", "আমানত", "সুদ", "তারল্য"],
    "fiscal_policy": ["বাজেট", "কর", "রাজস্ব", "ভর্তুকি", "ঘাটতি"],
    "trade": ["রপ্তানি", "আমদানি", "বাণিজ্য", "এলসি"],
    "employment": ["কর্মসংস্থান", "বেকারত্ব", "মজুরি", "চাকরি"],
    "growth_investment": ["জিডিপি", "প্রবৃদ্ধি", "বিনিয়োগ", "বিনিয়োগ", "উৎপাদন"],
}


@dataclass(frozen=True)
class LexiconScore:
    label: str
    score: int
    matches: list[str]


def score_lexicon(text: str, lexicon: dict[str, list[str]]) -> list[LexiconScore]:
    normalized = normalize_text(text)
    scores = []
    for label, terms in lexicon.items():
        matches = [term for term in terms if term in normalized]
        scores.append(LexiconScore(label=label, score=len(matches), matches=matches))
    return sorted(scores, key=lambda item: (-item.score, item.label))


def top_label(text: str, lexicon: dict[str, list[str]], fallback: str = "none") -> LexiconScore:
    scores = score_lexicon(text, lexicon)
    if not scores or scores[0].score == 0:
        return LexiconScore(label=fallback, score=0, matches=[])
    return scores[0]


def narrative_profile(text: str) -> dict[str, object]:
    topic = top_label(text, ECONOMIC_TOPIC_LEXICON, "other")
    force = top_label(text, NARRATIVE_FORCE_LEXICON, "neutral")
    target = top_label(text, VALUATION_TARGET_LEXICON, "unnamed_system")
    return {
        "economic_topic": topic.__dict__,
        "narrative_force": force.__dict__,
        "valuation_target": target.__dict__,
        "all_topic_scores": [item.__dict__ for item in score_lexicon(text, ECONOMIC_TOPIC_LEXICON)],
        "all_force_scores": [item.__dict__ for item in score_lexicon(text, NARRATIVE_FORCE_LEXICON)],
        "all_target_scores": [item.__dict__ for item in score_lexicon(text, VALUATION_TARGET_LEXICON)],
    }
