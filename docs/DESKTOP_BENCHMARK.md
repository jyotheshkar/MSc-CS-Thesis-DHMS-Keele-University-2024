# Desktop core benchmark

Measured **14 November 2026**, one local run on Python 3.11.15, Windows-10-10.0.26300-SP0.

## Input and method

A generated UTF-8 canonical CSV contained **100,000 observations, 500 cows and 200 hourly timestamps per cow**. Its size was **4,090,039 bytes**. Both documented observation and animal limits were exercised exactly; the file size remained below the separate 20 MiB limit. All data was synthetic and generated outside the repository. No real herd data was used.

`time.perf_counter()` measured each operation once. Activity analysis used a five-sample trailing mean with a final 20% chronological holdout. Single-cow and herd runs each produced 40 held-out predictions. Values were returned successfully without errors.

| Operation | Measured seconds |
|---|---:|
| CSV read, validation, immutable dataset creation and sorting | 1.195705 |
| Single-cow summary plus backtest | 0.023040 |
| Herd mean summary plus backtest | 0.084884 |

## Interpretation and limits

This is a smoke-scale measurement of the bounded analysis core, not a capacity or latency commitment. It does not measure GUI rendering, packaged application startup, peak memory, repeated-run variation, concurrent users or every possible dataset shape. Per-cow activity MAE was 5.100000, and herd activity MAE was 5.100000; these values describe only the synthetic fixture and do not establish predictive accuracy on real data.

The import sorts observations in O(n log n) time. A series extraction and rolling baseline backtest use O(n) work within the stated input limits. Desktop plotting separately downsamples display points. No result is extrapolated beyond 100,000 observations or 500 animals.

## Captured result

```json
{
  "date": "2026-11-14",
  "python": "3.11.15",
  "platform": "Windows-10-10.0.26300-SP0",
  "processor": "AMD64 Family 25 Model 80 Stepping 0, AuthenticAMD",
  "logical_cpus": 16,
  "scope": "Single local run with generated synthetic data; import plus summary/backtest. No GUI, packaging, peak memory or concurrent workload measurement.",
  "file_bytes": 4090039,
  "observations": 100000,
  "cows": 500,
  "timestamps_per_cow": 200,
  "window_samples": 5,
  "held_out_fraction": 0.2,
  "seconds": {
    "load_csv": 1.195705,
    "single_cow_summary_and_backtest": 0.02304,
    "herd_summary_and_backtest": 0.084884
  },
  "backtest_points": {
    "single_cow": 40,
    "herd": 40
  },
  "mae": {
    "single_cow": 5.099999999999994,
    "herd": 5.099999999999994
  },
  "limits": "Observation and cow limits exercised exactly; file is below20MiB. Timings describe this host and this synthetic shape only, not a production capacity guarantee."
}
```
