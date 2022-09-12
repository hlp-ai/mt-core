import os

import tensorflow as tf

from yimt.core.tests import test_util
from yimt.core.utils import scorers


class ScorersTest(tf.test.TestCase):
    def _run_scorer(self, scorer, refs, hyps):
        ref_path = test_util.make_data_file(
            os.path.join(self.get_temp_dir(), "ref.txt"), refs
        )
        hyp_path = test_util.make_data_file(
            os.path.join(self.get_temp_dir(), "hyp.txt"), hyps
        )
        return scorer(ref_path, hyp_path)

    def testBLEUScorer(self):
        refs = ["Hello world !", "How is it going ?"]
        scorer = scorers.BLEUScorer()
        score = self._run_scorer(scorer, refs, refs)
        self.assertEqual(100, int(score))

    def testROUGEScorer(self):
        refs = ["Hello world !", "How is it going ?"]
        scorer = scorers.ROUGEScorer()
        score = self._run_scorer(scorer, refs, refs)
        self.assertIsInstance(score, dict)
        self.assertIn("rouge-l", score)
        self.assertIn("rouge-1", score)
        self.assertIn("rouge-2", score)
        self.assertAlmostEqual(1.0, score["rouge-1"])

    def testTERScorer(self):
        refs = ["Hello world !", "How is it going ?"]
        scorer = scorers.TERScorer()
        score = self._run_scorer(scorer, refs, refs)
        self.assertEqual(score, 0)

    def testMakeScorers(self):
        def _check_scorers(scorers, instances):
            self.assertLen(scorers, len(instances))
            for scorer, instance in zip(scorers, instances):
                self.assertIsInstance(scorer, instance)

        _check_scorers(scorers.make_scorers("bleu"), [scorers.BLEUScorer])
        _check_scorers(scorers.make_scorers("BLEU"), [scorers.BLEUScorer])
        _check_scorers(
            scorers.make_scorers(["BLEU", "rouge"]),
            [scorers.BLEUScorer, scorers.ROUGEScorer],
        )


if __name__ == "__main__":
    tf.test.main()
