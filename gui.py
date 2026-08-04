import tkinter as tk


class QA_GUI:

    def __init__(self):
        self.window = tk.Tk()

        self.window.title("QA Automation Framework")
        self.window.geometry("400x200")

        self.label = tk.Label(self.window,text="Webseite testen:")
        self.label.pack(pady=10)

        self.url_entry = tk.Entry(self.window,width=40)
        self.url_entry.pack()

        self.button = tk.Button(self.window,text="Test starten",command=self.button_clicked)
        self.button.pack(pady=20)

    def button_clicked(self):
        url = self.url_entry.get()
        print("Button clicked")
        print("Teste URL:", url)


    def start(self):
        self.window.mainloop()

