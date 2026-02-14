from ry_testkit import PostgresOnlyTestBase, RedisOnlyTestBase


def test_exports() -> None:
    assert PostgresOnlyTestBase is not None
    assert RedisOnlyTestBase is not None
