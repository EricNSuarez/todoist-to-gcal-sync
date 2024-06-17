from src.sync import summaries_are_identical
import unittest

class TestSummariesAreIdentical(unittest.TestCase):
    
    def test_no_duration_in_summaries(self):
        """Test cases where no duration is specified in either summary."""
        self.assertTrue(summaries_are_identical("Buy groceries", "Buy groceries"))
        self.assertFalse(summaries_are_identical("Buy groceries", "Buy meat"))

    def test_no_duration_in_one_summary(self):
        """Test cases where the duration is specified in one summary only."""
        self.assertTrue(summaries_are_identical("Buy groceries [30m]", "Buy groceries"))
        self.assertTrue(summaries_are_identical("Buy groceries", "Buy groceries [45m]"))
        self.assertFalse(summaries_are_identical("Buy meat [30m]", "Buy groceries"))

    def test_different_durations_in_summaries(self):
        """Test cases where different durations are specified in the summaries."""
        self.assertTrue(summaries_are_identical("Buy groceries [30m]", "Buy groceries [45m]"))
        self.assertTrue(summaries_are_identical("Buy groceries [1h]", "Buy groceries [2 hours]"))

    def test_same_duration_different_summaries(self):
        """Test cases where the same duration is specified but summaries are different."""
        self.assertFalse(summaries_are_identical("Buy groceries [30m]", "Buy meat [30m]"))
        self.assertFalse(summaries_are_identical("Buy groceries [1h]", "Buy meat [1h]"))

    def test_various_durations(self):
        """Test cases where different formats of durations are specified."""
        self.assertTrue(summaries_are_identical("Buy groceries [1 hour]", "Buy groceries [60 mins]"))
        self.assertTrue(summaries_are_identical("Buy groceries [2h 30m]", "Buy groceries [2 hours 30 minutes]"))
        self.assertTrue(summaries_are_identical("Buy groceries [1 hour]", "Buy groceries [1 hour 30 mins] "))

if __name__ == "__main__":
    unittest.main()
