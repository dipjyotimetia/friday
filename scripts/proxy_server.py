import socket
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer


class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the requested URL
        url = self.path
        if not url.startswith("http"):
            url = "http://" + self.path

        try:
            # Make the request to the target server
            response = urllib.request.urlopen(url)

            # Set response headers
            self.send_response(response.status)
            for header, value in response.getheaders():
                self.send_header(header, value)
            self.end_headers()

            # Send the response body
            self.wfile.write(response.read())

        except urllib.error.URLError as e:
            self.send_error(500, str(e))
        except Exception as e:
            self.send_error(500, str(e))

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)

        url = self.path
        if not url.startswith("http"):
            url = "http://" + self.path

        try:
            # Create POST request
            req = urllib.request.Request(
                url, data=post_data, headers=dict(self.headers)
            )

            # Make the request
            response = urllib.request.urlopen(req)

            # Send response
            self.send_response(response.status)
            for header, value in response.getheaders():
                self.send_header(header, value)
            self.end_headers()

            self.wfile.write(response.read())

        except urllib.error.URLError as e:
            self.send_error(500, str(e))
        except Exception as e:
            self.send_error(500, str(e))


def run_proxy_server(host="localhost", port=8000):
    try:
        server = HTTPServer((host, port), ProxyHandler)
        print(f"Starting proxy server on {host}:{port}")
        server.serve_forever()
    except socket.error as e:
        print(f"Failed to start server: {e}")
    except KeyboardInterrupt:
        print("Shutting down server...")
        server.shutdown()


if __name__ == "__main__":
    run_proxy_server()
