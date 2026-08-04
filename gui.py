import tkinter as tk


def start_gui():
    window = tk.Tk()

    window.title("QA Automation Framework")
    window.geometry("400x200")

    label = tk.Label(window,text="Webseite testen:")
    label.pack(pady=10)

    url_entry = tk.Entry(window,width=40)
    url_entry.pack()

    button = tk.Button(window,text="Test starten")
    print("Button clicked")
    button.pack(pady=20)

    window.mainloop()

start_gui()