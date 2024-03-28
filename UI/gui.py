import tkinter as tk
from tkinter import font, filedialog
import customtkinter as ctk
import threading
from tkinter import font
import sys
from scraper.maimai_auto_main import MaiMaiScraper
from util.cookies_util import *
import pandas as pd
import os
from PIL import Image

class ConsoleDirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.insert(ctk.END, message)

class MainGUI(ctk.CTk):
     def __init__(self):
        
        super().__init__()

        self.maimai_scraper = None
        self.maimai_scraper_thread = None

        self.submitted_url_default = "Paste the MaiMai URL here"
        self.submitted_tag_default = "MaiMai"
        self.submitted_max_candidates_default = 100
        self.submitted_excel_default = "Paste the path to the destination folder of the Excel file"
        self.submitted_url = ""
        self.submitted_excel = ""
        self.submitted_tag = ""
        self.submitted_max_candidates = ""
        self.cookies_path = ""
        self.title("MaiMai Auto Scraper")
        self.geometry("700x450")
        self._set_appearance_mode("system")

        #Images
        # load images with light and dark mode image
        self.image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_images")
        self.logo_image = ctk.CTkImage(Image.open(os.path.join(self.image_path, "maimai_logo.png")), size=(26, 26))

        self.url_image = ctk.CTkImage(dark_image=Image.open(os.path.join(self.image_path, "url_logo.png")), size=(20, 20))
        self.excel_image = ctk.CTkImage(dark_image=Image.open(os.path.join(self.image_path, "Excel_logo.png")), size=(20, 20))
        self.filter_image = ctk.CTkImage(dark_image=Image.open(os.path.join(self.image_path, "filter_logo.png")), size=(20, 20))

        # create navigation frame
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=5)
        self.navigation_frame.grid(row=0, column=0, rowspan=2, sticky="ns")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.navigation_frame_label = ctk.CTkLabel(self.navigation_frame, text="  MaiMai Auto", image=self.logo_image,
                                                             compound="left", font=ctk.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        # Create constraints frame
        self.constraints_frame = ctk.CTkFrame(self, corner_radius=5)
        self.constraints_frame.grid(row=1, column=1, padx=20, pady=20, sticky="w")
        #self.constraints_frame.grid_columnconfigure(0, weight=1)
        self.constraints_frame.grid_rowconfigure(0, weight=0)
        self.constraints_frame.grid_columnconfigure(0, weight=1)
        self.constraints_frame.grid_columnconfigure(1, weight=1)
        #URL frame
        self.url_frame = ctk.CTkFrame(self, corner_radius=5, fg_color="transparent")
        self.url_frame.grid(row=0, column=1)
        #self.url_frame.grid_columnconfigure(1, weight=1)
        #self.url_frame.grid_columnconfigure(0, weight=1)
        self.url_frame.grid_columnconfigure(1, weight=1)

        # create excel frame
        self.excel_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")

        # create filter frame
        self.filter_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        

        """
        self.line_frame1 = ctk.CTkFrame(self.root, width=780, height=2, fg_color = "black")
        self.line_frame1.place(x=10, y=100)

        self.line_frame2 = ctk.CTkFrame(self.root, width=780, height=2, fg_color = "black")
        self.line_frame2.place(x=10, y=245)
        """

        self.url_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Home",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   image=self.url_image, anchor="w", command=self.url_button_event)
        self.url_button.grid(row=1, column=0, sticky="ew")

        self.excel_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Frame 2",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.excel_image, anchor="w", command=self.excel_button_event)
        self.excel_button.grid(row=2, column=0, sticky="ew")

        self.filter_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Frame 3",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.filter_image, anchor="w", command=self.filter_button_event)
        self.filter_button.grid(row=3, column=0, sticky="ew")

        # select default frame
        self.select_frame_by_name("url")
        
        # Max candidates input
        self.max_candidates_label = ctk.CTkLabel(self.constraints_frame, text="Max Candidates:")
        self.max_candidates_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        self.max_candidates_entry = ctk.CTkEntry(self.constraints_frame, width=300)  
        self.max_candidates_entry.insert(ctk.END, self.submitted_max_candidates_default)
        self.max_candidates_entry.grid(row=0, column=1, padx=20, pady=10, sticky="w")
        self.max_candidates_entry.bind('<FocusIn>', self.on_entry_click)

        # Tag input
        self.tag_label = ctk.CTkLabel(self.constraints_frame, text="File Tag:")
        self.tag_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.tag_entry = ctk.CTkEntry(self.constraints_frame, width=300)  
        self.tag_entry.insert(ctk.END, self.submitted_tag_default)
        self.tag_entry.grid(row=1, column=1, padx=20, pady=10, sticky="w")
        self.tag_entry.bind('<FocusIn>', self.on_entry_click)

        
        # URL input
        self.url_entry = ctk.CTkEntry(self.url_frame, width=480)  
        self.url_entry.insert(ctk.END, self.submitted_url_default)
        self.url_entry.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        self.url_entry.bind('<FocusIn>', self.on_entry_click)

        # Start button
        self.start_button = ctk.CTkButton(self.url_frame, text="Start", command=self.submit_input)
        self.start_button.grid(row=1, column=0, padx=20, pady=10, sticky="w")

        # Stop button
        self.stop_button = ctk.CTkButton(self.url_frame, text="Stop", command=self.stop_run)
        self.stop_button.grid(row=1, column=0, padx=20, pady=10)
        self.stop_button.configure(state=ctk.DISABLED)

        # Text box to show information
        self.text_box = ctk.CTkTextbox(self.url_frame)
        self.text_box.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")

        # Redirect print to text box
        sys.stdout = ConsoleDirector(self.text_box)
        sys.stderr = ConsoleDirector(self.text_box)

        #Cookies Management Button
        self.cookies_button = ctk.CTkButton(self.navigation_frame, text="Cookies Management", command=self.open_cookies_management)
        self.cookies_button.grid(row=6, column=0, padx=20, pady=20, sticky="s")

        
        """
        # Excel file label
        self.excel_label = ctk.CTkLabel(self.root, text="Excel file label input: ")
        self.excel_label.grid(row=5, column=0, padx=20, pady=10, sticky="w")
        
        # Text bar to show user's entry for Excel file path
        self.excel_entry_label = ctk.CTkLabel(self.root, text="Excel File Path:")
        self.excel_entry_label.grid(row=6, column=0, padx=20, pady=10, sticky="w")
        self.excel_entry = ctk.CTkEntry(self.root, width=600)
        self.excel_entry.insert(ctk.END, self.submitted_excel_default)
        self.excel_entry.grid(row=6, column=1, padx=20, pady=10, sticky="ew")
        self.excel_entry.bind('<FocusIn>', self.on_entry_click)
        

        # Browse button to select Excel file
        self.browse_excel_button = ctk.CTkButton(self.root, text="Browse", command=self.browse_excel_file)
        self.browse_excel_button.grid(row=7, column=0, padx=10, pady=10)

        # Start button
        self.start_button_excel = ctk.CTkButton(self.root, text="Start", command=self.submit_input_excel)
        self.start_button_excel.grid(row=8, column=0, padx=10, pady=10)

        # Stop button for Excel
        self.stop_button_excel = ctk.CTkButton(self.root, text="Stop", command=lambda: self.stop_run_excel())
        self.stop_button_excel.grid(row=8, column=1, padx=10, pady=10, sticky="w")
        self.stop_button_excel.configure(state=ctk.DISABLED)
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    """
     def select_frame_by_name(self, name):
        # set button color for selected button
        self.url_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.excel_button.configure(fg_color=("gray75", "gray25") if name == "frame_2" else "transparent")
        self.filter_button.configure(fg_color=("gray75", "gray25") if name == "frame_3" else "transparent")

        # show selected frame
        if name == "url":
            self.url_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.url_frame.grid_forget()
        if name == "excel":
            self.excel_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.excel_frame.grid_forget()
        if name == "filter":
            self.filter_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.filter_frame.grid_forget()

     def url_button_event(self):
        self.select_frame_by_name("url")

     def excel_button_event(self):
        self.select_frame_by_name("excel")

     def filter_button_event(self):
        self.select_frame_by_name("filter")

     
     def process_url(self, url):
        self.start_button.configure(state=ctk.DISABLED)
        self.stop_button.configure(state=ctk.NORMAL)
        self.maimai_scraper = MaiMaiScraper(filter_page=url, tag=self.submitted_tag, max_candidates=int(self.submitted_max_candidates), cookies_path=self.cookies_path)
        self.maimai_scraper_thread = threading.Thread(target=lambda: self.maimai_scraper.run())
        self.maimai_scraper_thread.start()

     def process_excel(self, excel):
        self.start_button_excel.configure(state=ctk.DISABLED)
        self.stop_button_excel.configure(state=ctk.NORMAL)
        self.maimai_scraper = MaiMaiScraper(tag=self.submitted_tag, max_candidates=int(self.submitted_max_candidates), cookies_path=self.cookies_path, excel_path = excel)
        self.maimai_scraper_thread = threading.Thread(target=lambda: self.maimai_scraper.run())
        self.maimai_scraper_thread.start()

    # Browse button to select Excel file
     def browse_excel_file(self):
        file_path = filedialog.askopenfilename(title="Select Excel File", filetypes=[("Excel Files", "*.xlsx;*.xls"), ("All files", "*.*")])
        if file_path:
            self.excel_entry.delete(0, tk.END)
            self.excel_entry.insert(tk.END, file_path)

     def on_closing(self):
        try:
            self.maimai_scraper.driver.quit()
        except AttributeError:
            pass
        finally:
            self.destroy()
        sys.exit(0)

     def on_entry_click(self, event):
        if event.widget.get() in [self.submitted_url_default, self.submitted_tag_default, self.submitted_max_candidates_default, self.submitted_excel_default]:
            event.widget.delete(0, tk.END)
            event.widget.configure(foreground='black') 

     def submit_input(self):

        self.submitted_max_candidates = self.max_candidates_entry.get()
        self.submitted_url = self.url_entry.get()
        self.submitted_tag = self.tag_entry.get()
            
        if self.submitted_url != self.submitted_url_default and self.submitted_url != "":
            self.process_url(self.submitted_url)
        else:
            print("Please input a URL")
        
     def submit_input_excel(self):
         
         self.submitted_excel = self.excel_entry.get()
         self.submitted_max_candidates = self.max_candidates_entry.get()
         self.submitted_tag = self.tag_entry.get()

         if self.submitted_excel != self.submitted_excel_default and self.submitted_excel != "":
            self.process_excel(self.submitted_excel)
         else:
            print("Please input an Excel file path")

     def open_cookies_management(self):
        cookies_window = tk.Toplevel(self)
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
    
     def stop_run_excel(self):
         
        try:
            close_scraper_thread = threading.Thread(target=lambda: self.maimai_scraper.driver.quit())
            close_scraper_thread.start()
        finally:
            self.stop_button_excel.configure(state=ctk.DISABLED)
            self.start_button_excel.configure(state=ctk.NORMAL)
            print("Stop Running")

if __name__ == "__main__":
    gui = MainGUI()
    gui.mainloop()
