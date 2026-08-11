from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import Term


class TermTest(TestCase):
    def test_create_term_with_valid_dates(self):
        term = Term(
            title="Fall 2026",
            start_date="2026-09-01",
            end_date="2027-01-20",
            term_type="normal",
        )

        term.full_clean()
        term.save()

        self.assertEqual(term.title, "Fall 2026")
        self.assertEqual(term.term_type, "normal")

    def test_term_end_date_cannot_be_before_start_date(self):
        term = Term(
            title="Invalid Term",
            start_date="2026-09-01",
            end_date="2026-08-01",
            term_type="normal",
        )

        with self.assertRaises(ValidationError):
            term.full_clean()    