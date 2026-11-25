"""Offline synthetic proof-of-work primitives. No networking or signing."""
import hashlib

PREFIX = "glp-ai-forum-v1"
MAX_ATTEMPTS = 2**23

def work_message(token, counter):
    if not isinstance(token, str) or not token or len(token) > 4096 or not token.isascii() or any(ord(c) < 33 or ord(c) > 126 for c in token):
        raise ValueError("invalid token")
    if type(counter) is not int or not 0 <= counter < 2**64:
        raise ValueError("invalid counter")
    return f"{PREFIX}\n{token}\n{counter}".encode("ascii")

def has_work(digest, bits):
    if type(bits) is not int or not 0 <= bits <= 256 or len(digest) != 32:
        raise ValueError("invalid digest or difficulty")
    return int.from_bytes(digest, "big") >> (256 - bits) == 0

def solve_fixture(token, bits, attempts=100000):
    """Synthetic fixtures only; deliberately limited to low difficulty."""
    if not token.startswith("synthetic-"):
        raise ValueError("only synthetic tokens accepted")
    if type(bits) is not int or not 0 <= bits <= 12:
        raise ValueError("fixture difficulty outside bounds")
    if type(attempts) is not int or not 1 <= attempts <= MAX_ATTEMPTS:
        raise ValueError("invalid attempt limit")
    for counter in range(attempts):
        if has_work(hashlib.sha256(work_message(token, counter)).digest(), bits):
            return counter
    return None

def self_test():
    assert work_message("synthetic-test", 12) == b"glp-ai-forum-v1\nsynthetic-test\n12"
    assert has_work(bytes.fromhex("000f" + "ff"*30), 12)
    assert not has_work(bytes.fromhex("0010" + "00"*30), 12)
    assert has_work(b"\xff"*32, 0)
    assert has_work(bytes(32), 256)
    counter = solve_fixture("synthetic-test", 10)
    assert counter == 841
    assert hashlib.sha256(work_message("synthetic-test", counter)).hexdigest() == "00074e81ca20f35e98a72c0a318cb33457521ed08dd0a0a346a5675e62095024"
    assert has_work(hashlib.sha256(work_message("synthetic-test", counter)).digest(), 10)
    assert all(not has_work(hashlib.sha256(work_message("synthetic-test", n)).digest(), 10) for n in range(counter))
    for token, bits in [("real-token", 10), ("synthetic-test", 20)]:
        try:
            solve_fixture(token, bits)
        except ValueError:
            pass
        else:
            raise AssertionError("unsafe input accepted")
    print("offline fixture tests passed")

if __name__ == "__main__":
    self_test()
