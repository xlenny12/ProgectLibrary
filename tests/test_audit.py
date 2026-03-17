from app.core import audit


def test_log_and_verify():
    audit.log("user-1", "TEST_ACTION", {"key": "value"})
    ok, tampered = audit.verify_integrity()
    assert ok
    assert tampered == []


def test_replay_returns_events():
    audit.log("user-1", "USER_CREATED", {"email": "a@b.com"})
    events = audit.replay_events()
    assert len(events) >= 1
    assert events[-1]["action"] == "USER_CREATED"


def test_tampered_log_detected(tmp_path):
    audit.log("user-1", "SENSITIVE", {})
    path = tmp_path / "audit.dat"
    raw = path.read_bytes()
    # decrypt, corrupt, re-encrypt with same key
    from app.core.crypto import decrypt, encrypt
    plaintext = decrypt(raw)
    corrupted = plaintext.replace("SENSITIVE", "TAMPERED_EXTERNALLY")
    path.write_bytes(encrypt(corrupted))
    ok, tampered = audit.verify_integrity()
    assert not ok
    assert len(tampered) == 1
