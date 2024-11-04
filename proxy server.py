import http.server
import socketserver
import requests
import tkinter as tk
from tkinter import messagebox
import threading
import webbrowser
import time

PORT = 8080
server_thread = None  # Global variable to hold the server thread
httpd = None  # Global variable for the server instance

class Proxy(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        target_url = 'http://' + self.path[1:]  # Remove leading slash
        try:
            response = requests.get(target_url)
            self.send_response(response.status_code)
            self.send_header('Content-Type', response.headers['Content-Type'])
            self.end_headers()
            self.wfile.write(response.content)
        except Exception as e:
            self.send_error(500, 'Internal Server Error: ' + str(e))

def run_proxy():
    global httpd
    httpd = socketserver.TCPServer(("", PORT), Proxy)
    print(f"Serving at port {PORT}")
    httpd.serve_forever()

def stop_proxy():
    global httpd
    if httpd:
        httpd.shutdown()
        print("Proxy stopped.")
        httpd.server_close()

class ProxyServerApp:
    def __init__(self, master):
        self.master = master
        master.title("Simple Proxy Server")

        self.start_button = tk.Button(master, text="Start Proxy", command=self.start_proxy)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(master, text="Stop Proxy", command=self.stop_proxy, state=tk.DISABLED)
        self.stop_button.pack(pady=10)

        self.url_entry = tk.Entry(master, width=50)
        self.url_entry.pack(pady=10)
        self.url_entry.insert(0, "Enter URL here (without http://)")

        self.label = tk.Label(master, text="")
        self.label.pack(pady=10)

    def start_proxy(self):
        # Disable the button to prevent multiple clicks
        self.start_button.config(state=tk.DISABLED)
        url = self.url_entry.get()
        if not url:
            messagebox.showwarning("Warning", "Please enter a URL.")
            self.start_button.config(state=tk.NORMAL)
            return

        global server_thread
        if server_thread is None or not server_thread.is_alive():
            server_thread = threading.Thread(target=run_proxy)
            server_thread.start()
            self.label.config(text=f"Proxy running at http://localhost:{PORT}")

        # Open the URL in the browser with the proxy
        webbrowser.open(f'http://localhost:{PORT}/{url}')
        self.stop_button.config(state=tk.NORMAL)

    def stop_proxy(self):
        stop_proxy()
        self.label.config(text="Proxy stopped.")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = ProxyServerApp(root)
    root.mainloop()
