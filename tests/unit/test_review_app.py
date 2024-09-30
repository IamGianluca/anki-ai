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


def test_review_one_note(deck):
    # given
    inputs = ["Y"]
    fake_input = FakeInputProvider(inputs)
    ra = ReviewApp(deck, input_provider=fake_input)
    assert ra.n_reviewed() == 0

    # when
    ra.review(n_reviews=1)

    # then
    assert ra.n_reviewed() == 1
