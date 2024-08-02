from src.utils import generate_auth_code, format_duration, time_since


def test_generate_auth_code():
    code = generate_auth_code()
    assert len(code) == 6
    assert code.isalnum()


def test_format_duration():
    assert format_duration(3600) == '1.00 ч.'
    assert format_duration(60) == '1.00 мин.'
    assert format_duration(10) == '10.00 сек.'


def test_time_since():
    assert time_since(1234567890)
