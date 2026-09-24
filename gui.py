import tkinter as tk
from tkinter import messagebox
from url_manager import load_urls, save_url, delete_url
from test_runner import run_test, export_pdf_with_playwright
import webbrowser                           #ermöglicht das Öffnen von Webseiten und HTML-Dateien im Standardbrowser
import os

class QA_GUI:

    def __init__(self):
        self.window = tk.Tk()

        self.window.title("QA Automation Framework")
        self.window.geometry("400x670")

        #titel
        title_label = tk.Label(self.window,text="QA Automation Framework",font=("Arial", 18, "bold"))
        title_label.pack(pady=(20, 5))

        subtitle_label = tk.Label(self.window,text="Website Quality Assurance",font=("Arial", 10))
        subtitle_label.pack(pady=(0, 20))

        #webseite testen
        test_frame = tk.LabelFrame(self.window,text="Webseite testen",padx=15,pady=15)                  #tk.LabelFrame = erstellt einen Rahmen mit Beschriftung mit self.window wird es direkt im hauptfenster erzeugt
        test_frame.pack(fill="x", padx=20, pady=10)                                                     # fill x = Rahmen wird über die verfügbare Breite gezogen

        self.url_entry = tk.Entry(test_frame, width=50)
        self.url_entry.pack(pady=5)

        self.button = tk.Button(test_frame,text="Test starten",command=self.button_clicked,width=20)
        self.button.pack(pady=10)

        #bericht
        report_frame = tk.LabelFrame(self.window,text="Bericht",padx=15,pady=15)
        report_frame.pack(fill="x", padx=20, pady=10)

        self.report_button = tk.Button(report_frame,text="Report anzeigen",command=self.open_report,width=18)
        self.report_button.pack(side="left", padx=5)

        self.pdf_button = tk.Button(report_frame,text="PDF exportieren",command=self.export_pdf,width=18)
        self.pdf_button.pack(side="left", padx=5)

        self.window.bind("<Return>", lambda event: self.button_clicked())

        #gespeicherte URLS
        url_frame = tk.LabelFrame(self.window,text="Gespeicherte URLs",padx=15,pady=15)
        url_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.save_button = tk.Button(url_frame,text="URL speichern",command=self.save_url,width=18)
        self.save_button.pack(pady=5)

        self.url_button = tk.Button(url_frame,text="URLs laden",command=self.load_saved_urls,width=18)
        self.url_button.pack(pady=5)

        self.url_listbox = tk.Listbox(url_frame,width=50,height=5)
        self.url_listbox.pack(pady=10, fill="x")

        self.url_listbox.bind("<Return>",lambda event: self.load_selected_url())

        self.delete_button = tk.Button(url_frame,text="URL löschen",command=self.delete_selected_url,width=18)
        self.delete_button.pack(pady=5)

        self.load_button = tk.Button(url_frame,text="URL auswählen",command=self.load_selected_url,width=18)
        self.load_button.pack(pady=5)

    def open_report(self):
        webbrowser.open("qa_test_report.html")

    def button_clicked(self):
        content_window = tk.Toplevel()
        content_window.title("Content Check")
        content_window.geometry("400x250")

        tk.Label(content_window, text="Erwarteter Titel:", font=("Arial", 10)).pack(pady=5)
        expected_title_entry = tk.Entry(content_window, font=("Arial", 14))
        expected_title_entry.pack(pady=5)

        tk.Label(content_window, text="Erwarteter Text:", font=("Arial", 10)).pack(pady=5)
        expected_text_entry = tk.Entry(content_window, font=("Arial", 14))
        expected_text_entry.pack(pady=5)

        tk.Button(content_window,text="Test starten",command=lambda: self.button_start(content_window, expected_title_entry.get(), expected_text_entry.get())).pack(pady=5)     #Maus
        content_window.bind("<Return>", lambda event: self.button_start(content_window,expected_title_entry.get(),expected_text_entry.get()))                                   #Entertaste

    def button_start(self, content_window, expected_title, expected_text):
        url = self.url_entry.get()
        content_window.destroy()
        run_test(url, expected_title, expected_text)

    def load_saved_urls(self):
        self.url_listbox.delete(0, tk.END)

        urls = load_urls()

        for url in urls:
            self.url_listbox.insert(tk.END,url)

    def delete_selected_url(self):
        selection = self.url_listbox.curselection()

        if selection:
            url = self.url_listbox.get(selection[0])
            delete_url(url)
            self.load_saved_urls()

        else:
            print("Keine URL ausgewählt")
            messagebox.showwarning("Warnung", "Keine URL ausgewählt")


    def save_url(self):
        url = self.url_entry.get()

        if url:
            save_url(url)
            self.url_entry.delete(0, tk.END)

        else:
            print("Keine URL eingegeben")
            messagebox.showwarning("Warnung", "Keine URL eingegeben")

    def load_selected_url(self):
        selection = self.url_listbox.curselection()

        if selection:
            selected_url = self.url_listbox.get(selection[0])
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, selected_url)

        else:
            print("Keine URL ausgewählt")
            messagebox.showwarning("Warnung", "Keine URL ausgewählt")

    def start(self):
        self.window.mainloop()

    def export_pdf(self):
        downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        pdf_file = os.path.join(downloads, "qa_test_report.pdf")

        export_pdf_with_playwright("qa_test_report.html",pdf_file)

