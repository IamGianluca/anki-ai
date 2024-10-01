import pytest

from anki_ai.entrypoints.review_notes_changes import ReviewApp


class FakeInputProvider:
    def __init__(self, inputs):
        self.inputs = inputs
        self.index = 0

    def __call__(self, prompt):
        out = self.inputs[self.index]
        self.index += 1
        return out


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


def test_save_reviewapp_state(tmp_path, deck):
    # given
    fpath = tmp_path / "out.txt"
    inputs = ["Y", "N"]
    fake_input = FakeInputProvider(inputs)
    ra = ReviewApp(deck, input_provider=fake_input)
    ra.review(n_reviews=2)

    # when
    ra.save(fpath=fpath)

    # then
    assert fpath.read_text() == "first\tTrue\nsecond\tFalse\n"


def test_load_reviewapp_state(tmp_path, deck):
    # given
    fpath = tmp_path / "in.txt"
    fpath.write_text("first\tTrue\nsecond\tFalse\n")
    ra = ReviewApp(deck)

    # then
    assert ra.n_reviewed() == 0

    # when
    ra.load(fpath)

    # then
    assert ra.n_reviewed() == 2


def test_reviewapp_collision(tmp_path, deck):
    # given
    fpath = tmp_path / "out.txt"
    inputs = ["Y", "N"]
    fake_input = FakeInputProvider(inputs)
    ra = ReviewApp(deck, input_provider=fake_input)
    ra.review(n_reviews=2)

    assert ra.n_reviewed() == 2

    ra.save(fpath=fpath)

    # when
    ra.load(fpath)

    # then
    assert ra.n_reviewed() == 2

    # given
    fpath = tmp_path / "in.txt"
    fpath.write_text("first\tTrue\nsecond\tFalse\n")
    ra = ReviewApp(deck)

    # then
    assert ra.n_reviewed() == 0

    # when
    ra.load(fpath)

    # then
    assert ra.n_reviewed() == 2
