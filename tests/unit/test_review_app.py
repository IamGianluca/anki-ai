import pytest

from anki_ai.entrypoints.review_note_changes import ReviewApp


class FakeInputProvider:
    def __init__(self, inputs):
        self.inputs = inputs
        self.index = 0

    def __call__(self, prompt):
        out = self.inputs[self.index]
        self.index += 1
        return out


@pytest.mark.parametrize("inputs,n_reviews", [(["Y"], 1), (["Y", "N"], 2)])
def test_review_one_or_more_notes(deck, inputs, n_reviews):
    # Given
    fake_input = FakeInputProvider(inputs)
    ra = ReviewApp(deck, deck, input_provider=fake_input)
    assert ra.n_reviewed() == 0

    # When
    ra.review(n_reviews=n_reviews)

    # Then
    assert ra.n_reviewed() == n_reviews


def test_save_reviewapp_state(tmp_path, deck):
    # Given
    fpath = tmp_path / "out.txt"
    inputs = ["Y", "N"]
    fake_input = FakeInputProvider(inputs)
    ra = ReviewApp(deck, deck, input_provider=fake_input)
    ra.review(n_reviews=2)

    # When
    ra.save(fpath=fpath)

    # Then
    assert fpath.read_text() == "first\tTrue\nsecond\tFalse\n"


def test_load_reviewapp_state(tmp_path, deck):
    # Given
    fpath = tmp_path / "in.txt"
    fpath.write_text("first\tTrue\nsecond\tFalse\n")
    ra = ReviewApp(deck, deck)

    # Then
    assert ra.n_reviewed() == 0

    # When
    ra.load(fpath)

    # Then
    assert ra.n_reviewed() == 2


def test_reviewapp_collision(tmp_path, deck):
    # Given
    fpath = tmp_path / "out.txt"
    inputs = ["Y", "N"]
    fake_input = FakeInputProvider(inputs)
    ra = ReviewApp(deck, deck, input_provider=fake_input)
    ra.review(n_reviews=2)

    assert ra.n_reviewed() == 2

    ra.save(fpath=fpath)

    # When
    ra.load(fpath)

    # Then
    assert ra.n_reviewed() == 2

    # Given
    fpath = tmp_path / "in.txt"
    fpath.write_text("first\tTrue\nsecond\tFalse\n")
    ra = ReviewApp(deck, deck)

    # Then
    assert ra.n_reviewed() == 0

    # When
    ra.load(fpath)

    # Then
    assert ra.n_reviewed() == 2
