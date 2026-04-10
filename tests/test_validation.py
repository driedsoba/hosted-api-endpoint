import pytest
from pydantic import ValidationError

from app.models.fun_fact import FunFactCreate


class TestFunRatingBoundaries:
    def test_rating_of_1_is_valid(self):
        fact = FunFactCreate(
            category="tech", title="Min", fact="Minimum rating", fun_rating=1
        )
        assert fact.fun_rating == 1

    def test_rating_of_10_is_valid(self):
        fact = FunFactCreate(
            category="tech", title="Max", fact="Maximum rating", fun_rating=10
        )
        assert fact.fun_rating == 10

    def test_rating_of_0_is_invalid(self):
        with pytest.raises(ValidationError):
            FunFactCreate(
                category="tech", title="Zero", fact="Too low", fun_rating=0
            )

    def test_rating_of_11_is_invalid(self):
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
    def test_all_valid_categories(self):
        for cat in ["hobbies", "food", "travel", "music", "sports", "tech", "random"]:
            fact = FunFactCreate(
                category=cat, title=f"Test {cat}", fact="Content", fun_rating=5
            )
            assert fact.category.value == cat

    def test_invalid_category_rejected(self):
        with pytest.raises(ValidationError):
            FunFactCreate(
                category="science",
                title="Bad Cat",
                fact="Invalid category",
                fun_rating=5,
            )


class TestStringValidation:
    def test_whitespace_only_title_rejected(self):
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
        with pytest.raises(ValidationError):
            FunFactCreate(
                category="tech",
                title="x" * 101,
                fact="Valid fact",
                fun_rating=5,
            )

    def test_fact_over_500_chars_rejected(self):
        with pytest.raises(ValidationError):
            FunFactCreate(
                category="tech",
                title="Valid",
                fact="x" * 501,
                fun_rating=5,
            )

    def test_whitespace_is_stripped_before_validation(self):
        fact = FunFactCreate(
            category="tech",
            title="  padded title  ",
            fact="  padded fact  ",
            fun_rating=5,
        )
        assert fact.title == "padded title"
        assert fact.fact == "padded fact"
