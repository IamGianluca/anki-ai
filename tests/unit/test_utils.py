from conftest import create_fake_file_str


def test_create_fake_test_file(note1):
    # When
    result = create_fake_file_str(notes=[note1])

    # Then
    header = "#separator:tab\n#html:true\n#guid column:1\n#notetype column:2\n#deck column:3\n#tags column:9\n"
    file_str = f"{note1.guid}\t{note1.notetype}\t{note1.deck_name}\t{note1.front}\t{note1.back}\t\t\t\t{note1.tags}\n"
    expected = header + file_str
    assert expected == result
