# ============================================================================
# TPD FLAGGED NETWORK UTILITY (v1.3 - Atari 2600 Racing Stripe Edition)
# PART 1 OF 2
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
        self.root.title("TPD Professional Node Fleet Utility v1.3")
        self.root.geometry("860x640") # Widened explicitly to prevent heading clipping
        self.root.minsize(800, 580)
        self.discovered_nodes = {}
        
        # Apply Master Retro Atari Palette Schemes Globally
        self.bg_dark      = "#1A1A1A"  # Console Body Charcoal
        self.fg_cream     = "#E6DFD3"  # Dashboard Faux-Beige Text
        self.stripe_red   = "#C83A22"  # Atari Racing Stripe Red-Orange
        self.stripe_yell  = "#EAA135"  # Atari Racing Stripe Sunset Yellow
        self.stripe_tan   = "#D6B88D"  # Atari Racing Stripe Light Tan
        self.btn_bg       = "#2D2D2D"  # Control Toggle Gray
        
        self.root.configure(bg=self.bg_dark)
        self.setup_retro_styles()
        self.create_widgets()
        
    def setup_retro_styles(self):
        style = ttk.Style()
        style.theme_use("default")
        
        # Base Label Frames Styling
        style.configure("TLabelframe", background=self.bg_dark, foreground=self.fg_cream, bordercolor=self.stripe_tan, thickness=1)
        style.configure("TLabelframe.Label", background=self.bg_dark, foreground=self.stripe_yell, font=("Courier", 11, "bold"))
        
        # Labels and Basic Assets
        style.configure("TLabel", background=self.bg_dark, foreground=self.fg_cream, font=("Courier", 10, "bold"))
        
        # Dropdowns and Entries Configurations
        style.configure("TCombobox", fieldbackground=self.btn_bg, background=self.bg_dark, foreground=self.fg_cream, arrowcolor=self.stripe_yell)
        
        # Table Sheet Element Layout Overrides
        style.configure("Treeview", background=self.btn_bg, fieldbackground=self.btn_bg, foreground=self.fg_cream, rowheight=24, font=("Courier", 10))
        style.configure("Treeview.Heading", background=self.bg_dark, foreground=self.stripe_tan, font=("Courier", 10, "bold"), relief="flat")
        style.map("Treeview.Heading", background=[('active', self.btn_bg)])
        
        # Custom Action Buttons
        style.configure("Atari.TButton", background=self.btn_bg, foreground=self.stripe_yell, font=("Courier", 11, "bold"), relief="raised", bordercolor=self.stripe_red)
        style.map("Atari.TButton", background=[('active', self.stripe_red)], foreground=[('active', self.bg_dark)])

    def create_widgets(self):
        # Top toolbar frame
        btn_frame = ttk.Frame(self.root, padding=10)
        btn_frame.pack(fill=tk.X)
        btn_frame.configure(style="TLabel")
        
        ttk.Button(btn_frame, text="Scan Network Infrastructure", command=self.discover_fleet, style="Atari.TButton").pack(side=tk.LEFT, padx=5)
        
        # Decorative Atari Racing Stripes Accent Bar Block Layout
        stripe_canvas = tk.Canvas(self.root, height=6, bg=self.bg_dark, highlightthickness=0)
        stripe_canvas.pack(fill=tk.X, pady=5)
        stripe_canvas.create_rectangle(0, 0, 2000, 2, fill=self.stripe_red, outline="")
        stripe_canvas.create_rectangle(0, 2, 2000, 4, fill=self.stripe_yell, outline="")
        stripe_canvas.create_rectangle(0, 4, 2000, 6, fill=self.stripe_tan, outline="")
        
        # Node display sheet layout table - Widened sizes to guarantee zero layout truncation
        self.tree = ttk.Treeview(self.root, columns=("IP", "Subnet", "Type", "P1_Uni", "P2_Uni", "ColorOrder"), show="headings")
        self.tree.heading("IP", text="Node IP Address")
        self.tree.heading("Subnet", text="Subnet Mask")
        self.tree.heading("Type", text="Protocol")
        self.tree.heading("P1_Uni", text="Port 1 Universe")
        self.tree.heading("P2_Uni", text="Port 2 Universe")
        self.tree.heading("ColorOrder", text="Color Order Map")
        
        self.tree.column("IP", width=140, anchor=tk.CENTER)
        self.tree.column("Subnet", width=140, anchor=tk.CENTER)
        self.tree.column("Type", width=100, anchor=tk.CENTER)
        self.tree.column("P1_Uni", width=130, anchor=tk.CENTER)
        self.tree.column("P2_Uni", width=130, anchor=tk.CENTER)
        self.tree.column("ColorOrder", width=150, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Parameter Editor Workspace Form
        edit_frame = ttk.LabelFrame(self.root, text=" Target Node Parameters Editor ", padding=15)
        edit_frame.pack(fill=tk.BOTH, expand=False, padx=15, pady=15)
        
        edit_frame.columnconfigure(1, weight=1, minsize=160)
        edit_frame.columnconfigure(3, weight=1, minsize=160)
        
        # Row 0: Network Base Coordinates
        ttk.Label(edit_frame, text="Target IP Address:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=8)
        self.ent_ip = ttk.Entry(edit_frame)
        self.ent_ip.insert(0, "10.101.1.50")
        self.ent_ip.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=8)
        
        ttk.Label(edit_frame, text="Target Subnet Mask:").grid(row=0, column=2, sticky=tk.W, padx=20, pady=8)
        self.ent_sub = ttk.Entry(edit_frame)
        self.ent_sub.insert(0, "255.255.255.0")
        self.ent_sub.grid(row=0, column=3, sticky=tk.EW, padx=5, pady=8)
        
        # Row 1: Port 1 and Port 2 Starting Universe assignment inputs
        ttk.Label(edit_frame, text="Port 1 Start Universe:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=8)
        self.ent_uni = ttk.Entry(edit_frame)
        self.ent_uni.insert(0, "1")
        self.ent_uni.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=8)
        
        ttk.Label(edit_frame, text="Port 2 Start Universe:").grid(row=1, column=2, sticky=tk.W, padx=20, pady=8)
        self.ent_uni2 = ttk.Entry(edit_frame)
        self.ent_uni2.insert(0, "9")
        self.ent_uni2.grid(row=1, column=3, sticky=tk.EW, padx=5, pady=8)
        
        # Row 2: Dynamic Protocol Selection Matrix Dropdown (EVERY COMBINATION MATRICES ADDED)
        ttk.Label(edit_frame, text="Dynamic Pixel Mapping:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=8)
        self.combo_color = ttk.Combobox(edit_frame, state="readonly", values=[
            "RGBW (1234)", "GRBW (2134)", "BRGW (3124)", "WRGB (4123)",
            "RGB (123)", "GRB (213)", "BRG (312)", "RBG (132)",
            "RGBW-W2 (12345)", "RGBAW (12354)"
        ])
        self.combo_color.set("RGBW (1234)")
        self.combo_color.grid(row=2, column=1, columnspan=3, sticky=tk.EW, padx=5, pady=8)
        
        # Row 3: Submission Action Trigger Bar
        btn_submit = ttk.Button(edit_frame, text="Transmit Configuration to Node", command=self.push_config, style="Atari.TButton")
        btn_submit.grid(row=3, column=0, columnspan=4, sticky=tk.EW, pady=15)
# ============================================================================
# TPD FLAGGED NETWORK UTILITY (v1.3 - Atari 2600 Racing Stripe Edition)
# PART 2 OF 2
# ============================================================================
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
                    # Unpack 33 bytes layout: header(16), ip(4), sub(4), p1_uni(2), p2_uni(2), type(1), colormap(4)
                    header, ip0, ip1, ip2, ip3, sub0, sub1, sub2, sub3, p1_uni, p2_uni, strip_t, c0, c1, c2, c3 = struct.unpack("<16sBBBBBBBHHHBBBBB", data[:33])
                    
                    ip_str = f"{ip0}.{ip1}.{ip2}.{ip3}"
                    sub_str = f"{sub0}.{sub1}.{sub2}.{sub3}"
                    color_str = f"{c0}.{c1}.{c2}.{c3}"
                    
                    if strip_t == 0:     type_str = "4-Ch RGBW"
                    elif strip_t == 1:   type_str = "3-Ch RGB"
                    else:                type_str = "5-Ch Penta"
                    
                    self.tree.insert("", tk.END, values=(ip_str, sub_str, type_str, p1_uni, p2_uni, color_str))
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
        new_uni2 = int(self.ent_uni2.get())
        color_choice = self.combo_color.get()
        
        if "RGBW-W2" in color_choice or "RGBAW" in color_choice: strip_type = 2
        elif "RGB (" in color_choice or "GRB (" in color_choice or "BRG (" in color_choice or "RBG (" in color_choice: strip_type = 1
        else: strip_type = 0
        
        matrix_map = {
            "RGBW (1234)": (1,2,3,4), "GRBW (2134)": (2,1,3,4), "BRGW (3124)": (3,1,2,4), "WRGB (4123)": (4,1,2,3),
            "RGB (123)":   (1,2,3,1), "GRB (213)":   (2,1,3,1), "BRG (312)":   (3,1,2,1), "RBG (132)":   (1,3,2,1),
            "RGBW-W2 (12345)": (1,2,3,4), "RGBAW (12354)": (1,2,3,5)
        }
        c0, c1, c2, c3 = matrix_map.get(color_choice, (1,2,3,4))
        
        payload = struct.pack("<16sBBBBBBBHHHBBBBB", MAGIC_HEADER, 
                              ip_parts[0], ip_parts[1], ip_parts[2], ip_parts[3], 
                              sub_parts[0], sub_parts[1], sub_parts[2], sub_parts[3], 
                              new_uni, new_uni2, strip_type, c0, c1, c2, c3)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(payload, (current_node_ip, TPD_CONFIG_PORT))
        sock.close()
        messagebox.showinfo("Success", f"Configuration transmitted successfully to {current_node_ip}. Node is rebooting.")
        self.discover_fleet()

if __name__ == "__main__":
    root = tk.Tk()
    app = TPDNetManager(root)
    root.mainloop()
