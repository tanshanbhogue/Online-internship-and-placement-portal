from dataclasses import dataclass

STRONG = 75.0
WEAK = 50.0
RECENT_N = 3
MIN_ATTEMPTS = 2
IMPROVE_DELTA = 15.0


@dataclass(frozen=True)
class CategoryInsight:
    category: str
    attempts: int
    average: float
    recent_average: float
    earlier_average: float | None
    status: str  # strong | average | weak | improved | not_enough_data


@dataclass(frozen=True)
class FocusArea:
    category: str
    priority: int  # 1 = most urgent
    message: str


def _mean(values: list[float]) -> float:
    return round(sum(values) / len(values), 2)


def classify(category: str, scores: list[float]) -> CategoryInsight:
    recent_scores = scores[-RECENT_N:]
    earlier_scores = scores[:-RECENT_N]
    recent = _mean(recent_scores)
    earlier = _mean(earlier_scores) if earlier_scores else None

    if len(scores) < MIN_ATTEMPTS:
        status = "not_enough_data"
    elif earlier is not None and earlier < WEAK and recent >= WEAK and recent - earlier >= IMPROVE_DELTA:
        status = "improved"
    elif recent >= STRONG:
        status = "strong"
    elif recent < WEAK:
        status = "weak"
    else:
        status = "average"
    return CategoryInsight(category, len(scores), _mean(scores), recent, earlier, status)


def focus_areas(insights: list[CategoryInsight], limit: int = 3) -> list[FocusArea]:
    weak = sorted((i for i in insights if i.status == "weak"), key=lambda i: i.recent_average)
    average = sorted((i for i in insights if i.status == "average"), key=lambda i: i.recent_average)
    thin = sorted((i for i in insights if i.status == "not_enough_data"), key=lambda i: i.category)

    messages: list[str | tuple[str, str]] = []
    for i in weak:
        messages.append((i.category, f"Focus on {i.category}: your recent average is {i.recent_average}%. Practise a short set every day."))
    for i in average:
        messages.append((i.category, f"Keep working on {i.category}: your recent average is {i.recent_average}%, {round(STRONG - i.recent_average, 2)} points from a strength."))
    for i in thin:
        messages.append((i.category, f"Try {i.category} at least once more so we can tell how you are doing."))

    return [FocusArea(category=c, priority=n, message=m) for n, (c, m) in enumerate(messages[:limit], start=1)]
