import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import http.server
import socketserver
import socket
import webbrowser

class WiFiTransferApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Wi-Fi Video Transfer")
        self.root.geometry("500x450")
        
        self.server_thread = None
        self.httpd = None
        self.port = 8000
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(main_frame, text="Wi-Fi Video Transfer to iPhone", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Instructions
        instructions = """
        Transfer videos to iPhone over Wi-Fi:
        
        1. Connect PC and iPhone to same Wi-Fi network
        2. Select a folder with videos
        3. Start the server
        4. Open the provided URL on your iPhone
        5. Download videos directly to your iPhone
        
        No cables required!
        """
        
        info_text = tk.Text(main_frame, height=8, width=50, wrap=tk.WORD, font=("Arial", 9))
        info_text.insert(tk.END, instructions)
        info_text.config(state=tk.DISABLED)
        info_text.pack(pady=10)
        
        # Folder selection
        folder_frame = ttk.Frame(main_frame)
        folder_frame.pack(fill=tk.X, pady=10)
        
        self.folder_var = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        ttk.Label(folder_frame, text="Videos Folder:").pack(anchor=tk.W)
        
        folder_select_frame = ttk.Frame(folder_frame)
        folder_select_frame.pack(fill=tk.X, pady=5)
        
        self.folder_entry = ttk.Entry(folder_select_frame, textvariable=self.folder_var, width=40)
        self.folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(folder_select_frame, text="Browse", command=self.browse_folder)
        browse_btn.pack(side=tk.RIGHT)
        
        # Server info
        self.info_var = tk.StringVar(value="Server not started")
        info_label = ttk.Label(main_frame, textvariable=self.info_var, font=("Arial", 10, "bold"))
        info_label.pack(pady=10)
        
        self.url_var = tk.StringVar(value="")
        url_label = ttk.Label(main_frame, textvariable=self.url_var, foreground="blue", 
                             font=("Arial", 9), cursor="hand2")
        url_label.pack(pady=5)
        url_label.bind("<Button-1>", self.open_url)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        self.start_btn = ttk.Button(button_frame, text="Start Server", command=self.start_server)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(button_frame, text="Stop Server", command=self.stop_server, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.open_btn = ttk.Button(button_frame, text="Open in Browser", command=self.open_browser)
        self.open_btn.pack(side=tk.LEFT, padx=5)
        
        self.exit_btn = ttk.Button(button_frame, text="Exit", command=self.exit_app)
        self.exit_btn.pack(side=tk.LEFT, padx=5)
        
    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.folder_var.get())
        if folder:
            self.folder_var.set(folder)
            
    def start_server(self):
        folder = self.folder_var.get()
        if not os.path.exists(folder):
            messagebox.showerror("Error", "Folder does not exist!")
            return

        # Change to the selected directory
        os.chdir(folder)
        
        # Start HTTP server in a thread
        self.server_thread = threading.Thread(target=self.run_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        # Get local IP address
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect((socket.gethostbyname(socket.gethostname()), 80))
            ip_address = s.getsockname()[0]
            s.close()
            
            url = f"http://{ip_address}:{self.port}"
            self.url_var.set(url)
            self.info_var.set(f"Server running on: {ip_address}")
            
        except Exception as e:
            self.info_var.set("Could not get IP address")
            
    def run_server(self):
        try:
            handler = http.server.SimpleHTTPRequestHandler
            self.httpd = socketserver.TCPServer(("", self.port), handler)
            self.info_var.set(f"Server started on port {self.port}")
            self.httpd.serve_forever()
        except Exception as e:
            self.info_var.set(f"Server error: {str(e)}")
            
    def stop_server(self):
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
            self.httpd = None
            
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.info_var.set("Server stopped")
        self.url_var.set("")
        
    def open_url(self, event):
        webbrowser.open(self.url_var.get())
        
    def open_browser(self):
        if self.url_var.get():
            webbrowser.open(self.url_var.get())
        else:
            messagebox.showinfo("Info", "Start the server first to get the URL")
            
    def exit_app(self):
        self.stop_server()
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.root.quit()

def main():
    root = tk.Tk()
    app = WiFiTransferApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()