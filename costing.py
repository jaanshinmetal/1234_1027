"""Pure calculation and CSV helpers; monetary values use Decimal."""
import csv
import io
from decimal import Decimal, ROUND_HALF_UP


def number(value):
    result = Decimal(str(value))
    if not result.is_finite() or result < 0:
        raise ValueError("金額與參數必須是有限的非負數")
    return result


def money(value):
    return number(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def material_cost(weight, price, loss):
    return money(number(weight) / 1000 * number(price) * (1 + number(loss) / 100))


def die_cost(dimensions, cavities, rules):
    """Rules contain max side length, cavity count and per-piece cost."""
    sides = [number(v) for v in dimensions]
    if len(sides) != 3 or min(sides) <= 0 or cavities < 1:
        return None
    for rule in sorted(rules, key=lambda r: r["最大邊長上限 (mm)"]):
        if max(sides) <= number(rule["最大邊長上限 (mm)"]) and cavities == rule["穴數"]:
            return money(rule["每件壓鑄費 (NT$)"])
    return None


def summarize(items):
    total = sum((money(value) for _, value in items), Decimal("0.00"))
    return total, [
        {"製程": name, "金額 (NT$/件)": float(money(value)),
         "佔比 (%)": float(money(value) / total * 100) if total else 0.0}
        for name, value in items
    ]


def csv_bytes(rows):
    """UTF-8 BOM for Excel; neutralize spreadsheet formulas in text cells."""
    def safe(cell):
        text = str(cell)
        return "'" + text if text.lstrip().startswith(("=", "+", "-", "@", "\t", "\r", "\n")) else text
    stream = io.StringIO(newline="")
    writer = csv.writer(stream)
    writer.writerows([[safe(cell) for cell in row] for row in rows])
    return stream.getvalue().encode("utf-8-sig")
