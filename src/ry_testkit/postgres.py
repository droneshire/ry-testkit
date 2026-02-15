import os
import time
import typing as T
import unittest

import psycopg2
from psycopg2 import OperationalError
from testcontainers.core.container import DockerContainer  # type: ignore[import-untyped]
from testcontainers.core.waiting_utils import wait_for_logs  # type: ignore[import-untyped]


class PostgresOnlyTestBase(unittest.TestCase):
    container: T.Optional[DockerContainer] = None
    _started = False

    IMAGE = os.getenv("TEST_POSTGRES_IMAGE", "postgres:latest")
    USER = os.getenv("TEST_POSTGRES_USER", "test")
    PASSWORD = os.getenv("TEST_POSTGRES_PASSWORD", "test")
    DB = os.getenv("TEST_POSTGRES_DB", "testdb")
    READY_TIMEOUT_S = int(os.getenv("TEST_POSTGRES_READY_TIMEOUT_S", "60"))
    READY_SLEEP_S = float(os.getenv("TEST_POSTGRES_READY_SLEEP_S", "0.5"))

    @classmethod
    def _dsn(cls) -> str:
        assert cls.container is not None
        return (
            f"dbname={cls.DB} user={cls.USER} password={cls.PASSWORD} "
            f"host={cls.container.get_container_host_ip()} "
            f"port={cls.container.get_exposed_port(5432)}"
        )

    @classmethod
    def _wait_ready(cls) -> None:
        deadline = time.time() + cls.READY_TIMEOUT_S
        while time.time() < deadline:
            try:
                conn = psycopg2.connect(cls._dsn())
                conn.close()
                return
            except OperationalError:
                time.sleep(cls.READY_SLEEP_S)
        raise RuntimeError("Postgres test container did not become ready")

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        if cls._started:
            return

        c = DockerContainer(cls.IMAGE)
        c.with_env("POSTGRES_USER", cls.USER)
        c.with_env("POSTGRES_PASSWORD", cls.PASSWORD)
        c.with_env("POSTGRES_DB", cls.DB)
        c.with_exposed_ports(5432)
        c.start()

        try:
            wait_for_logs(
                c, "database system is ready to accept connections", timeout=cls.READY_TIMEOUT_S
            )
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
    def postgres_connection_info(cls) -> T.Dict[str, T.Any]:
        assert cls.container is not None
        return {
            "host": cls.container.get_container_host_ip(),
            "port": int(cls.container.get_exposed_port(5432)),
            "user": cls.USER,
            "password": cls.PASSWORD,
            "dbname": cls.DB,
        }
