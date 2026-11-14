"""Validated imports and deterministic, non-clinical time-series analysis.

All functions are independent of Tk. Imports return a complete immutable dataset
or raise; a failed or cancelled load cannot partially replace the UI session.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timezone
import io
import math
import os
from pathlib import Path
import tempfile
from typing import Callable

MAX_FILE_BYTES = 20 * 1024 * 1024
MAX_OBSERVATIONS = 100_000
MAX_COWS = 500
METRICS = ("activity", "temperature")


class DataError(ValueError):
    """An input cannot be processed within the documented data contract."""


class ImportCancelled(DataError):
    """The caller requested cancellation before an import completed."""


@dataclass(frozen=True)
class Observation:
    timestamp: datetime
    cow_id: str
    activity: float | None = None
    temperature: float | None = None


@dataclass(frozen=True)
class Dataset:
    observations: tuple[Observation, ...]
    source_name: str
    timezone_aware: bool
    source_path: str | None = None

    @property
    def cow_ids(self) -> tuple[str, ...]:
        return tuple(sorted({o.cow_id for o in self.observations}))

    @property
    def metrics(self) -> tuple[str, ...]:
        return tuple(m for m in METRICS if any(getattr(o, m) is not None for o in self.observations))

    def series(self, cow_id: str | None, metric: str) -> tuple[tuple[datetime, float], ...]:
        """Return sorted observations, or per-timestamp cow means for the herd.

        Missing values are omitted. Herd means may have different cow coverage
        at each timestamp and are descriptive; no imputation is performed.
        """
        if metric not in METRICS:
            raise DataError("Select activity or temperature.")
        values: dict[datetime, list[float]] = {}
        for observation in self.observations:
            value = getattr(observation, metric)
            if value is not None and (cow_id is None or observation.cow_id == cow_id):
                values.setdefault(observation.timestamp, []).append(value)
        return tuple((t, _mean(v)) for t, v in sorted(values.items()))


@dataclass(frozen=True)
class Summary:
    count: int
    minimum: float
    maximum: float
    mean: float
    first: datetime
    last: datetime


@dataclass(frozen=True)
class Prediction:
    timestamp: datetime
    actual: float
    predicted: float


@dataclass(frozen=True)
class Backtest:
    points: tuple[Prediction, ...]
    mae: float
    training_count: int
    window: int


def _mean(values: list[float]) -> float:
    # Dividing before summation avoids overflow for many large finite values.
    try:
        return math.fsum(v / len(values) for v in values)
    except (OverflowError, ValueError) as exc:
        raise DataError("Values exceed the supported numerical range.") from exc


def _timestamp(raw: str, row: int) -> datetime:
    try:
        value = datetime.fromisoformat(raw.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise DataError(f"Row {row}: timestamp must be ISO 8601 (for example 2026-01-01T12:00:00Z).") from exc
    return value.astimezone(timezone.utc) if value.tzinfo is not None else value


def _number(raw: str, metric: str, row: int) -> float | None:
    if not raw.strip():
        return None
    try:
        value = float(raw)
    except ValueError as exc:
        raise DataError(f"Row {row}: {metric} must be a finite number or blank.") from exc
    if not math.isfinite(value):
        raise DataError(f"Row {row}: {metric} must be finite.")
    if metric == "activity" and value < 0:
        raise DataError(f"Row {row}: activity cannot be negative.")
    return value


def _cow_id(raw: str, row: int) -> str:
    value = raw.strip()
    if not value or len(value) > 128 or any(ord(c) < 32 or ord(c) == 127 for c in value):
        raise DataError(f"Row {row}: cow_id must contain 1–128 printable characters.")
    return value


def load_csv(path: str | Path, cancel: Callable[[], bool] | None = None,
             legacy_metric: str | None = None) -> Dataset:
    """Load UTF-8 canonical long CSV, or explicitly selected legacy wide CSV.

    Canonical headers: timestamp,cow_id and activity and/or temperature. Units
    are caller supplied: activity counts per interval and temperature Celsius.
    Optional blank metric cells are omitted from analysis. No units are inferred.
    Legacy date headers: Date or Unnamed: 0. Group mean is ignored and recomputed.
    All-aware timestamps become UTC; mixing aware and naive timestamps is rejected.
    """
    source = Path(path)
    if legacy_metric not in (None, *METRICS):
        raise DataError("Legacy metric must be activity or temperature.")
    def check_cancel():
        if cancel and cancel():
            raise ImportCancelled("Import cancelled; the previous dataset is unchanged.")
    check_cancel()
    try:
        with source.open("rb") as stream:
            raw = stream.read(MAX_FILE_BYTES + 1)
    except OSError as exc:
        raise DataError(f"Cannot read CSV: {exc.strerror or type(exc).__name__}.") from exc
    if len(raw) > MAX_FILE_BYTES:
        raise DataError("CSV exceeds the 20 MiB file limit.")
    try:
        content = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise DataError("CSV must use UTF-8 encoding.") from exc
    observations: list[Observation] = []
    seen: set[tuple[datetime, str]] = set()
    cows: set[str] = set()
    aware: bool | None = None
    reader = csv.reader(io.StringIO(content, newline=""), strict=True)
    try:
        headers = next(reader, [])
        headers = [h.strip() for h in headers]
        if not headers or len(set(headers)) != len(headers):
            raise DataError("CSV must have a nonempty header with no duplicate columns.")
        canonical = {"timestamp", "cow_id"}.issubset(headers)
        if canonical:
            metric_columns = [m for m in METRICS if m in headers]
            if not metric_columns:
                raise DataError("Canonical CSV needs an activity or temperature column.")
        else:
            if legacy_metric is None:
                raise DataError("CSV lacks timestamp,cow_id. Select Legacy activity wide or Legacy temperature wide for an old wide file.")
            dates = [h for h in headers if h in ("Date", "Unnamed: 0")]
            if not dates:
                raise DataError("Legacy wide CSV needs a Date or Unnamed: 0 timestamp column.")
            cow_columns = [h for h in headers if h not in (*dates, "Group mean")]
            if not cow_columns:
                raise DataError("Legacy wide CSV contains no cow columns.")
            if len(cow_columns) > MAX_COWS:
                raise DataError("CSV exceeds the 500 cow limit.")
        def append(timestamp, cow, activity, temperature, row):
            nonlocal aware
            is_aware = timestamp.tzinfo is not None
            if aware is not None and aware != is_aware:
                raise DataError(f"Row {row}: do not mix timezone-aware and timezone-naive timestamps.")
            aware = is_aware
            key = (timestamp, cow)
            if key in seen:
                raise DataError(f"Row {row}: duplicate timestamp and cow_id.")
            if activity is None and temperature is None:
                raise DataError(f"Row {row}: at least one measurement is required.")
            cows.add(cow)
            if len(cows) > MAX_COWS:
                raise DataError("CSV exceeds the 500 cow limit.")
            if len(observations) >= MAX_OBSERVATIONS:
                raise DataError("CSV exceeds the 100,000 observation limit.")
            seen.add(key)
            observations.append(Observation(timestamp, cow, activity, temperature))
        for row in reader:
            check_cancel()
            line = reader.line_num
            if not row or all(not cell.strip() for cell in row):
                continue
            if len(row) != len(headers):
                raise DataError(f"Row {line}: expected {len(headers)} columns; found {len(row)}.")
            record = dict(zip(headers, row))
            if canonical:
                timestamp = _timestamp(record["timestamp"], line)
                values = {m: _number(record.get(m, ""), m, line) for m in METRICS}
                append(timestamp, _cow_id(record["cow_id"], line), values['activity'], values['temperature'], line)
            else:
                timestamp = _timestamp(record[dates[0]], line)
                if len(dates) == 2 and _timestamp(record[dates[1]], line) != timestamp:
                    raise DataError(f"Row {line}: Date and Unnamed: 0 disagree.")
                for cow in cow_columns:
                    check_cancel()
                    value = _number(record[cow], legacy_metric, line)
                    if value is None:
                        continue
                    append(timestamp, _cow_id(cow, line), value if legacy_metric == 'activity' else None,
                           value if legacy_metric == 'temperature' else None, line)
    except csv.Error as exc:
        raise DataError(f"Row {reader.line_num}: malformed CSV ({exc}).") from exc
    check_cancel()
    if not observations:
        raise DataError("CSV contains no measurements.")
    observations.sort(key=lambda o: (o.timestamp, o.cow_id))
    return Dataset(tuple(observations), source.name, bool(aware), str(source.resolve()))


def summarize(dataset: Dataset, cow_id: str | None, metric: str) -> Summary:
    series = dataset.series(cow_id, metric)
    if not series:
        raise DataError("No measurements for this cow and metric.")
    values = [value for _, value in series]
    return Summary(len(values), min(values), max(values), _mean(values), series[0][0], series[-1][0])


def backtest(dataset: Dataset, cow_id: str | None, metric: str, window: int = 5,
             test_fraction: float = .2) -> Backtest:
    """Walk-forward one-step trailing-mean baseline on the final time fraction.

    Every prediction uses only earlier actual observations. Windows count samples,
    not elapsed time. Missing observations are not interpolated. This is a baseline,
    not the historical neural model and not a diagnostic forecast.
    """
    if isinstance(window, bool) or not isinstance(window, int) or not 1 <= window <= 10_000:
        raise DataError("Window must be an integer between 1 and 10,000.")
    if isinstance(test_fraction, bool) or not isinstance(test_fraction, (float, int)) or not math.isfinite(test_fraction) or not 0 < test_fraction < 1:
        raise DataError("Test fraction must be between zero and one.")
    series = dataset.series(cow_id, metric)
    split = int(len(series) * (1 - test_fraction))
    if split < window or split >= len(series):
        raise DataError(f"Not enough history: use at least {math.ceil(window/(1-test_fraction))} measurements or a smaller window.")
    # Maintain a rolling mean instead of recomputing an O(window) sum for each
    # held-out observation. The input bounds keep both memory and work bounded.
    rolling = _mean([value for _, value in series[split-window:split]])
    collected = []
    for i in range(split, len(series)):
        collected.append(Prediction(series[i][0], series[i][1], rolling))
        if i + 1 < len(series):
            try:
                rolling = math.fsum((rolling, series[i][1]/window, -series[i-window][1]/window))
            except (OverflowError, ValueError) as exc:
                raise DataError("Values exceed the supported numerical range.") from exc
            if not math.isfinite(rolling):
                raise DataError("Values exceed the supported numerical range.")
    points = tuple(collected)
    errors = [abs(point.actual - point.predicted) for point in points]
    if any(not math.isfinite(error) for error in errors):
        raise DataError("Differences exceed the supported numerical range.")
    return Backtest(points, _mean(errors), split, window)


def _spreadsheet_safe(value: str) -> str:
    return "'" + value if value.lstrip().startswith(("=", "+", "-", "@")) else value


def export_analysis(path: str | Path, dataset: Dataset, cow_id: str | None, metric: str,
                    window: int = 5, test_fraction: float = .2) -> None:
    """Atomically save a baseline backtest CSV, never overwriting the import."""
    target = Path(path)
    if dataset.source_path and target.resolve() == Path(dataset.source_path).resolve():
        raise DataError("Choose a new export filename; the original CSV is read-only.")
    result = backtest(dataset, cow_id, metric, window, test_fraction)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="", dir=target.parent,
                                         prefix=".dhms-", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            writer = csv.writer(stream)
            writer.writerow(["timestamp", "cow_id", "metric", "actual", "baseline_predicted", "absolute_error", "window_samples", "analysis"])
            for point in result.points:
                writer.writerow([point.timestamp.isoformat(), _spreadsheet_safe(cow_id if cow_id is not None else "HERD_MEAN"), metric,
                                 point.actual, point.predicted, abs(point.actual-point.predicted), window, "descriptive trailing-mean baseline; not diagnostic"])
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
    except OSError as exc:
        raise DataError(f"Cannot save export: {exc.strerror or type(exc).__name__}.") from exc
    finally:
        if temporary and temporary.exists():
            temporary.unlink()
