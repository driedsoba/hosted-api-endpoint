"""Unit tests for Pydantic model validation rules.

These tests validate the FunFactCreate model in isolation - no HTTP,
no service, no repository. They verify that Pydantic rejects invalid
input before it ever reaches the business logic.

Boundary value testing is used for numeric fields (testing at, just below,
and just above the valid range) to catch off-by-one errors in constraints.
"""

import pytest
from pydantic import ValidationError

from app.models.fun_fact import FunFactCreate


class TestFunRatingBoundaries:
    """fun_rating must be an integer between 1 and 10 inclusive.
    Tests the boundaries: valid edges (1, 10) and invalid neighbours (0, 11, -1).
    """

    def test_rating_of_1_is_valid(self):
        """Lower boundary - minimum allowed value."""
        fact = FunFactCreate(
            category="tech", title="Min", fact="Minimum rating", fun_rating=1
        )
        assert fact.fun_rating == 1

    def test_rating_of_10_is_valid(self):
        """Upper boundary - maximum allowed value."""
        fact = FunFactCreate(
            category="tech", title="Max", fact="Maximum rating", fun_rating=10
        )
        assert fact.fun_rating == 10

    def test_rating_of_0_is_invalid(self):
        """Just below lower boundary."""
        with pytest.raises(ValidationError):
            FunFactCreate(
                category="tech", title="Zero", fact="Too low", fun_rating=0
            )

    def test_rating_of_11_is_invalid(self):
        """Just above upper boundary."""
        with pytest.raises(ValidationError):
            FunFactCreate(
                category="tech", title="Eleven", fact="Too high", fun_rating=11
            )

    def test_negative_rating_is_invalid(self):
        with pytest.raises(ValidationError):
            FunFactCreate(
                category="tech", title="Negative", fact="Way too low", fun_rating=-1
            )


class TestCategoryValidation:
    """Category is an enum - only predefined values are accepted."""

    def test_all_valid_categories(self):
        """Exhaustively verify every allowed category value."""
        for cat in ["hobbies", "food", "travel", "music", "sports", "tech", "random"]:
            fact = FunFactCreate(
                category=cat, title=f"Test {cat}", fact="Content", fun_rating=5
            )
            assert fact.category.value == cat

    def test_invalid_category_rejected(self):
        """Arbitrary strings not in the enum are rejected."""
        with pytest.raises(ValidationError):
            FunFactCreate(
                category="science",
                title="Bad Cat",
                fact="Invalid category",
                fun_rating=5,
            )


class TestStringValidation:
    """String fields have length constraints and whitespace stripping.

    The strip_whitespace validator runs before min_length, which means
    a title of "   " becomes "" and then fails the min_length=1 check.
    """

    def test_whitespace_only_title_rejected(self):
        """Whitespace is stripped first, leaving an empty string that fails min_length."""
        with pytest.raises(ValidationError):
            FunFactCreate(
                category="tech", title="   ", fact="Valid fact", fun_rating=5
            )

    def test_empty_title_rejected(self):
        with pytest.raises(ValidationError):
            FunFactCreate(
                category="tech", title="", fact="Valid fact", fun_rating=5
            )

    def test_title_over_100_chars_rejected(self):
        """Title max_length is 100 characters."""
        with pytest.raises(ValidationError):
            FunFactCreate(
                category="tech",
                title="x" * 101,
                fact="Valid fact",
                fun_rating=5,
            )

    def test_fact_over_500_chars_rejected(self):
        """Fact max_length is 500 characters."""
        with pytest.raises(ValidationError):
            FunFactCreate(
                category="tech",
                title="Valid",
                fact="x" * 501,
                fun_rating=5,
            )

    def test_whitespace_is_stripped_before_validation(self):
        """Leading/trailing whitespace is removed by the field_validator."""
        fact = FunFactCreate(
            category="tech",
            title="  padded title  ",
            fact="  padded fact  ",
            fun_rating=5,
        )
        assert fact.title == "padded title"
        assert fact.fact == "padded fact"
