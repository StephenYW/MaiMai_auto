import tkinter as tk
from tkinter import font, filedialog
import customtkinter as ctk
import threading
from tkinter import font
import sys
from scraper.maimai_auto_main import MaiMaiScraper
from util.cookies_util import *
import pandas as pd

class ConsoleDirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.insert(ctk.END, message)

class MainGUI:
     def __init__(self):
        self.maimai_scraper = None
        self.maimai_scraper_thread = None

        self.submitted_url_default = "Paste the MaiMai URL here"
        self.submitted_tag_default = "MaiMai"
        self.submitted_max_candidates_default = 100
        #self.submitted_excel_default = "Paste the path to the destination folder of the Excel file"
        self.submitted_url = ""
        #self.submitted_excel = ""
        self.submitted_tag = ""
        self.submitted_max_candidates = ""
        self.cookies_path = ""
        self.root = ctk.CTk()
        self.root.title("MaiMai Auto Scraper")
        self.root.geometry("800x475")
        self.root._set_appearance_mode("system")

        #Cookies Management Button
        self.cookies_button = ctk.CTkButton(self.root, text="Cookies Management", command=self.open_cookies_management)
        self.cookies_button.grid(row=5, column=1, padx=10, pady=10, sticky="se")

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # URL input
        self.url_label = ctk.CTkLabel(self.root, text="URL:")
        self.url_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        self.url_entry = ctk.CTkEntry(self.root, width=600)  
        self.url_entry.insert(ctk.END, self.submitted_url_default)
        self.url_entry.grid(row=0, column=1, padx=20, pady=10, sticky="ew")
        self.url_entry.bind('<FocusIn>', self.on_entry_click)

        # Tag input
        self.tag_label = ctk.CTkLabel(self.root, text="Tag:")
        self.tag_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.tag_entry = ctk.CTkEntry(self.root, width=300)  
        self.tag_entry.insert(ctk.END, self.submitted_tag_default)
        self.tag_entry.grid(row=1, column=1, padx=20, pady=10, sticky="w")
        self.tag_entry.bind('<FocusIn>', self.on_entry_click)

        # Max candidates input
        self.max_candidates_label = ctk.CTkLabel(self.root, text="Max Candidates:")
        self.max_candidates_label.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.max_candidates_entry = ctk.CTkEntry(self.root, width=300)  
        self.max_candidates_entry.insert(ctk.END, self.submitted_max_candidates_default)
        self.max_candidates_entry.grid(row=2, column=1, padx=20, pady=10, sticky="w")
        self.max_candidates_entry.bind('<FocusIn>', self.on_entry_click)


        # Start button
        self.start_button = ctk.CTkButton(self.root, text="Start", command=self.submit_input)
        self.start_button.grid(row=3, column=0, padx=10, pady=10)

        # Stop button
        self.stop_button = ctk.CTkButton(self.root, text="Stop", command=self.stop_run)
        self.stop_button.grid(row=3, column=1, padx=10, pady=10, sticky="w")
        self.stop_button.configure(state=ctk.DISABLED)

        # Text box to show information
        self.text_box = ctk.CTkTextbox(self.root)
        self.text_box.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Redirect print to text box
        sys.stdout = ConsoleDirector(self.text_box)
        sys.stderr = ConsoleDirector(self.text_box)

     def process_url(self, url):
        self.start_button.configure(state=ctk.DISABLED)
        self.stop_button.configure(state=ctk.NORMAL)
        self.maimai_scraper = MaiMaiScraper(filter_page=url, tag=self.submitted_tag, max_candidates=int(self.submitted_max_candidates), cookies_path=self.cookies_path)
        self.maimai_scraper_thread = threading.Thread(target=lambda: self.maimai_scraper.run())
        self.maimai_scraper_thread.start()

     def on_closing(self):
        try:
            self.maimai_scraper.driver.quit()
        except AttributeError:
            pass
        finally:
            self.root.destroy()
        sys.exit(0)

     def on_entry_click(self, event):
        if event.widget.get() in [self.submitted_url_default, self.submitted_tag_default, self.submitted_max_candidates_default]:
            event.widget.delete(0, tk.END)
            event.widget.configure(foreground='black') 

     def submit_input(self):
        self.submitted_url = self.url_entry.get()
        self.submitted_tag = self.tag_entry.get()
        self.submitted_max_candidates = self.max_candidates_entry.get()

        if self.submitted_url != self.submitted_url_default and self.submitted_url != "":
            self.process_url(self.submitted_url)
        else:
            print("Please input a URL")

     def open_cookies_management(self):
        cookies_window = tk.Toplevel(self.root)
        cookies_window.title("Cookies Management")
        cookies_window.geometry("800x400")  # Increased window size

        cookies_window.grab_set()

        # Cookies input text box
        cookies_label = tk.Label(cookies_window, text="Path to your cookies:", font=("Helvetica", 24))
        cookies_label.pack(padx=20, pady=(20, 10), anchor="w")

        cookies_text = tk.Entry(cookies_window, width=70, font=("Helvetica", 24))  # Increased entry width and font size
        cookies_text.pack(padx=20, pady=10, anchor="w", fill="x")

        # Browse button to select cookies file
        def browse_file():
            file_path = filedialog.askopenfilename(title="Select Cookies File", filetypes=[("Pickles", "*.pkl"), ("All files", "*.*")])
            if file_path:
                cookies_text.delete(0, tk.END)
                cookies_text.insert(tk.END, file_path)

        browse_button = tk.Button(cookies_window, text="Browse", command=browse_file, font=("Helvetica", 24))  # Increased button font size
        browse_button.pack(side="left", padx=(20, 10), pady=(0, 20))

        # Load cookies button
        def load_cookies():
            self.process_cookies(cookies_text.get(), cookies_window)

        load_button = tk.Button(cookies_window, text="Load Cookies", command=load_cookies, font=("Helvetica", 24))  # Increased button font size
        load_button.pack(side="left", padx=(0, 20), pady=(0, 20))

        cookies_window.mainloop()

     def process_cookies(self, cookies_path, cookies_window):
        if cookies_path:
            self.cookies_path = cookies_path
            print("Cookies loaded successfully")
        else:
            print("Failed to load cookies")
        cookies_window.destroy()


     def stop_run(self):
        try:
            close_scraper_thread = threading.Thread(target=lambda: self.maimai_scraper.driver.quit())
            close_scraper_thread.start()
        finally:
            self.stop_button.configure(state=ctk.DISABLED)
            self.start_button.configure(state=ctk.NORMAL)
            print("Stop Running")
    

if __name__ == "__main__":
    gui = MainGUI()
    gui.root.mainloop()
