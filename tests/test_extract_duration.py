from src.sync import extract_duration
import unittest

class TestExtractDuration(unittest.TestCase):
    """
    Unit tests for the extract_duration function.
    """
    
    def test_minutes_only(self):
        """
        Test cases where the duration is specified in minutes only.
        """
        self.assertEqual(extract_duration("Sample text [45m]"), 45, "Failed for [45m]")
        self.assertEqual(extract_duration("Sample text [15 minutos]"), 15, "Failed for [15 minutos]")
        self.assertEqual(extract_duration("Sample text [15minutes]"), 15, "Failed for [15minutes]")
        self.assertEqual(extract_duration("Sample text [152]"), 152, "Failed for [152]")
        self.assertEqual(extract_duration("Sample text [25]"), 25, "Failed for [25]")

    def test_hours_only(self):
        """
        Test cases where the duration is specified in hours only.
        """
        self.assertEqual(extract_duration("Sample [2h] text"), 120, "Failed for [2h]")
        self.assertEqual(extract_duration("Sample text [2hours]"), 120, "Failed for [2hours]")
        self.assertEqual(extract_duration("Sample text [1hora]"), 60, "Failed for [1hora]")
        self.assertEqual(extract_duration("Sample text [5horas]"), 300, "Failed for [5horas]")
    
    def test_hours_and_minutes(self):
        """
        Test cases where the duration is specified in both hours and minutes.
        """
        self.assertEqual(extract_duration("Sample text [2h2m]"), 122, "Failed for [2h2m]")
        self.assertEqual(extract_duration("Sample text [2h04m]"), 124, "Failed for [2h04m]")

    def test_invalid_or_missing_duration(self):
        """
        Test cases where the duration is invalid or missing.
        """
        self.assertIsNone(extract_duration("Do nothing"), "Failed for invalid case 'Do nothing'")
        self.assertIsNone(extract_duration("No duration here []"), "Failed for invalid case 'No duration here []'")
        self.assertIsNone(extract_duration("Invalid [time]"), "Failed for invalid case 'Invalid [time]'")

    def test_multiple_durations(self):
        """
        Test cases where multiple durations are specified in the summary.
        """
        self.assertEqual(extract_duration("Sample text [60] [1m]"), 61, "Failed for [60] [1m]")
        self.assertEqual(extract_duration("Workout [30m] [2h]"), 150, "Failed for [30m] [2h]")
        self.assertEqual(extract_duration("Read book [90] [1h]"), 150, "Failed for [90] [1h]")
        self.assertEqual(extract_duration("Cook dinner [2h30m] [15m]"), 165, "Failed for [2h30m] [15m]")
        self.assertEqual(extract_duration("Meeting [1h] [45m]"), 105, "Failed for [1h] [45m]")
        self.assertEqual(extract_duration("Meeting [1h] []"), 60, "Failed for [1h] []")
        self.assertEqual(extract_duration("Meeting [40] [time]"), 40, "Failed for [40] [time]")

if __name__ == '__main__':
    unittest.main()
