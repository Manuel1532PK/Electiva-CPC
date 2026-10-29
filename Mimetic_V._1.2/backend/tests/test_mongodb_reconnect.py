import unittest
from unittest.mock import AsyncMock, MagicMock, Mock, patch

from app.database import mongodb


def _failing_db_client(error: Exception):
    """Cliente simulado cuya conexión al ping falla siempre."""
    client_inst = MagicMock()
    db_mock = Mock()
    db_mock.command = AsyncMock(side_effect=error)
    client_inst.__getitem__.return_value = db_mock
    return client_inst


def _healthy_db_client():
    """Cliente simulado que responde al ping correctamente."""
    client_inst = MagicMock()
    db_mock = Mock()
    db_mock.command = AsyncMock(return_value=1)
    client_inst.__getitem__.return_value = db_mock
    return client_inst


class TestConnectDb(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self._old_client, self._old_db = mongodb.client, mongodb.db

    async def asyncTearDown(self):
        mongodb.client, mongodb.db = self._old_client, self._old_db

    @patch("app.database.mongodb.create_indexes", new_callable=AsyncMock)
    @patch("app.database.mongodb.asyncio.sleep", new_callable=AsyncMock)
    @patch("app.database.mongodb.AsyncIOMotorClient")
    async def test_reintenta_y_falla_despues_de_max_retries(self, mock_client_class, mock_sleep, mock_indexes):
        mock_client_class.return_value = _failing_db_client(RuntimeError("offline"))

        result = await mongodb.connect_db(max_retries=2, server_selection_timeout_ms=2000)

        self.assertIs(result, False)
        self.assertEqual(mock_client_class.call_count, 2)
        self.assertIsNone(mongodb.client)
        self.assertIsNone(mongodb.db)
        mock_indexes.assert_not_awaited()

    @patch("app.database.mongodb.create_indexes", new_callable=AsyncMock)
    @patch("app.database.mongodb.asyncio.sleep", new_callable=AsyncMock)
    @patch("app.database.mongodb.AsyncIOMotorClient")
    async def test_amplia_exito_tras_primer_intento_fallido(self, mock_client_class, mock_sleep, mock_indexes):
        attempts = iter([
            _failing_db_client(TimeoutError("slow")),
            _healthy_db_client(),
        ])
        mock_client_class.side_effect = lambda *a, **k: next(attempts)

        result = await mongodb.connect_db(max_retries=3, server_selection_timeout_ms=2000)

        self.assertIs(result, True)
        self.assertEqual(mock_client_class.call_count, 2)
        self.assertIsNotNone(mongodb.client)
        self.assertIsNotNone(mongodb.db)
        mock_indexes.assert_awaited_once()

    @patch("app.database.mongodb.create_indexes", new_callable=AsyncMock)
    @patch("app.database.mongodb.asyncio.sleep", new_callable=AsyncMock)
    @patch("app.database.mongodb.AsyncIOMotorClient")
    async def test_exito_cierra_el_cliente_anterior(self, mock_client_class, mock_sleep, mock_indexes):
        old_client = _healthy_db_client()
        mongodb.client = old_client
        new_client = _healthy_db_client()
        mock_client_class.return_value = new_client

        result = await mongodb.connect_db(max_retries=1)

        self.assertIs(result, True)
        old_client.close.assert_called_once()
        self.assertIs(mongodb.client, new_client)

    @patch("app.database.mongodb.asyncio.sleep", new_callable=AsyncMock)
    @patch("app.database.mongodb.AsyncIOMotorClient")
    async def test_falla_no_cierra_cliente_anterior_sano(self, mock_client_class, mock_sleep):
        old_client = _healthy_db_client()
        mongodb.client = old_client
        mock_client_class.return_value = _failing_db_client(RuntimeError("offline"))

        result = await mongodb.connect_db(max_retries=1)

        self.assertIs(result, False)
        old_client.close.assert_not_called()
        self.assertIsNone(mongodb.client)
        self.assertIsNone(mongodb.db)


class TestDbIsReady(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self._old_db = mongodb.db

    async def asyncTearDown(self):
        mongodb.db = self._old_db

    async def test_false_cuando_no_hay_db(self):
        mongodb.db = None
        self.assertIs(await mongodb.db_is_ready(), False)

    async def test_true_cuando_ping_responde(self):
        db_mock = Mock()
        db_mock.command = AsyncMock(return_value=1)
        mongodb.db = db_mock
        self.assertIs(await mongodb.db_is_ready(), True)
        db_mock.command.assert_awaited_once_with("ping")

    async def test_false_cuando_ping_falla(self):
        db_mock = Mock()
        db_mock.command = AsyncMock(side_effect=RuntimeError("down"))
        mongodb.db = db_mock
        self.assertIs(await mongodb.db_is_ready(), False)


class TestEnsureConnected(unittest.IsolatedAsyncioTestCase):

    @patch("app.database.mongodb.connect_db", new_callable=AsyncMock, return_value=True)
    @patch("app.database.mongodb.db_is_ready", new_callable=AsyncMock, return_value=False)
    async def test_reconecta_cuando_db_inactiva(self, mock_ready, mock_connect):
        result = await mongodb.ensure_connected()
        self.assertIs(result, True)
        mock_connect.assert_awaited_once_with(
            max_retries=1,
            server_selection_timeout_ms=mongodb.DB_HEALTH_SELECTION_TIMEOUT_MS,
        )

    @patch("app.database.mongodb.connect_db", new_callable=AsyncMock)
    @patch("app.database.mongodb.db_is_ready", new_callable=AsyncMock, return_value=True)
    async def test_no_reconecta_cuando_db_sana(self, mock_ready, mock_connect):
        result = await mongodb.ensure_connected()
        self.assertIs(result, True)
        mock_connect.assert_not_awaited()


if __name__ == "__main__":
    unittest.main(verbosity=2)