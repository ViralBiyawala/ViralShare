import os
import socket
import threading
import tkinter as tk
from tkinter import messagebox
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
error_logger = logging.getLogger('error_logger')
access_logger = logging.getLogger('access_logger')
error_handler = logging.FileHandler('error.log')
access_handler = logging.FileHandler('access.log')
error_handler.setLevel(logging.ERROR)
access_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
error_handler.setFormatter(formatter)
access_handler.setFormatter(formatter)
error_logger.addHandler(error_handler)
access_logger.addHandler(access_handler)

done_event = threading.Event()
peered = set()

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        s.connect(('10.254.254.254', 1))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = '127.0.0.1'
    finally:
        s.close()
    return local_ip

class Peer:
    def __init__(self, host, port, password):
        self.host = host
        self.port = port
        self.password = password
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        self.files = []
        self.peers = []
        self.running = True

    def start(self):
        threading.Thread(target=self.listen).start()
        share_folder = 'share'
    
        # Check if the 'share' folder exists, if not, create it
        if not os.path.exists(share_folder):
            os.makedirs(share_folder)
            access_logger.info(f"Created folder: {share_folder}")
            
        download_folder = 'download'
    
        # Check if the 'download' folder exists, if not, create it
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)
            access_logger.info(f"Created folder: {download_folder}")

        access_logger.info(f"Server started on {self.host}:{self.port}")

    def listen(self):
        while self.running:
            try:
                client_socket, client_address = self.socket.accept()
                threading.Thread(target=self.handle_client, args=(client_socket, client_address)).start()
            except OSError:
                return

    def handle_client(self, client_socket, client_address):
        try:
            while self.running:
                request = client_socket.recv(1024).decode('utf-8')
                if not request:
                    break

                if request.startswith("connect"):
                    self.list_files()
                    peer_host, peer_port, peer_password = request.split()[1:4]
                    if self.validate_password(peer_password):
                        access_logger.info(f"Server connected to {peer_host}:{peer_port}")
                        client_socket.send("OK".encode('utf-8'))
                    else:
                        error_logger.info(f"wrong password from {peer_host}:{peer_port}")
                        client_socket.send("WRONG_PASSWORD".encode('utf-8'))
                elif request == "list":
                    client_socket.send(self.list_files().encode('utf-8'))
                elif request.startswith("download"):
                    access_logger.info(f"os.curdir: {os.getcwd()}")
                    filename = request.split()[1]
                    filepath = os.path.join('share', filename)
                    if filename in self.files:
                        file_size = os.path.getsize(filepath)
                        client_socket.send(f"OK {file_size}".encode('utf-8'))
                        with open(filepath, 'rb') as f:
                            while True:
                                data = f.read(1024 * 1024)
                                if not data:
                                    break
                                client_socket.send(data)
                        access_logger.info(f"Server sent file {filename} to {client_address}")
                    else:
                        error_logger.error(f"File {filename} not found")
                        client_socket.send("ERROR 0".encode('utf-8'))
                elif request.startswith("disconnect"):
                    peer_host, peer_port = request.split()[1:3]
                    self.remove_peer(peer_host, int(peer_port))
                    access_logger.info(f"Server disconnected from {peer_host}:{peer_port}")
                    break  # Disconnect and exit loop
        except Exception as e:
            error_logger.error(f"Error handling client {client_address}: {e}")
        finally:
            client_socket.close()

    def download(self, filename):
        # access_logger.info(f"os.curdir: {os.getcwd()}")
        # filename = os.path.join(os.getcwd(),'share', filename)
        for peer_host, peer_port, peer_socket in self.peers:
            try:
                peer_socket.send(f"download {filename}".encode('utf-8'))
                access_logger.info(f"Requesting {filename} from {peer_host}:{peer_port}")
                response = peer_socket.recv(1024).decode('utf-8')
                if response.startswith("OK"):
                    file_size = int(response.split()[1])
                    filepath = os.path.join('download', filename)
                    with open(filepath, 'wb') as f:
                        received = 0
                        while received < file_size:
                            data = peer_socket.recv(1024 * 1024)
                            if not data:
                                break
                            f.write(data)
                            received += len(data)
                    access_logger.info(f"Downloaded {filename} from {peer_host}:{peer_port}")
                    return True
                elif response.startswith("ERROR"):
                    error_logger.error(f"{peer_host}:{peer_port} does not have file {filename}")
            except Exception as e:
                error_logger.error(f"Error downloading from {peer_host}:{peer_port}: {e}")
        error_logger.error(f"Could not download {filename} from any peers")
        return False

    def list_files(self):
        access_logger.info("Listing files")
        share_folder = 'share'
        # List all files in the 'share' folder
        self.files = [f for f in os.listdir(share_folder) if os.path.isfile(os.path.join(share_folder, f))]

        return "\n".join(self.files)


    def validate_password(self, password):
        return password == self.password

    def connect(self, peer_host, peer_port, peer_password):
        try:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.connect((peer_host, peer_port))
            peer_socket.send(f"connect {self.host} {self.port} {peer_password}".encode('utf-8'))
            response = peer_socket.recv(1024).decode('utf-8')
            if response == "OK":
                self.remote_connect(peer_host, peer_port, peer_socket)
                access_logger.info(f"Connected to {peer_host}:{peer_port}")
                return True
            else:
                error_logger.error(f"Connection failed: {response}")
                peer_socket.close()
                return False
        except Exception as e:
            error_logger.error(f"Connection to {peer_host}:{peer_port} failed: {e}")
            return False

    def remote_connect(self, peer_host, peer_port, peer_socket):
        try:
            self.peers.append((peer_host, peer_port, peer_socket))
            return True
        except Exception as e:
            error_logger.error(f"Connection to {peer_host}:{peer_port} failed: {e}")
            return False

    def disconnect(self, peer_host, peer_port):
        self.remove_peer(peer_host, peer_port)

    def list_all_files(self):
        all_files = {}
        for peer_host, peer_port, peer_socket in self.peers:
            try:
                peer_socket.send("list".encode('utf-8'))
                response = peer_socket.recv(4096).decode('utf-8')
                if response:
                    all_files[f"{peer_host}:{peer_port}"] = response.split("\n")
                    access_logger.info(f"Received files list from {peer_host}:{peer_port}")
            except Exception as e:
                error_logger.error(f"Error listing files from {peer_host}:{peer_port}: {e}")
        return all_files

    def remove_peer(self, peer_host, peer_port):
        for peer in self.peers:
            if peer[0] == peer_host and peer[1] == int(peer_port):
                peer[2].close()
                self.peers.remove(peer)
                break

    def stop(self):
        self.running = False
        self.socket.close()
        for _, _, peer_socket in self.peers:
            peer_socket.close()
            
