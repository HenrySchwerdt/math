import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'research/ecdlp/experiments/lib'))
from toyec import Curve, dlog_bruteforce, dlog_bsgs  # noqa: E402


class ToyECTest(unittest.TestCase):
    def test_group_law_and_dlog(self):
        rng = random.Random(20261103)
        for p in (101, 103, 211, 1009):
            for _ in range(3):
                while True:
                    try:
                        E = Curve(rng.randrange(p), rng.randrange(p), p)
                        break
                    except ValueError:
                        continue
                pts = E.points()
                n = len(pts)
                self.assertLessEqual(abs(n - (p + 1)), 2 * p ** 0.5)
                for _ in range(20):
                    P, Q, R = (rng.choice(pts) for _ in range(3))
                    self.assertTrue(E.on_curve(E.add(P, Q)))
                    self.assertEqual(E.add(P, Q), E.add(Q, P))
                    self.assertEqual(E.add(E.add(P, Q), R), E.add(P, E.add(Q, R)))
                    self.assertIsNone(E.mul(n, P))
                    k = rng.randrange(n)
                    T = E.mul(k, P)
                    o = E.point_order(P, n)
                    self.assertEqual(dlog_bruteforce(E, P, T), k % o)
                    self.assertEqual(dlog_bsgs(E, P, T, o), k % o)


if __name__ == '__main__':
    unittest.main()
