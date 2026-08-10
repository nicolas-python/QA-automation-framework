import tkinter as tk
from url_manager import load_urls, save_url, delete_url
from test_runner import run_test

class QA_GUI:

    def __init__(self):
        self.window = tk.Tk()

        self.window.title("QA Automation Framework")
        self.window.geometry("400x350")

        self.label = tk.Label(self.window,text="Webseite testen:")
        self.label.pack(pady=10)

        self.url_entry = tk.Entry(self.window,width=40)
        self.url_entry.pack()

        self.button = tk.Button(self.window,text="Test starten",command=self.button_clicked)
        self.button.pack(pady=10)

        self.save_button = tk.Button(self.window,text="URL speichern",command=self.save_url)
        self.save_button.pack(padx=10)

        self.url_button = tk.Button(self.window, text="Gespeicherte URLs laden", command=self.load_saved_urls)
        self.url_button.pack(pady=10)

        self.url_listbox = tk.Listbox(self.window, width=50, height=5)
        self.url_listbox.pack(pady=10)

        self.delete_button = tk.Button(self.window,text="URL löschen",command=self.delete_selected_url)
        self.delete_button.pack(padx=10)

        self.load_button = tk.Button(self.window,text="URLs laden",command=self.load_selected_url)
        self.load_button.pack()

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

        tk.Button(content_window,text="Test starten",command=lambda: self.button_start(content_window, expected_title_entry.get(), expected_text_entry.get())).pack(pady=5)

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

    def save_url(self):
        url = self.url_entry.get()

        if url:
            save_url(url)
            self.url_entry.delete(0, tk.END)

        else:
            print("Keine URL eingegeben")

    def load_selected_url(self):
        selection = self.url_listbox.curselection()

        if selection:
            selected_url = self.url_listbox.get(selection[0])
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, selected_url)

        else:
            print("Keine URL ausgewählt")

    def start(self):
        self.window.mainloop()

