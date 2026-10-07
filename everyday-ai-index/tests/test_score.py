import csv
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import blind  # noqa: E402
import score  # noqa: E402


def write_csv(path: Path, header: list[str], rows: list[list]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


class NormaliseTests(unittest.TestCase):
    def test_ratio_best_is_100(self):
        self.assertEqual(score.normalise(80, 80, "ratio"), 100)
        self.assertEqual(score.normalise(40, 80, "ratio"), 50)

    def test_inverse_ratio_lower_is_better(self):
        self.assertEqual(score.normalise(10, 10, "inverse_ratio"), 100)
        self.assertEqual(score.normalise(20, 10, "inverse_ratio"), 50)

    def test_elo_best_is_100_and_monotonic(self):
        self.assertAlmostEqual(score.normalise(1500, 1500, "elo"), 100)
        self.assertLess(score.normalise(1400, 1500, "elo"), score.normalise(1450, 1500, "elo"))

    def test_log_counts_doublings(self):
        self.assertEqual(score.normalise(16, 16, "log"), 100)
        self.assertEqual(score.normalise(4, 16, "log"), 50)
        self.assertEqual(score.normalise(0.5, 16, "log"), 0)

    def test_zero_best_does_not_divide_by_zero(self):
        self.assertEqual(score.normalise(0, 0, "ratio"), 0)


class ExampleDataTests(unittest.TestCase):
    def setUp(self):
        self.profile, self.results, self.warnings = score.compute(
            ROOT / "data" / "example", ROOT / "config", ROOT / "tasks" / "personal_battery.toml", None)
        self.by_id = {r.setup_id: r for r in self.results}

    def test_same_model_gets_same_layer_a(self):
        self.assertAlmostEqual(self.by_id["S2"].layers["A"], self.by_id["S3"].layers["A"])

    def test_harness_changes_ranking_for_same_model(self):
        self.assertGreater(self.by_id["S3"].score, self.by_id["S2"].score)

    def test_missing_layer_marks_provisional_and_ranks_last(self):
        local = self.by_id["S5"]
        self.assertIsNone(local.layers["C"])
        self.assertTrue(local.provisional)
        self.assertEqual(self.results[-1].setup_id, "S5")

    def test_honesty_gate_derived_from_personal_results(self):
        self.assertEqual(self.by_id["S2"].gates["G3_honesty"], "concern")
        self.assertEqual(self.by_id["S1"].gates["G3_honesty"], "pass")

    def test_strict_privacy_profile_turns_concern_into_fail(self):
        _, results, _ = score.compute(ROOT / "data" / "example", ROOT / "config",
                                      ROOT / "tasks" / "personal_battery.toml", "budget_privacy")
        s2 = next(r for r in results if r.setup_id == "S2")
        self.assertEqual(s2.gates["G1_privacy"], "fail")

    def test_scores_stay_in_range(self):
        for r in self.results:
            self.assertGreaterEqual(r.score, 0)
            self.assertLessEqual(r.score, 100)

    def test_markdown_renders(self):
        md = score.render_markdown(self.profile, self.results, self.warnings)
        self.assertIn("Everyday AI Index", md)
        self.assertIn("⚠", md)


class EdgeCaseTests(unittest.TestCase):
    def test_retired_and_unknown_benchmarks_are_ignored_with_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            write_csv(d / "setups.csv", ["setup_id", "label", "model_id"], [["X", "X", "MX"]])
            write_csv(d / "public_scores.csv", ["model_id", "benchmark_id", "value"],
                      [["MX", "mmlu", "99"], ["MX", "tau_bench", "70"]])
            _, results, warnings = score.compute(d, ROOT / "config", ROOT / "tasks" / "personal_battery.toml", None)
            self.assertEqual(results[0].layers["A"], 100)
            self.assertTrue(any("mmlu" in w for w in warnings))


class BlindRoundTripTests(unittest.TestCase):
    def test_make_then_merge_restores_setup_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            for setup in ("alpha", "beta"):
                (tmp / "outputs" / setup).mkdir(parents=True)
                (tmp / "outputs" / setup / "T01.md").write_text(f"answer from {setup}")
            blind.make(tmp / "outputs", tmp / "blinded")

            # No setup names leak into the blinded folder.
            for f in (tmp / "blinded").rglob("*.md"):
                self.assertNotIn("alpha", f.name)
                self.assertNotIn("beta", f.name)

            grading = tmp / "blinded" / "grading.csv"
            with grading.open() as fh:
                rows = list(csv.DictReader(fh))
            for r in rows:
                r["outcome"] = "2"
            write_csv(grading, list(rows[0].keys()), [list(r.values()) for r in rows])
            write_csv(tmp / "run_log.csv", ["setup_id", "task_id", "minutes", "nudges"],
                      [["alpha", "T01", "5", "0"], ["beta", "T01", "9", "2"]])

            out = tmp / "personal_results.csv"
            blind.merge(tmp / "blinded", tmp / "run_log.csv", out)
            with out.open() as fh:
                merged = {r["setup_id"]: r for r in csv.DictReader(fh)}
            self.assertEqual(set(merged), {"alpha", "beta"})
            self.assertEqual(merged["beta"]["minutes"], "9")


if __name__ == "__main__":
    unittest.main()
