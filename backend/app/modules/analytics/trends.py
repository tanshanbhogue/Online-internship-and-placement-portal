MIN_POINTS = 3
MAX_POINTS = 10
CHANGE_POINTS = 5.0


def moving_average(scores: list[float], window: int) -> list[float]:
    window = max(1, window)
    out: list[float] = []
    for i in range(len(scores)):
        chunk = scores[max(0, i - window + 1) : i + 1]
        out.append(round(sum(chunk) / len(chunk), 2))
    return out


def trend_direction(scores: list[float]) -> str:
    recent = scores[-MAX_POINTS:]
    n = len(recent)
    if n < MIN_POINTS:
        return "not_enough_data"
    mean_x = (n - 1) / 2
    mean_y = sum(recent) / n
    denominator = sum((x - mean_x) ** 2 for x in range(n))
    slope = sum((x - mean_x) * (y - mean_y) for x, y in enumerate(recent)) / denominator
    change = slope * (n - 1)
    if change >= CHANGE_POINTS:
        return "improving"
    if change <= -CHANGE_POINTS:
        return "declining"
    return "steady"
