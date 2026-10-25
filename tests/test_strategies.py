import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.projector_remote import ProjectorRemote
from strategies.highest_priority_strategy import HighestPriorityStrategy
from strategies.first_available_strategy import FirstAvailableStrategy
from exceptions.device_exceptions import NoSuitableItemException


class TestStrategies(unittest.TestCase):
    def setUp(self):
        self.p1 = ProjectorRemote("PR01", "Remote 1", "Kho", battery_level=50)
        self.p2 = ProjectorRemote("PR02", "Remote 2", "Kho", battery_level=90)
        self.p3 = ProjectorRemote("PR03", "Remote 3", "Kho", battery_level=70)
        self.candidates = [self.p1, self.p2, self.p3]

    def test_highest_priority_strategy(self):
        strategy = HighestPriorityStrategy[ProjectorRemote](lambda d: d.get_default_priority_score())
        chosen = strategy.select(self.candidates)
        self.assertEqual(chosen.id, "PR02")
        self.assertEqual(chosen.battery_level, 90)

    def test_first_available_strategy(self):
        strategy = FirstAvailableStrategy[ProjectorRemote]()
        chosen = strategy.select(self.candidates)
        self.assertEqual(chosen.id, "PR01")

    def test_empty_candidates_raises_exception(self):
        hp_strategy = HighestPriorityStrategy[ProjectorRemote](lambda d: d.get_default_priority_score())
        fa_strategy = FirstAvailableStrategy[ProjectorRemote]()

        with self.assertRaises(NoSuitableItemException):
            hp_strategy.select([])

        with self.assertRaises(NoSuitableItemException):
            fa_strategy.select([])


if __name__ == "__main__":
    unittest.main()
