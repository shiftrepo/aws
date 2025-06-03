#!/usr/bin/env python3

import http.server
import socketserver

PORT = 8080
DIRECTORY = "."

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

if __name__ == "__main__":
    handler = Handler
    
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"サーバーを開始しました。http://localhost:{PORT} にアクセスしてください。")
        print("サーバーを停止するには、Ctrl+Cを押してください。")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nサーバーを停止しています...")
            httpd.server_close()
            print("サーバーを停止しました。")