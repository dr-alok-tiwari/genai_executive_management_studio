from __future__ import annotations

import csv
import io
from typing import Iterable


def txt_bytes(text: str) -> bytes:
    return (text or "").encode("utf-8")


def markdown_bytes(text: str) -> bytes:
    return (text or "").encode("utf-8")


def csv_bytes(rows: Iterable[dict]) -> bytes:
    rows = list(rows)
    output = io.StringIO()
    if not rows:
        output.write("")
        return output.getvalue().encode("utf-8")
    writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")
