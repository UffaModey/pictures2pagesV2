from unittest import TestCase
from fastapi.testclient import TestClient
from pictures2pages_v2.app.application import create_application


class TestBaseEventHandler(TestCase):
    def test_startup_handler(self):
        app = create_application()
        with self.assertLogs("pictures2pages_v2", level="INFO") as cm:

            with TestClient(app):
                pass
            self.assertEqual(
                cm.output,
                [
                    "INFO:pictures2pages_v2:Starting up ...",
                    "INFO:pictures2pages_v2:Shutting down ...",
                ],
            )
