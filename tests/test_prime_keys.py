# Tests for prime_gen.py and prime.py, run against real generated keys in a
# scratch directory so nothing touches the repo's own committed key files.

import base64
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Runs one of the two scripts as a subprocess inside the given directory, the
# way a real user would invoke them, rather than importing and monkeypatching
# module-level file paths.
def run(script, args, cwd):
    result = subprocess.run(
        [sys.executable, os.path.join(HERE, script)] + args,
        cwd=cwd, capture_output=True, text=True, timeout=30,
    )
    return result.returncode, result.stdout, result.stderr


class KeyGenerationTests(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.mkdtemp(prefix="prime-keys-test-")
        self.addCleanup(lambda: __import__("shutil").rmtree(self.work, ignore_errors=True))

    def test_newkey_writes_a_prime(self):
        code, out, err = run("prime_gen.py", ["seed-a", "-newkey", "--bits", "64"], self.work)
        self.assertEqual(code, 0, err)
        with open(os.path.join(self.work, "prime.key")) as f:
            value = int(f.read())
        self.assertGreater(value, 0)

    def test_privatekey_writes_a_prime(self):
        code, out, err = run("prime_gen.py", ["seed-a", "-privatekey", "--bits", "80"], self.work)
        self.assertEqual(code, 0, err)
        with open(os.path.join(self.work, "private.key")) as f:
            value = int(f.read())
        self.assertGreater(value, 0)

    def test_same_seed_gives_the_same_prime(self):
        run("prime_gen.py", ["repeat-me", "-newkey", "--bits", "64"], self.work)
        with open(os.path.join(self.work, "prime.key")) as f:
            first = f.read()
        os.remove(os.path.join(self.work, "prime.key"))
        run("prime_gen.py", ["repeat-me", "-newkey", "--bits", "64"], self.work)
        with open(os.path.join(self.work, "prime.key")) as f:
            second = f.read()
        self.assertEqual(first, second)

    def test_different_seeds_give_different_primes(self):
        run("prime_gen.py", ["seed-one", "-newkey", "--bits", "64"], self.work)
        with open(os.path.join(self.work, "prime.key")) as f:
            first = f.read()
        os.remove(os.path.join(self.work, "prime.key"))
        run("prime_gen.py", ["seed-two", "-newkey", "--bits", "64"], self.work)
        with open(os.path.join(self.work, "prime.key")) as f:
            second = f.read()
        self.assertNotEqual(first, second)

    def test_a_bit_size_under_the_floor_is_refused(self):
        code, out, err = run("prime_gen.py", ["seed-a", "-newkey", "--bits", "4"], self.work)
        self.assertNotEqual(code, 0)
        self.assertIn("bits", err)

    def test_default_run_needs_a_private_key(self):
        code, out, err = run("prime_gen.py", ["seed-a"], self.work)
        self.assertNotEqual(code, 0)
        self.assertIn("private.key not found", out + err)

    def test_default_run_reuses_an_existing_prime_key(self):
        run("prime_gen.py", ["seed-a", "-newkey", "--bits", "64"], self.work)
        with open(os.path.join(self.work, "prime.key")) as f:
            before = f.read()
        run("prime_gen.py", ["seed-a", "-privatekey", "--bits", "80"], self.work)
        run("prime_gen.py", ["seed-a"], self.work)
        with open(os.path.join(self.work, "prime.key")) as f:
            after = f.read()
        # the default run must not overwrite an existing prime.key
        self.assertEqual(before, after)


class RecoveryRoundTripTests(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.mkdtemp(prefix="prime-keys-recover-test-")
        self.addCleanup(lambda: __import__("shutil").rmtree(self.work, ignore_errors=True))
        run("prime_gen.py", ["seed-a", "-newkey", "--bits", "64"], self.work)
        run("prime_gen.py", ["seed-a", "-privatekey", "--bits", "80"], self.work)
        run("prime_gen.py", ["seed-a"], self.work)
        with open(os.path.join(self.work, "prime.key")) as f:
            self.key2 = int(f.read())

    def test_the_recovered_key_matches_the_generated_one(self):
        code, out, err = run("prime.py", [], self.work)
        self.assertEqual(code, 0, err)
        recovered = int(out.strip().split("key: ")[1])
        self.assertEqual(recovered, self.key2)

    def test_a_mismatched_private_key_is_reported_not_crashed(self):
        with open(os.path.join(self.work, "private.key"), "w") as f:
            f.write("999999999999999999999999")
        code, out, err = run("prime.py", [], self.work)
        self.assertEqual(code, 0)
        self.assertIn("does not evenly divide", out)

    def test_a_missing_pub_key_is_reported(self):
        os.remove(os.path.join(self.work, "pub.key"))
        code, out, err = run("prime.py", [], self.work)
        self.assertIn("Missing required key file", out)

    def test_a_zero_private_key_is_reported(self):
        with open(os.path.join(self.work, "private.key"), "w") as f:
            f.write("0")
        code, out, err = run("prime.py", [], self.work)
        self.assertIn("cannot be zero", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
