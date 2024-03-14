import tkinter as tk
from tkinter import font, filedialog
import customtkinter as ctk
import threading
from tkinter import font
import sys
from scraper.maimai_auto_main import MaiMaiScraper
import pandas as pd

class ConsoleDirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.insert(tk.END, message)

class MainGUI:
     def __init__(self):
        self.maimai_scraper = None
        self.maimai_scraper_thread = None

        self.submitted_url_default = "Paste the MaiMai URL here"
        self.submitted_excel_default = "Paste the path to the destination folder of the Excel file"
        self.submitted_url = ""
        self.submitted_excel = ""
        self.root = ctk.CTk()
        self.root.title("MaiMai Auto Scraper")
        self.root.geometry("850x700")
        self.root._set_appearance_mode("dark")

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # URL input
        self.url_label = ctk.CTkLabel(self.root, text="URL:")
        self.url_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.url_entry = ctk.CTkEntry(self.root, width=600)
        self.url_entry.insert(ctk.END, self.submitted_url_default)
        self.url_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.url_entry.bind('<FocusIn>', self.on_entry_click)

        # Start button
        self.start_button = ctk.CTkButton(self.root, text="Start", command=self.submit_input)
        self.start_button.grid(row=2, column=0, padx=10, pady=10)

        # Stop button
        self.stop_button = ctk.CTkButton(self.root, text="Stop", command=self.stop_run)
        self.stop_button.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        self.stop_button.configure(state=ctk.DISABLED)

        # Text box to show information
        self.text_box = ctk.CTkTextbox(self.root)
        self.text_box.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Redirect print to text box
        sys.stdout = ConsoleDirector(self.text_box)
        sys.stderr = ConsoleDirector(self.text_box)

     def process_url(self, url):
        self.start_button.configure(state=ctk.DISABLED)
        self.stop_button.configure(state=ctk.NORMAL)
        self.maimai_scraper = MaiMaiScraper(filter_page=url)
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
        if event.widget.get() in [self.submitted_url_default, self.submitted_excel_default]:
            event.widget.delete(0, tk.END)
            event.widget.config(fg='black')

     def submit_input(self):
        self.submitted_url = self.url_entry.get()

        if self.submitted_url != self.submitted_url_default and self.submitted_url != "":
            self.process_url(self.submitted_url)
        else:
            print("Please input a URL")

     def stop_run(self):
        try:
            close_scraper_thread = threading.Thread(target=lambda: self.maimai_scraper.driver.quit())
            close_scraper_thread.start()
        finally:
            self.stop_button.config(state=tk.DISABLED)
            self.start_button.config(state=tk.NORMAL)
            print("Stop Running")
    

if __name__ == "__main__":
    gui = MainGUI()
    gui.root.mainloop()
