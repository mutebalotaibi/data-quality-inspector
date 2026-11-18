"""Regression checks for the synthetic training datasets.

Run with: python -m unittest discover -s tests -v
"""

from __future__ import annotations

import csv
import re
import unittest
from datetime import date
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_PATH = DATA_DIR / "customers_raw.csv"
REFERENCE_PATH = DATA_DIR / "customers_clean_reference.csv"
EXPECTED_FIELDS = [
    "customer_id", "full_name", "email", "mobile_number", "national_id",
    "city", "date_of_birth", "registration_date", "last_updated_at", "customer_status",
]
VALID_CITIES = {"الرياض", "جدة", "الدمام", "مكة المكرمة", "المدينة المنورة", "أبها", "تبوك"}
VALID_STATUSES = {"نشط", "غير نشط", "معلق"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as csv_file:
        return list(csv.DictReader(csv_file))


class GeneratedCustomerDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.reference = read_csv(REFERENCE_PATH)
        cls.raw = read_csv(RAW_PATH)

    def test_both_files_have_expected_schema_and_size(self) -> None:
        self.assertEqual(len(self.reference), 120)
        self.assertEqual(len(self.raw), 120)
        self.assertEqual(list(self.reference[0]), EXPECTED_FIELDS)
        self.assertEqual(list(self.raw[0]), EXPECTED_FIELDS)

    def test_reference_data_is_valid_baseline(self) -> None:
        for record in self.reference:
            self.assertRegex(record["customer_id"], r"^CUST-\d{5}$")
            self.assertRegex(record["email"], r"^customer\d{3}@example\.test$")
            self.assertRegex(record["mobile_number"], r"^05\d{8}$")
            self.assertRegex(record["national_id"], r"^1\d{9}$")
            self.assertIn(record["city"], VALID_CITIES)
            self.assertIn(record["customer_status"], VALID_STATUSES)
            self.assertLess(date.fromisoformat(record["date_of_birth"]), date.fromisoformat(record["registration_date"]))

    def test_raw_data_keeps_record_identifiers_for_reference_comparison(self) -> None:
        self.assertEqual(
            [record["customer_id"] for record in self.raw],
            [record["customer_id"] for record in self.reference],
        )

    def test_raw_data_contains_known_examples_of_each_dimension(self) -> None:
        self.assertEqual(self.raw[2]["email"], "")
        self.assertEqual(self.raw[5]["email"], "not-an-email")
        self.assertGreater(date.fromisoformat(self.raw[20]["date_of_birth"]), date.fromisoformat(self.raw[20]["registration_date"]))
        self.assertEqual(self.raw[24]["last_updated_at"], "2025-08-12")
        self.assertNotEqual(self.raw[30]["full_name"], self.reference[30]["full_name"])
        self.assertEqual(self.raw[80]["email"], self.raw[79]["email"])


if __name__ == "__main__":
    unittest.main()