class PeerGUI:
    def __init__(self, master):
        self.master = master
        master.title("ViralShare - Peer to Peer File Sharing without the Internet")

        self.peer = None

        # Frame for left column (operations and inputs)
        self.left_frame = tk.Frame(master)
        self.left_frame.grid(row=0, column=0, sticky="nsew")

        # Start Server Section
        self.start_server_frame = tk.LabelFrame(self.left_frame, text="Start Server", padx=10, pady=10)
        self.start_server_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.host_label = tk.Label(self.start_server_frame, text="Host (Local IP):")
        self.host_label.grid(row=0, column=0, sticky="e")
        self.host_value_label = tk.Label(self.start_server_frame, text=get_local_ip())
        self.host_value_label.grid(row=0, column=1)
        self.port_label = tk.Label(self.start_server_frame, text="Port:")
        self.port_label.grid(row=1, column=0, sticky="e")
        self.port_entry = tk.Entry(self.start_server_frame)
        self.port_entry.grid(row=1, column=1)
        self.password_label = tk.Label(self.start_server_frame, text="Password:")
        self.password_label.grid(row=2, column=0, sticky="e")
        self.password_entry = tk.Entry(self.start_server_frame, show="*")
        self.password_entry.grid(row=2, column=1)
        self.start_server_button = tk.Button(self.start_server_frame, text="Start Server", command=self.start_server)
        self.start_server_button.grid(row=3, column=1, pady=10)

        # Connect to Peer Section
        self.connect_peer_frame = tk.LabelFrame(self.left_frame, text="Connect to Peer", padx=10, pady=10)
        self.connect_peer_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.peer_host_label = tk.Label(self.connect_peer_frame, text="Peer Host:")
        self.peer_host_label.grid(row=0, column=0, sticky="e")
        self.peer_host_entry = tk.Entry(self.connect_peer_frame)
        self.peer_host_entry.grid(row=0, column=1)
        self.peer_port_label = tk.Label(self.connect_peer_frame, text="Peer Port:")
        self.peer_port_label.grid(row=1, column=0, sticky="e")
        self.peer_port_entry = tk.Entry(self.connect_peer_frame)
        self.peer_port_entry.grid(row=1, column=1)
        self.peer_password_label = tk.Label(self.connect_peer_frame, text="Peer Password:")
        self.peer_password_label.grid(row=2, column=0, sticky="e")
        self.peer_password_entry = tk.Entry(self.connect_peer_frame, show="*")
        self.peer_password_entry.grid(row=2, column=1)
        self.connect_to_peer_button = tk.Button(self.connect_peer_frame, text="Connect", command=self.connect_to_peer)
        self.connect_to_peer_button.grid(row=3, column=1, pady=10)

        # File Operations Section
        self.file_frame = tk.LabelFrame(self.left_frame, text="File Operations", padx=10, pady=10)
        self.file_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        self.list_files_button = tk.Button(self.file_frame, text="List Files", command=self.list_files)
        self.list_files_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.list_all_files_button = tk.Button(self.file_frame, text="List All Files", command=self.list_all_files)
        self.list_all_files_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.download_file_label = tk.Label(self.file_frame, text="Download File:")
        self.download_file_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.download_file_entry = tk.Entry(self.file_frame)
        self.download_file_entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        self.download_button = tk.Button(self.file_frame, text="Download", command=self.download_file)
        self.download_button.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

        # Listbox to display files
        self.file_listbox = tk.Listbox(master, width=80, height=20)
        self.file_listbox.grid(row=0, column=1, rowspan=3, padx=10, pady=10, sticky="news")

        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(1, weight=1)

        master.protocol("WM_DELETE_WINDOW", self.on_closing)

    # Methods remain unchanged...

    def start_server(self):
        host = self.host_value_label.cget("text")
        port = self.port_entry.get()
        password = self.password_entry.get()
        if not port or not password:
            messagebox.showerror("Error", "All fields must be filled")
            return
        self.peer = Peer(host, int(port), password)
        self.peer.start()
        messagebox.showinfo("Success", "Server started successfully")

    def connect_to_peer(self):
        peer_host = self.peer_host_entry.get()
        peer_port = self.peer_port_entry.get()
        peer_password = self.peer_password_entry.get()
        if not peer_host or not peer_port or not peer_password:
            messagebox.showerror("Error", "All fields must be filled")
            return
        if not self.peer:
            messagebox.showerror("Error", "You must start your server first")
            return
        try:
            if self.peer.connect(peer_host, int(peer_port), peer_password):
                messagebox.showinfo("Success", "Connected to peer successfully")
            else:
                messagebox.showerror("Error", "Failed to connect to peer")
        except Exception as e:
            messagebox.showerror("Error", f"Connection to peer failed: {e}")

    def list_files(self):
        if not self.peer:
            messagebox.showerror("Error", "Not connected to peer")
            return
        self.file_listbox.delete(0, tk.END)
        files = self.peer.list_files().split("\n")
        for file in files:
            self.file_listbox.insert(tk.END, file)

    def list_all_files(self):
        if not self.peer:
            messagebox.showerror("Error", "Not connected to peer")
            return
        self.file_listbox.delete(0, tk.END)
        all_files = self.peer.list_all_files()
        for peer, files in all_files.items():
            self.file_listbox.insert(tk.END, f"Files from {peer}:")
            for file in files:
                self.file_listbox.insert(tk.END, f" {file}")

    def download_file(self):
        if not self.peer:
            messagebox.showerror("Error", "Not connected to peer")
            return
        filename = self.download_file_entry.get()
        if not filename:
            messagebox.showerror("Error", "Please enter a file name")
            return
        try:
            if self.peer.download(filename):
                messagebox.showinfo("Success", f"File {filename} downloaded successfully")
            else:
                messagebox.showerror("Error", f"Failed to download file {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download file {filename}: {e}")

    def on_closing(self):
        if self.peer:
            self.peer.stop()
        self.master.destroy()

def run_gui():
    root = tk.Tk()
    app = PeerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    gui_thread = threading.Thread(target=run_gui)
    gui_thread.start()
