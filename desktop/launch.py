"""Source/frozen entry point. --self-test exercises packaged core and sample."""
from __future__ import annotations

import json
import sys


def self_test():
    from dhms.app import sample_file
    from dhms.core import backtest, load_csv, summarize

    dataset = load_csv(sample_file())
    metric = dataset.metrics[0]
    stats = summarize(dataset, None, metric)
    result = backtest(dataset, None, metric, window=3)
    assert stats.count > 3 and result.points
    if sys.stdout is not None:
        print(json.dumps({"version": "1.0.0", "sample_rows": len(dataset.observations), "animals": len(dataset.cow_ids), "predictions": len(result.points), "mae": result.mae, "status": "passed"}))


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
    elif "--smoke-gui" in sys.argv:
        from dhms.app import smoke_test
        smoke_test()
    else:
        from dhms.app import main
        main()
