"""Plain-language helpers shared by all views. `lang` is en, rw or fr; officer pages use English."""
import re

from components.i18n import BEFORE_AFTER, CROPS, GROUPS, MONTHS_FULL, MONTHS_SHORT, SEASONS

EN_SHORT = MONTHS_SHORT["en"]


def season_label(s, lang="en"):
    return SEASONS.get(lang, SEASONS["en"]).get(s, s)


def crop_label(c, lang="en"):
    return CROPS.get(lang, {}).get(c, c)


def month_full(code, lang="en"):
    """'11 Nov' or 'Nov' -> full month name in the chosen language."""
    tok = str(code).split()[-1]
    return MONTHS_FULL[lang][EN_SHORT.index(tok)] if tok in EN_SHORT else str(code)


def window_label(w, lang="en"):
    """Translate a survey window such as '16-31 Dec', 'Before 1 Dec' or 'After Feb'."""
    if lang == "en" or not isinstance(w, str):
        return w
    before, after = BEFORE_AFTER[lang]
    w = re.sub(r"^Before\b", before, w)
    w = re.sub(r"^After\b", after, w)
    return re.sub(r"\b(" + "|".join(EN_SHORT) + r")\b", lambda m: MONTHS_SHORT[lang][EN_SHORT.index(m.group(1))], w)


def group_phrase(g, lang="en"):
    return GROUPS.get(lang, GROUPS["en"]).get(g, f"{str(g).lower()} prices")


def vs_average_text(idx):
    """Seasonal price index 1.037 -> 'about 4% above the yearly average'."""
    p = (idx - 1) * 100
    if abs(p) < 1:
        return "about the same as the yearly average"
    return f"about {abs(p):.0f}% {'above' if p > 0 else 'below'} the yearly average"


def data_as_of(forecast, lang="en"):
    """Latest price month, read from the data so a refresh updates it automatically."""
    try:
        y, mo = forecast["Food (all)"]["last_observed"].split("-")
        return f"{MONTHS_FULL[lang][int(mo) - 1]} {y}"
    except Exception:
        return "?"
