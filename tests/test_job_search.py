"""
Testy jednostkowe dla modułu job_search.py.

Uruchomienie:
    python -m pytest tests/ -v
    # lub
    python -m unittest discover tests/
"""

import unittest

from job_search import (
    JobListing,
    detect_benefits,
    detect_rotation,
    format_report_csv,
    format_report_json,
    format_report_text,
    meets_benefits_criteria,
    meets_rotation_criteria,
)


class TestDetectRotation(unittest.TestCase):
    def test_14_21_detected(self):
        self.assertEqual(detect_rotation("Rotation: 14/21"), "14/21")

    def test_14_14_detected(self):
        self.assertEqual(detect_rotation("schedule 14/14 offshore"), "14/14")

    def test_2_weeks_on_3_weeks_off(self):
        result = detect_rotation("2 weeks on / 3 weeks off")
        self.assertEqual(result, "2 weeks on / 3 weeks off")

    def test_no_rotation(self):
        self.assertEqual(detect_rotation("Full time permanent position"), "Nie podano")

    def test_numeric_pattern_fallback(self):
        result = detect_rotation("Working schedule: 4/4")
        self.assertEqual(result, "4/4")


class TestMeetsRotationCriteria(unittest.TestCase):
    def test_14_21_accepted(self):
        self.assertTrue(meets_rotation_criteria("14/21"))

    def test_14_14_accepted(self):
        self.assertTrue(meets_rotation_criteria("14/14"))

    def test_other_patterns_rejected(self):
        self.assertFalse(meets_rotation_criteria("4/4"))
        self.assertFalse(meets_rotation_criteria("Nie podano"))
        self.assertFalse(meets_rotation_criteria("28/28"))


class TestDetectBenefits(unittest.TestCase):
    def test_accommodation_detected(self):
        benefits = detect_benefits("Free accommodation and meals provided")
        self.assertIn("accommodation", benefits)

    def test_meals_detected(self):
        benefits = detect_benefits("meals included in the package")
        self.assertIn("meals", benefits)

    def test_polish_terms_detected(self):
        benefits = detect_benefits("zapewniamy zakwaterowanie i wyżywienie")
        self.assertIn("zakwaterowanie", benefits)
        self.assertIn("wyżywienie", benefits)

    def test_no_benefits(self):
        benefits = detect_benefits("competitive salary, car allowance")
        self.assertEqual(benefits, [])


class TestMeetsBenefitsCriteria(unittest.TestCase):
    def test_both_provided(self):
        self.assertTrue(meets_benefits_criteria(["accommodation", "meals"]))

    def test_only_accommodation(self):
        self.assertFalse(meets_benefits_criteria(["accommodation"]))

    def test_only_meals(self):
        self.assertFalse(meets_benefits_criteria(["meals"]))

    def test_polish_benefits(self):
        self.assertTrue(
            meets_benefits_criteria(["zakwaterowanie", "wyżywienie"])
        )

    def test_empty_benefits(self):
        self.assertFalse(meets_benefits_criteria([]))


class TestJobListing(unittest.TestCase):
    def _make_listing(self, rotation_ok=True, benefits_ok=True) -> JobListing:
        return JobListing(
            title="Scaffolder",
            company="Acme AS",
            location="Stavanger",
            meets_rotation_criteria=rotation_ok,
            meets_benefits_criteria=benefits_ok,
        )

    def test_meets_all_criteria_both_true(self):
        listing = self._make_listing(rotation_ok=True, benefits_ok=True)
        self.assertTrue(listing.meets_all_criteria())

    def test_meets_all_criteria_rotation_false(self):
        listing = self._make_listing(rotation_ok=False, benefits_ok=True)
        self.assertFalse(listing.meets_all_criteria())

    def test_meets_all_criteria_benefits_false(self):
        listing = self._make_listing(rotation_ok=True, benefits_ok=False)
        self.assertFalse(listing.meets_all_criteria())


class TestFormatReportText(unittest.TestCase):
    def setUp(self):
        self.listings = [
            JobListing(
                title="Scaffolder §17-4",
                company="Nordic Scaffolding AS",
                location="Stavanger",
                rotation_schedule="14/21",
                contract_type="Full-time",
                meets_rotation_criteria=True,
                meets_benefits_criteria=True,
                benefits=["accommodation", "meals"],
            ),
            JobListing(
                title="Industrial Painter NORSOK",
                company="Paint Pro AS",
                location="Bergen",
                rotation_schedule="28/28",
                contract_type="Contract",
                meets_rotation_criteria=False,
                meets_benefits_criteria=False,
            ),
        ]

    def test_contains_section_headers(self):
        report = format_report_text(self.listings)
        self.assertIn("1. PRZEGLĄD OFERT PRACY", report)
        self.assertIn("2. SZCZEGÓŁY OFERT PRACY", report)
        self.assertIn("3. KRYTERIA SELEKCJI OFERT", report)
        self.assertIn("4. ZASTOSOWANE SŁOWA KLUCZOWE", report)

    def test_contains_listing_data(self):
        report = format_report_text(self.listings)
        self.assertIn("Nordic Scaffolding AS", report)
        self.assertIn("14/21", report)

    def test_total_count_correct(self):
        report = format_report_text(self.listings)
        self.assertIn("2", report)

    def test_keywords_present(self):
        report = format_report_text(self.listings)
        self.assertIn("§17", report)
        self.assertIn("NORSOK M-501", report)


class TestFormatReportJson(unittest.TestCase):
    def test_valid_json(self):
        import json

        listings = [
            JobListing(
                title="Test Job",
                company="Test AS",
                location="Oslo",
            )
        ]
        output = format_report_json(listings)
        data = json.loads(output)
        self.assertIn("job_listings", data)
        self.assertEqual(len(data["job_listings"]), 1)
        self.assertIn("search_keywords", data)
        self.assertIn("selection_criteria", data)


class TestFormatReportCsv(unittest.TestCase):
    def test_csv_has_header(self):
        listings = [
            JobListing(
                title="Test Job",
                company="Test AS",
                location="Oslo",
            )
        ]
        output = format_report_csv(listings)
        self.assertIn("Firma", output)
        self.assertIn("Stanowisko", output)
        self.assertIn("Rotacja", output)

    def test_csv_row_count(self):
        listings = [
            JobListing(title="Job 1", company="Company A", location="Oslo"),
            JobListing(title="Job 2", company="Company B", location="Bergen"),
        ]
        output = format_report_csv(listings)
        lines = [ln for ln in output.strip().splitlines() if ln]
        # header + 2 data rows
        self.assertEqual(len(lines), 3)


if __name__ == "__main__":
    unittest.main()
