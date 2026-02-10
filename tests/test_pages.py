from daily_ops_agent.domain.change_detection import hash_text


def test_hash_text_stable():
    assert hash_text("abc") == hash_text("abc")
    assert hash_text("abc") != hash_text("abcd")
