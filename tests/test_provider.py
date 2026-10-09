import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

from faultpilot.provider import diagnose_with_ollama


class MockOllamaHandler(BaseHTTPRequestHandler):
    request_payload = None

    def do_POST(self):
        self.__class__.request_payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        body = json.dumps({
            "response": json.dumps({
                "category": "shape_mismatch",
                "cause": "The matrix widths differ.",
                "evidence": "shapes cannot be multiplied",
            }),
            "prompt_eval_count": 17,
            "eval_count": 12,
        }).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args):
        pass


class ProviderContractTests(unittest.TestCase):
    def test_local_http_contract(self):
        server = HTTPServer(("127.0.0.1", 0), MockOllamaHandler)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            result = diagnose_with_ollama(
                {"case_id": "x", "traceback": "shapes cannot be multiplied"},
                "test-model",
                f"http://127.0.0.1:{server.server_port}/api/generate",
            )
        finally:
            server.shutdown()
            worker.join(timeout=2)
            server.server_close()
        self.assertEqual(MockOllamaHandler.request_payload["model"], "test-model")
        self.assertFalse(MockOllamaHandler.request_payload["stream"])
        self.assertEqual(result["category"], "shape_mismatch")
        self.assertEqual(result["status"], "model_diagnosis_unverified")
        self.assertEqual(result["prompt_tokens"], 17)
