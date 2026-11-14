import csv
from datetime import datetime, timedelta
import io
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from dhms.core import DataError, ImportCancelled, load_csv, summarize, backtest, export_analysis


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.folder = Path(self.temporary.name)

    def write(self, text, name="input.csv"):
        path = self.folder/name
        path.write_text(text, encoding="utf-8", newline="")
        return path

    def history(self, cows=("A",), rows=20):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["timestamp","cow_id","activity","temperature"])
        start = datetime(2026,1,1)
        for i in reversed(range(rows)):
            for n,cow in enumerate(cows):
                writer.writerow([(start+timedelta(hours=i)).isoformat(),cow,i+n,38+n*.1+i*.01])
        return load_csv(self.write(output.getvalue()))

    def test_sort_summary_and_herd_mean(self):
        data = self.history(("B","A"))
        self.assertEqual(data.cow_ids, ("A","B"))
        self.assertEqual(data.metrics, ("activity","temperature"))
        stats = summarize(data, "B", "activity")
        self.assertEqual((stats.count,stats.minimum,stats.maximum,stats.mean),(20,0,19,9.5))
        self.assertEqual(data.series(None,"activity")[0][1],.5)
        self.assertEqual(data.series(None,"activity")[-1][1],19.5)

    def test_optional_metrics_are_omitted_without_imputation(self):
        data = load_csv(self.write("timestamp,cow_id,activity,temperature\n2026-01-01,A,1,\n2026-01-02,A,,38\n"))
        self.assertEqual(len(data.series("A","activity")),1)
        self.assertEqual(len(data.series("A","temperature")),1)
        with self.assertRaises(DataError): summarize(data,"absent","activity")
        with self.assertRaises(DataError): data.series("A","diagnosis")

    def test_timezone_normalization_and_mixed_rejection(self):
        data=load_csv(self.write("timestamp,cow_id,activity\n2026-01-01T01:00:00+01:00,A,1\n2026-01-01T01:00:00Z,A,2\n"))
        self.assertTrue(data.timezone_aware)
        self.assertEqual(data.observations[0].timestamp.hour,0)
        with self.assertRaisesRegex(DataError,"mix timezone"):
            load_csv(self.write("timestamp,cow_id,activity\n2026-01-01,A,1\n2026-01-02T00:00:00Z,A,2\n"))

    def test_duplicate_normalized_time_rejected(self):
        with self.assertRaisesRegex(DataError,"Row 3: duplicate"):
            load_csv(self.write("timestamp,cow_id,activity\n2026-01-01T01:00:00+01:00,A,1\n2026-01-01T00:00:00Z,A,2\n"))

    def test_bad_row_never_returns_partial_import(self):
        for invalid in ["bad,A,2", "2026-01-02,A,nan", "2026-01-02,A,inf", "2026-01-02,A,-1", "2026-01-02,,1", "2026-01-02,A,", "2026-01-02,A,2,3"]:
            with self.subTest(invalid=invalid), self.assertRaisesRegex(DataError,"Row 3"):
                load_csv(self.write("timestamp,cow_id,activity\n2026-01-01,A,1\n"+invalid+"\n"))

    def test_limits_and_malformed_headers(self):
        for header in ["", "timestamp,cow_id", "timestamp,cow_id,activity,activity"]:
            with self.subTest(header=header), self.assertRaises(DataError):
                load_csv(self.write(header+"\n"))
        with patch('dhms.core.MAX_FILE_BYTES',4), self.assertRaisesRegex(DataError,"20 MiB"):
            load_csv(self.write("12345"))
        with patch('dhms.core.MAX_OBSERVATIONS',1), self.assertRaisesRegex(DataError,"observation limit"):
            self.history(rows=2)
        with patch('dhms.core.MAX_COWS',1), self.assertRaisesRegex(DataError,"cow limit"):
            self.history(cows=("A","B"),rows=1)

    def test_utf8_bom_and_invalid_encoding(self):
        data=load_csv(self.write("\ufefftimestamp,cow_id,temperature\n2026-01-01,é,38.2\n"))
        self.assertEqual(data.cow_ids,("é",))
        path=self.folder/'bad.csv'; path.write_bytes(b'\xff\xfeabc')
        with self.assertRaisesRegex(DataError,"UTF-8"): load_csv(path)

    def test_cancellation_during_import(self):
        calls=[]
        def cancel():
            calls.append(1)
            return len(calls)>2
        path=self.write("timestamp,cow_id,activity\n2026-01-01,A,1\n2026-01-02,A,2\n")
        with self.assertRaises(ImportCancelled): load_csv(path,cancel)

    def test_legacy_requires_explicit_metric_and_ignores_group_mean(self):
        path=self.write("Unnamed: 0,1001,1002, Group mean\n2026-01-01,1,3,999\n2026-01-02,2,4,999\n")
        with self.assertRaisesRegex(DataError,"Select Legacy"): load_csv(path)
        data=load_csv(path,legacy_metric='activity')
        self.assertEqual(data.cow_ids,("1001","1002"))
        self.assertEqual(data.series(None,'activity')[0][1],2)
        self.assertEqual(data.metrics,('activity',))
        with self.assertRaises(DataError): load_csv(path,legacy_metric='diagnosis')

    def test_legacy_dates_must_align_and_blank_measurements_skip(self):
        data=load_csv(self.write("Date,Unnamed: 0,A,B\n2026-01-01,2026-01-01,,38\n"),legacy_metric='temperature')
        self.assertEqual(data.cow_ids,('B',))
        with self.assertRaisesRegex(DataError,"disagree"):
            load_csv(self.write("Date,Unnamed: 0,A\n2026-01-01,2026-01-02,1\n"),legacy_metric='activity')

    def test_backtest_uses_only_earlier_actual_values(self):
        data=self.history(rows=20)
        result=backtest(data,"A","activity",window=3,test_fraction=.2)
        self.assertEqual(result.training_count,16)
        self.assertEqual(result.points[0].actual,16)
        self.assertEqual(result.points[0].predicted,14)
        self.assertEqual(result.points[-1].predicted,17)
        self.assertEqual(result.mae,2)
        # Irregular temperature values exercise the rolling update independently
        # of the easy arithmetic progression above.
        measurements=data.series('A','temperature')
        result=backtest(data,'A','temperature',window=7,test_fraction=.5)
        for i,point in enumerate(result.points,start=result.training_count):
            expected=sum(value for _,value in measurements[i-7:i])/7
            self.assertAlmostEqual(point.predicted,expected,places=10)

    def test_backtest_invalid_and_short_series(self):
        data=self.history(rows=3)
        for window in [0,True,1.5,10001]:
            with self.subTest(window=window),self.assertRaises(DataError): backtest(data,"A","activity",window=window)
        for fraction in [0,1,float('nan'),True]:
            with self.subTest(fraction=fraction),self.assertRaises(DataError): backtest(data,"A","activity",test_fraction=fraction)
        with self.assertRaisesRegex(DataError,"Not enough history"): backtest(data,"A","activity",window=5)

    def test_export_formula_safety_and_original_readonly(self):
        data=self.history(cows=('=SUM(A1)',))
        before=Path(data.source_path).read_bytes()
        with self.assertRaisesRegex(DataError,"original CSV"): export_analysis(data.source_path,data,'=SUM(A1)','activity')
        output=self.folder/'analysis.csv'
        export_analysis(output,data,'=SUM(A1)','activity',window=3)
        rows=list(csv.DictReader(io.StringIO(output.read_text())))
        self.assertEqual(len(rows),4)
        self.assertEqual(rows[0]['cow_id'],"'=SUM(A1)")
        self.assertEqual(float(rows[0]['absolute_error']),2)
        self.assertEqual(Path(data.source_path).read_bytes(),before)

    def test_failed_export_preserves_existing_target_and_cleans_temporary(self):
        data=self.history(); output=self.write('previous',name='analysis.csv')
        with patch('dhms.core.os.replace',side_effect=OSError('disk error')),self.assertRaises(DataError):
            export_analysis(output,data,'A','activity')
        self.assertEqual(output.read_text(),'previous')
        self.assertEqual(list(self.folder.glob('.dhms-*.tmp')),[])


if __name__=='__main__': unittest.main()
