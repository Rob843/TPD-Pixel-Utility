# ============================================================================
# TPD FLAGGED NETWORK FLEET MANAGEMENT UTILITY (v1.2 - Pro-Grid Layout Fixed)
# ============================================================================
import socket
import struct
import tkinter as tk
from tkinter import messagebox, ttk

TPD_DISCOVER_PORT = 2711
TPD_CONFIG_PORT   = 2712
MAGIC_HEADER      = b"TPD_NET_CFG_MODE"

class TPDNetManager:
    def __init__(self, root):
        self.root = root
        self.root.title("TPD Professional Node Fleet Utility v1.2")
        self.root.geometry("740x560")
        self.root.minsize(700, 500)
        self.discovered_nodes = {}
        self.create_widgets()
        
    def create_widgets(self):
        # Top toolbar frame
        btn_frame = ttk.Frame(self.root, padding=10)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="Scan School Network", command=self.discover_fleet).pack(side=tk.LEFT, padx=5)
        
        # Grid table
        self.tree = ttk.Treeview(btn_frame, columns=("IP", "Subnet", "Type", "Port1_Uni", "ColorOrder"), show="headings")
        self.tree.heading("IP", text="Node IP Address")
        self.tree.heading("Subnet", text="Subnet Mask")
        self.tree.heading("Type", text="Chip Protocol")
        self.tree.heading("Port1_Uni", text="Output 1 Universe")
        self.tree.heading("ColorOrder", text="Color Map (1-4)")
        
        self.tree.column("IP", width=130, anchor=tk.CENTER)
        self.tree.column("Subnet", width=130, anchor=tk.CENTER)
        self.tree.column("Type", width=110, anchor=tk.CENTER)
        self.tree.column("Port1_Uni", width=120, anchor=tk.CENTER)
        self.tree.column("ColorOrder", width=130, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Parameter Editor Workspace Form
        edit_frame = ttk.LabelFrame(self.root, text=" Target Node Parameters Editor ", padding=15)
        edit_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        edit_frame.columnconfigure(1, weight=1, minsize=180)
        edit_frame.columnconfigure(3, weight=1, minsize=180)
        
        # Row 0: IP Address and Subnet configuration inputs
        ttk.Label(edit_frame, text="Target IP Address:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=8)
        self.ent_ip = ttk.Entry(edit_frame)
        self.ent_ip.insert(0, "10.101.1.50")
        self.ent_ip.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=8)
        
        ttk.Label(edit_frame, text="Target Subnet Mask:").grid(row=0, column=2, sticky=tk.W, padx=20, pady=8)
        self.ent_sub = ttk.Entry(edit_frame)
        self.ent_sub.insert(0, "255.255.255.0")
        self.ent_sub.grid(row=0, column=3, sticky=tk.EW, padx=5, pady=8)
        
        # Row 1: Starting universe and Protocol Selection Dropdown
        ttk.Label(edit_frame, text="Port 1 Start Universe:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=8)
        self.ent_uni = ttk.Entry(edit_frame)
        self.ent_uni.insert(0, "1")
        self.ent_uni.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=8)
        
        ttk.Label(edit_frame, text="Dynamic Pixel Protocol:").grid(row=1, column=2, sticky=tk.W, padx=20, pady=8)
        self.combo_color = ttk.Combobox(edit_frame, state="readonly", values=[
            "RGBW (1234)", "RGB (123)", "GRBW (2134)", "GRB (213)", 
            "WRGB (4123)", "BRGW (3124)"
        ])
        self.combo_color.set("RGBW (1234)")
        self.combo_color.grid(row=1, column=3, sticky=tk.EW, padx=5, pady=8)
        
        # FIXED: Changed the button from .pack() to .grid() to stop the layout crash!
        btn_submit = ttk.Button(edit_frame, text="Transmit Configuration to Node", command=self.push_config)
        btn_submit.grid(row=2, column=0, columnspan=4, sticky=tk.EW, pady=20)

    def discover_fleet(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        self.discovered_nodes.clear()
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(1.0)
        
        try:
            sock.sendto(MAGIC_HEADER + b"\x01", ('255.255.255.255', TPD_DISCOVER_PORT))
            while True:
                data, addr = sock.recvfrom(1024)
                if data.startswith(MAGIC_HEADER):
                    header, ip0, ip1, ip2, ip3, sub0, sub1, sub2, sub3, p1_uni, strip_t, c0, c1, c2, c3 = struct.unpack("<16sBBBBBBBHHBBBBB", data[:31])
                    
                    ip_str = f"{ip0}.{ip1}.{ip2}.{ip3}"
                    sub_str = f"{sub0}.{sub1}.{sub2}.{sub3}"
                    color_str = f"{c0}.{c1}.{c2}.{c3}"
                    type_str = "4-Ch RGBW" if strip_t == 0 else "3-Ch RGB"
                    
                    self.discovered_nodes[ip_str] = {"ip": ip_str, "uni": p1_uni, "type": strip_t}
                    self.tree.insert("", tk.END, values=(ip_str, sub_str, type_str, p1_uni, color_str))
        except socket.timeout:
            pass
        finally:
            sock.close()

    def push_config(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Selection Error", "Please scan and select a controller node from the table list.")
            return
            
        node_values = self.tree.item(selected, "values")
        current_node_ip = node_values
        
        try:
            ip_parts = [int(x) for x in self.ent_ip.get().split('.')]
            sub_parts = [int(x) for x in self.ent_sub.get().split('.')]
            if len(ip_parts) != 4 or len(sub_parts) != 4: raise ValueError
        except ValueError:
            messagebox.showerror("Format Error", "IP and Subnet fields must be standard octet blocks (e.g. 10.101.1.50)")
            return
            
        new_uni = int(self.ent_uni.get())
        color_choice = self.combo_color.get()
        strip_type = 1 if "RGB (" in color_choice or "GRB (" in color_choice else 0
        
        matrix_map = {
            "RGBW (1234)": (1,2,3,4), "RGB (123)":  (1,2,3,1),
            "GRBW (2134)": (2,1,3,4), "GRB (213)":  (2,1,3,1),
            "WRGB (4123)": (4,1,2,3), "BRGW (3124)": (3,1,2,4)
        }
        c0, c1, c2, c3 = matrix_map.get(color_choice, (1,2,3,4))
        
        payload = struct.pack("<16sBBBBBBBHHBBBBB", MAGIC_HEADER, 
                              ip_parts, ip_parts, ip_parts, ip_parts, 
                              sub_parts, sub_parts, sub_parts, sub_parts, 
                              new_uni, strip_type, c0, c1, c2, c3)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(payload, (current_node_ip, TPD_CONFIG_PORT))
        sock.close()
        messagebox.showinfo("Success", f"Configuration transmitted successfully to {current_node_ip}. Node is rebooting.")
        self.discover_fleet()

if __name__ == "__main__":
    root = tk.Tk()
    app = TPDNetManager(root)
    root.mainloop()
