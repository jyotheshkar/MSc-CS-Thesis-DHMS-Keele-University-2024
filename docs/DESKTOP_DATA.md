# Data, analysis and research boundaries

## Canonical input

Save a UTF-8 CSV with these headers:

```csv
timestamp,cow_id,activity,temperature
2024-01-01T08:00:00,cow-001,12,38.4
2024-01-02T08:00:00,cow-001,15,38.5
```

These rows are illustrative synthetic data. Cow identifiers are text, not a fixed four-digit number. `activity` must be nonnegative. Temperature is a numerical measurement; the application does not infer units or clinical meaning. Use consistent units and acquisition methods within a series. At least one metric value is required for each accepted observation. Do not mix timezone-aware and timezone-naive timestamps within a file.

Duplicate cow/timestamp observations are rejected so the application does not silently double-count or pick a conflicting row. Missing metrics are supported only according to the parser's documented contract. Keep original data outside the repository. Import does not modify or remove the selected file.

The included sample is synthetic and contains no actual herd or personal data. Start with **Load sample**, then import your own file using **Open CSV**. Observe the reported schema and count before interpreting charts.

## Baseline analysis

The trailing-mean baseline uses a window of prior observations. A chronological holdout is evaluated one step at a time; when the next observation becomes historical it may enter a later prediction window. This is walk-forward one-step backtesting, not a fixed-origin multi-step forecast.

The mean absolute error uses the same units as the metric. Results for two metrics in different units cannot be compared as if they were a common accuracy score. A short series or a window too large for the available history produces a clear error rather than an invented result.

## Not a veterinary product

Charts and summaries support research data exploration. The application does not diagnose illness, validate temperature thresholds or recommend animal treatment. It does not reproduce an operational neural-network service or establish accuracy from the original dissertation.

The historical `.h5` model files are not loaded by the supported desktop edition. Their matching preprocessing, label/schema and complete validation contract were not established. No user-provided model or Python code is executed during import.
