# instead of a react app, creat python gui to access my fastapi endpoints

import tkinter as tk
from tkinter import ttk
import requests
import json
from typing import Optional
import pickle

class AutocompleteEntry(ttk.Entry):
    def __init__(self, autocomplete_list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.autocomplete_list = autocomplete_list
        self.var = self["textvariable"] = tk.StringVar()
        self.var.trace("w", self.changed)
        self.bind("<Right>", self.selection)
        self.bind("<Down>", self.move_down)
        self.lb_up = False

    def changed(self, name, index, mode):
        if self.var.get() == '':
            if self.lb_up:
                self.lb.destroy()
                self.lb_up = False
        else:
            words = self.comparison()
            if words:
                if not self.lb_up:
                    self.lb = tk.Listbox()
                    self.lb.bind("<Double-Button-1>", self.selection)
                    self.lb.bind("<Right>", self.selection)
                    self.lb.place(x=self.winfo_x(), y=self.winfo_y() + self.winfo_height())
                    self.lb_up = True
                self.lb.delete(0, tk.END)
                for w in words:
                    self.lb.insert(tk.END, w)
            else:
                if self.lb_up:
                    self.lb.destroy()
                    self.lb_up = False

    def selection(self, event):
        if self.lb_up:
            self.var.set(self.lb.get(tk.ACTIVE))
            self.lb.destroy()
            self.lb_up = False
            self.icursor(tk.END)

    def move_down(self, event):
        if self.lb_up:
            self.lb.focus()
            self.lb.selection_set(0)

    def comparison(self):
        pattern = self.var.get().lower()
        return [w for w in self.autocomplete_list if pattern in w.lower()]

class OrderLadderTable(tk.Frame):
    def __init__(self, master, columns, cell_width=120, cell_height=24, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.columns = columns
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.canvas = tk.Canvas(self, borderwidth=0, background="#ffffff", height=20*cell_height)
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.table_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0,0), window=self.table_frame, anchor="nw")
        self.table_frame.bind("<Configure>", self.on_frame_configure)
        self.rows = []

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def clear(self):
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        self.rows = []

    def insert_row(self, values, cell_bg_colors=None):
        row_widgets = []
        for col, value in enumerate(values):
            bg = cell_bg_colors[col] if cell_bg_colors and col < len(cell_bg_colors) else "white"
            label = tk.Label(
                self.table_frame,
                text=value,
                width=int(self.cell_width/8),
                height=1,
                borderwidth=0,  # Less bold border
                relief="flat",  # Less bold border
                bg=bg,
                anchor="center",
                padx=4,  # Add a little padding for a cleaner look
                pady=2
            )
            label.grid(row=len(self.rows), column=col, sticky="nsew", padx=1, pady=1)
            row_widgets.append(label)
        self.rows.append(row_widgets)

    def set_headers(self):
        for col, col_name in enumerate(self.columns):
            label = tk.Label(self.table_frame, text=col_name, width=int(self.cell_width/8), height=1,
                             borderwidth=0, relief="flat", bg="#e0e0e0", anchor="center", font=("Arial", 10, "bold"), padx=4, pady=2)
            label.grid(row=0, column=col, sticky="nsew", padx=1, pady=1)

class MarketDataGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SMP Market Making Terminal")
        self.root.geometry("600x900")

        # be sure to start fastapi server before running this
        self.base_url = "http://localhost:8000"
        
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        self.item_names = self.load_item_names()
        self.create_input_fields()
        self.create_output_display()
        self.create_buttons()
        self.configure_grid()
    
    def create_input_fields(self):
        ttk.Label(self.main_frame, text="Market Hash Name:").grid(row=0, column=0, sticky=tk.W)
        self.market_hash_name = AutocompleteEntry(self.item_names, self.main_frame, width=40)
        self.market_hash_name.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Item ID input
        ttk.Label(self.main_frame, text="Item ID (optional):").grid(row=1, column=0, sticky=tk.W)
        self.item_id = ttk.Entry(self.main_frame, width=40)
        self.item_id.grid(row=1, column=1, sticky=(tk.W, tk.E))
    
    def create_output_display(self):
        # Text output for general results
        self.output_text = tk.Text(self.main_frame, wrap=tk.WORD, height=20, width=80)
        self.output_text.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.output_text.yview)
        scrollbar.grid(row=2, column=2, sticky=(tk.N, tk.S))
        self.output_text['yscrollcommand'] = scrollbar.set

        # Custom order ladder table (hidden by default)
        columns = ("level", "bid_quantity", "price", "fair_value", "ask_quantity")
        self.order_ladder_table = OrderLadderTable(self.main_frame, columns)
        self.order_ladder_table.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.order_ladder_table.grid_remove()  # Hide by default
    
    def create_buttons(self):
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="Get Price Overview", 
                  command=self.get_price_overview).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Start Streaming Order Ladder", 
                  command=self.get_order_ladder).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Get Featured Items", 
                  command=self.get_featured_items).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Get All Items", 
                  command=self.get_all_items).pack(side=tk.LEFT, padx=5)
    
    def configure_grid(self):
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(2, weight=1)
    
    def display_result(self, result):
        self.order_ladder_table.grid_remove()
        self.output_text.grid()
        self.output_text.delete(1.0, tk.END)
        if isinstance(result, dict):
            formatted_result = json.dumps(result, indent=2)
        else:
            formatted_result = str(result)
        self.output_text.insert(tk.END, formatted_result)
    
    def get_price_overview(self):
        """Get price overview for the entered market hash name"""
        market_hash_name = self.market_hash_name.get()
        if not market_hash_name:
            self.display_result("Please enter a market hash name")
            return
        
        try:
            response = requests.get(f"{self.base_url}/priceoverview/{market_hash_name}")
            response.raise_for_status()
            self.display_result(response.json())
        except Exception as e:
            self.display_result(f"Error: {str(e)}")
    
    def get_order_ladder(self):
        """Get order ladder for the entered market hash name"""
        market_hash_name = self.market_hash_name.get()
        if not market_hash_name:
            self.display_result("Please enter a market hash name")
            return
        try:
            response = requests.get(f"{self.base_url}/orderladder/{market_hash_name}?levels=20")
            response.raise_for_status()
            self.display_order_ladder_table(response.text)
        except Exception as e:
            self.display_result(f"Error: {str(e)}")
    
    def get_featured_items(self):
        """Get featured items"""
        try:
            response = requests.get(f"{self.base_url}/buff/featured")
            response.raise_for_status()
            self.display_result(response.json())
        except Exception as e:
            self.display_result(f"Error: {str(e)}")
    
    def get_all_items(self):
        """Get all items"""
        try:
            response = requests.get(f"{self.base_url}/items")
            response.raise_for_status()
            self.display_result(response.json())
        except Exception as e:
            self.display_result(f"Error: {str(e)}")

    def display_order_ladder_table(self, df_json):
        self.output_text.grid_remove()
        self.order_ladder_table.grid()
        self.order_ladder_table.clear()
        self.order_ladder_table.set_headers()
        try:
            df = json.loads(df_json)
            columns = df.get('columns', [])
            data = df.get('data', [])
            price_idx = None
            for i, col in enumerate(columns):
                if 'price' in col.lower():
                    price_idx = i
                    break
            if price_idx is None:
                raise Exception('No price column found in order ladder data')
            prices = [row[price_idx] for row in data if row[price_idx] is not None]
            if not prices:
                raise Exception('No prices found in order ladder data')
            mid_price = sum(prices) / len(prices)
            level = 1
            for row in data:
                price = row[price_idx]
                if price is None:
                    continue
                bid_quantity = row[1] if price <= mid_price and len(row) > 1 else ''
                ask_quantity = row[1] if price > mid_price and len(row) > 1 else ''
                fair_value = ''
                cell_bg_colors = ["white"] * 5
                # Only color the correct cell
                if price <= mid_price and bid_quantity != '':
                    cell_bg_colors[1] = "#b6e7a7"  # green for bid_quantity
                if price > mid_price and ask_quantity != '':
                    cell_bg_colors[4] = "#ffcccc"  # red for ask_quantity
                self.order_ladder_table.insert_row(
                    (level, bid_quantity, price, fair_value, ask_quantity),
                    cell_bg_colors=cell_bg_colors
                )
                level += 1
        except Exception as e:
            self.display_result(f"Error displaying order ladder: {str(e)}")

    def load_item_names(self):
        with open("730_ITEMNAMES.txt", "rb") as f:
            return pickle.load(f)

def main():
    root = tk.Tk()
    app = MarketDataGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
