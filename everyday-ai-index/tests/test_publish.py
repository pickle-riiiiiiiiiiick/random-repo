import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "publish"))

import build  # noqa: E402
from ds import ticks, token_vars  # noqa: E402
from site_page import site_html  # noqa: E402
from slides import method_deck, results_deck  # noqa: E402

EXAMPLE = ROOT / "editions" / "000-example"


class DesignTokenTests(unittest.TestCase):
    def test_aliases_resolve_per_theme(self):
        light, dark = token_vars("light"), token_vars("dark")
        self.assertEqual(light["--series-1"], light["--green"])
        self.assertEqual(dark["--highlight"], dark["--red"])
        self.assertNotEqual(light["--paper"], dark["--paper"])

    def test_ticks_cover_range(self):
        t = ticks(0, 95, 4)
        self.assertEqual(t[0], 0)
        self.assertGreaterEqual(t[-1], 95)


class DeckTests(unittest.TestCase):
    def setUp(self):
        self.weights = build.weights()
        self.edition, self.profile, self.results, _, self.setups = build.score_edition(EXAMPLE)

    def test_method_deck_has_page_numbers(self):
        slides = method_deck(self.weights)
        self.assertGreaterEqual(len(slides), 4)
        self.assertIn(f"1 / {len(slides)}", slides[0])

    def test_results_deck_marks_illustrative_data(self):
        slides = results_deck(self.edition, self.profile, self.results, self.setups, self.weights)
        self.assertTrue(all("illustrative" in s.lower() or "link in the comments" in s for s in slides))

    def test_results_deck_adds_same_model_slide(self):
        slides = results_deck(self.edition, self.profile, self.results, self.setups, self.weights)
        self.assertTrue(any("Same model, different app" in s for s in slides))

    def test_provisional_setup_not_in_ranking_chart(self):
        slides = results_deck(self.edition, self.profile, self.results, self.setups, self.weights)
        ranking = slides[1]
        self.assertIn("Not ranked yet", ranking)
        self.assertNotIn(">Local model *<", ranking)

    def test_site_page_is_an_artifact_body(self):
        page = site_html([build.score_edition(EXAMPLE) + (EXAMPLE,)], self.weights)
        self.assertTrue(page.startswith("<title>"))
        self.assertNotIn("<html", page)
        self.assertIn('prefers-color-scheme: dark', page)


if __name__ == "__main__":
    unittest.main()
