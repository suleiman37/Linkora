from app.utils.short_codes import ALPHABET, CODE_LENGTH, generate_short_code


def test_generated_short_code_uses_approved_format() -> None:
    code = generate_short_code()

    assert len(code) == CODE_LENGTH
    assert all(character in ALPHABET for character in code)