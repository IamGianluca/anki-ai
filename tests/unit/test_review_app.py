import pytest

from anki_ai.entrypoints.review_notes_changes import ReviewApp


class FakeInputProvider:
    def __init__(self, inputs):
        self.inputs = inputs
        self.index = 0

    def __call__(self, prompt):
        return self.inputs[self.index]


def test_add_deck_to_review_app(deck):
    # when
    ra = ReviewApp(deck)

    # then
    assert ra.deck == deck


@pytest.mark.parametrize("inputs,n_reviews", [(["Y"], 1), (["Y", "N"], 2)])
def test_review_one_or_more_notes(deck, inputs, n_reviews):
    # given
    fake_input = FakeInputProvider(inputs)
    ra = ReviewApp(deck, input_provider=fake_input)
    assert ra.n_reviewed() == 0

    # when
    ra.review(n_reviews=n_reviews)

    # then
    assert ra.n_reviewed() == n_reviews
