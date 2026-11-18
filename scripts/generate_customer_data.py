"""Generate safe, synthetic customer datasets for the data-quality project.

The raw dataset deliberately contains controlled quality issues.  The clean
reference dataset contains the expected source values before those issues are
introduced; it is useful for validating the accuracy dimension later.
"""

from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_FILE = DATA_DIR / "customers_raw.csv"
REFERENCE_FILE = DATA_DIR / "customers_clean_reference.csv"
RANDOM_SEED = 20261118
CUSTOMER_COUNT = 120

FIELDNAMES = [
    "customer_id",
    "full_name",
    "email",
    "mobile_number",
    "national_id",
    "city",
    "date_of_birth",
    "registration_date",
    "last_updated_at",
    "customer_status",
]

FIRST_NAMES = [
    "أحمد", "سارة", "محمد", "نورة", "خالد", "ريم", "عبدالله", "الجوهرة",
    "فهد", "دانة", "تركي", "مها", "عمر", "ليان", "ماجد", "هيا",
]
LAST_NAMES = [
    "العتيبي", "القحطاني", "الغامدي", "الحربي", "المطيري", "الشهري",
    "الزهراني", "الشمري", "الدوسري", "السبيعي",
]
CITIES = ["الرياض", "جدة", "الدمام", "مكة المكرمة", "المدينة المنورة", "أبها", "تبوك"]
STATUSES = ["نشط", "غير نشط", "معلق"]


def iso_date_between(start: date, end: date) -> str:
    return (start + timedelta(days=random.randint(0, (end - start).days))).isoformat()


def build_clean_record(index: int) -> dict[str, str]:
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    full_name = f"{first_name} {last_name}"
    latin_email = f"customer{index:03d}@example.test"
    birth_date = iso_date_between(date(1965, 1, 1), date(2004, 12, 31))
    registration_date = iso_date_between(date(2022, 1, 1), date(2026, 8, 31))
    return {
        "customer_id": f"CUST-{index:05d}",
        "full_name": full_name,
        "email": latin_email,
        "mobile_number": f"05{random.randint(0, 9)}{random.randint(1000000, 9999999)}",
        "national_id": f"1{random.randint(100000000, 999999999)}",
        "city": random.choice(CITIES),
        "date_of_birth": birth_date,
        "registration_date": registration_date,
        "last_updated_at": iso_date_between(date(2026, 9, 1), date(2026, 11, 18)),
        "customer_status": random.choice(STATUSES),
    }


def introduce_quality_issues(records: list[dict[str, str]]) -> list[dict[str, str]]:
    """Return a copy with deterministic, intentional quality issues."""
    raw = [record.copy() for record in records]

    # Completeness: mandatory fields missing.
    raw[2]["email"] = ""
    raw[7]["mobile_number"] = ""
    raw[15]["city"] = ""
    raw[26]["national_id"] = ""

    # Validity: invalid syntax or values outside the controlled domain.
    raw[5]["email"] = "not-an-email"
    raw[11]["mobile_number"] = "056123"  # Too short.
    raw[18]["national_id"] = "ABC12345"
    raw[33]["city"] = "الرياضض"
    raw[41]["customer_status"] = "قيد المراجعة"
    raw[52]["date_of_birth"] = "1991/13/40"

    # Consistency: values that disagree with another field.
    raw[20]["date_of_birth"] = "2030-05-10"  # Date of birth after registration.
    raw[46]["registration_date"] = "2021-12-31"  # Outside expected business period.

    # Timeliness: source has not been refreshed within the intended 90-day SLA.
    raw[24]["last_updated_at"] = "2025-08-12"
    raw[70]["last_updated_at"] = "2026-01-05"

    # Accuracy: differs from the reference value; requires authoritative source.
    raw[30]["full_name"] = "اسم غير مطابق"
    raw[61]["city"] = "جدة" if records[61]["city"] != "جدة" else "الرياض"

    # Uniqueness: duplicate business identifiers. Retain different record IDs to
    # represent duplicate customer registrations, not merely duplicate rows.
    raw[80]["email"] = raw[79]["email"]
    raw[95]["national_id"] = raw[94]["national_id"]
    raw[110]["mobile_number"] = raw[109]["mobile_number"]

    return raw


def write_csv(path: Path, records: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(records)


def main() -> None:
    random.seed(RANDOM_SEED)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    clean_records = [build_clean_record(index) for index in range(1, CUSTOMER_COUNT + 1)]
    raw_records = introduce_quality_issues(clean_records)
    write_csv(REFERENCE_FILE, clean_records)
    write_csv(RAW_FILE, raw_records)
    print(f"Created {len(raw_records)} raw customer records: {RAW_FILE}")
    print(f"Created {len(clean_records)} reference records: {REFERENCE_FILE}")


if __name__ == "__main__":
    main()
