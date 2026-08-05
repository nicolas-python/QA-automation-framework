import tkinter as tk
from url_manager import load_urls, save_url, delete_url

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
        self.button.pack(pady=20)

        self.save_button = tk.Button(self.window,text="URL speichern",command=self.save_url)
        self.save_button.pack(pady=10)

        self.delete_button = tk.Button(self.window,text="URL löschen",command=self.delete_selected_url)
        self.delete_button.pack(pady=10)

        self.url_listbox = tk.Listbox(self.window, width=50, height=5)
        self.url_listbox.pack(pady=10)

        self.url_button = tk.Button(self.window,text="Gespeicherte URLs laden",command=self.load_saved_urls)
        self.url_button.pack(pady=10)

        self.load_button = tk.Button(self.window,text="URLs laden",command=self.select_url)
        self.load_button.pack()

    def button_clicked(self):
        url = self.url_entry.get()
        print("Button clicked")
        print("Teste URL:", url)

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
            print("URL gelöscht:", url)

        else:
            print("Keine URL ausgewählt")

    def save_url(self):
        url = self.url_entry.get()

        if url:
            save_url(url)
            print("URL gespeichert:", url)
            self.url_entry.delete(0, tk.END)

        else:
            print("Keine URL eingegeben")

    def select_url(self):
        selection = self.url_listbox.curselection()

        if selection:
            selected_url = self.url_listbox.get(selection[0])
            print("Ausgewählte URL:", selected_url)

        else:
            print("Keine URL ausgewählt")

    def start(self):
        self.window.mainloop()

