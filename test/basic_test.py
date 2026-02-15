import unittest

from ry_testkit import PostgresOnlyTestBase, RedisOnlyTestBase


class BasicTest(unittest.TestCase):
    def test_exports(self) -> None:
        self.assertIsNotNone(PostgresOnlyTestBase)
        self.assertIsNotNone(RedisOnlyTestBase)
