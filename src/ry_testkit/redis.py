import os
import time
import typing as T
import unittest

import redis
from redis import RedisError
from testcontainers.core.container import DockerContainer  # type: ignore[import-untyped]
from testcontainers.core.waiting_utils import wait_for_logs  # type: ignore[import-untyped]


class RedisOnlyTestBase(unittest.TestCase):
    container: T.Optional[DockerContainer] = None
    _started = False

    IMAGE = os.getenv("TEST_REDIS_IMAGE", "redis:latest")
    READY_TIMEOUT_S = int(os.getenv("TEST_REDIS_READY_TIMEOUT_S", "60"))
    READY_SLEEP_S = float(os.getenv("TEST_REDIS_READY_SLEEP_S", "0.5"))

    @classmethod
    def _client(cls) -> redis.Redis:
        assert cls.container is not None
        return redis.Redis(
            host=cls.container.get_container_host_ip(),
            port=int(cls.container.get_exposed_port(6379)),
            db=0,
            decode_responses=True,
        )

    @classmethod
    def _wait_ready(cls) -> None:
        deadline = time.time() + cls.READY_TIMEOUT_S
        while time.time() < deadline:
            try:
                if cls._client().ping():
                    return
            except RedisError:
                time.sleep(cls.READY_SLEEP_S)
        raise RuntimeError("Redis test container did not become ready")

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        if cls._started:
            return

        c = DockerContainer(cls.IMAGE)
        c.with_exposed_ports(6379)
        c.start()

        try:
            wait_for_logs(c, "Ready to accept connections", timeout=cls.READY_TIMEOUT_S)
        except Exception:
            pass

        cls.container = c
        cls._wait_ready()
        cls._started = True

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.container is not None:
            cls.container.stop()
            cls.container = None
        cls._started = False
        super().tearDownClass()

    @classmethod
    def redis_connection_info(cls) -> T.Dict[str, T.Any]:
        assert cls.container is not None
        return {
            "host": cls.container.get_container_host_ip(),
            "port": int(cls.container.get_exposed_port(6379)),
            "db": 0,
        }
