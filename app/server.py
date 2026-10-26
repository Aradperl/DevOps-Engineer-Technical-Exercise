#!/usr/bin/env python3
"""Tiny exercise web service. Python standard library only."""

import html
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.environ.get("PORT", "8080"))
MESSAGE = os.environ.get("MESSAGE", "hello from the exercise")
APP_VERSION = os.environ.get("APP_VERSION", "0.1.0")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/":
            self._send_html()
        elif path == "/healthz":
            self._send(200, "text/plain; charset=utf-8", b"ok\n")
        else:
            self._send(404, "text/plain; charset=utf-8", b"not found\n")

    def _send_html(self):
        hostname = os.environ.get("HOSTNAME", "unknown")
        page = (
            "<!DOCTYPE html>\n"
            '<html lang="en">\n'
            "<head>\n"
            '  <meta charset="utf-8">\n'
            "  <title>Exercise</title>\n"
            "</head>\n"
            "<body>\n"
            f"  <p>Message: {html.escape(MESSAGE)}</p>\n"
            f"  <p>Version: {html.escape(APP_VERSION)}</p>\n"
            f"  <p>Pod: {html.escape(hostname)}</p>\n"
            "</body>\n"
            "</html>\n"
        )
        self._send(200, "text/html; charset=utf-8", page.encode("utf-8"))

    def _send(self, status, content_type, body):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        return


def main():
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
