from get_issuing_certs import get_certificates


def test_get_certificates() -> None:
    assert get_certificates("google.com", "443") is not None
