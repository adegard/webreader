import tkinter as tk
import requests
from bs4 import BeautifulSoup
import webbrowser
import os

class WebReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Web Page Reader")

        # Theme variables
        self.dark_mode = False
        self.bg_light = "white"
        self.fg_light = "black"
        self.bg_dark = "#2E2E2E"
        self.fg_dark = "white"

        # Entry for URL
        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.pack(pady=10)
        self.url_entry.bind("<Return>", self.load_page)  # Bind Enter key

        # Load Button
        self.load_button = tk.Button(root, text="Load", command=self.load_page)
        self.load_button.pack(pady=5)

        # Toggle Theme Button (ensuring visibility)
        self.theme_button = tk.Button(root, text="Toggle Dark/Light Mode", command=self.toggle_theme, bg="gray", fg="white")
        self.theme_button.pack(pady=5)

        # Frame for text and scrollbar
        frame = tk.Frame(root)
        frame.pack(pady=10, fill="both", expand=True)

        # Scrollbar
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        # Text Display
        self.text_display = tk.Text(frame, wrap="word", font=("Arial", 12), height=20, width=60, yscrollcommand=scrollbar.set)
        self.text_display.pack(fill="both", expand=True)
        scrollbar.config(command=self.text_display.yview)

        # Links Display
        self.links_display = tk.Listbox(root, height=10, width=80)
        self.links_display.pack(pady=5)
        self.links_display.bind("<Double-Button-1>", self.open_selected_link)

        # Font Size Controls
        self.font_size = 12
        self.increase_button = tk.Button(root, text="Increase Font", command=self.increase_font)
        self.increase_button.pack(pady=5)
        self.decrease_button = tk.Button(root, text="Decrease Font", command=self.decrease_font)
        self.decrease_button.pack(pady=5)

        # Load last visited page if available
        self.load_last_page()

        # Set default theme
        self.apply_theme()

    def load_page(self, event=None):
        url = self.url_entry.get()
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract and clean text content (removing extra new lines)
            text_content = "\n".join([line.strip() for line in soup.get_text().split("\n") if line.strip()])

            # Save last visited page
            with open("last_url.txt", "w") as file:
                file.write(url)

            self.text_display.delete("1.0", tk.END)
            self.text_display.insert(tk.END, text_content)

            # Extract and show links
            self.links_display.delete(0, tk.END)
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if href.startswith("http"):
                    self.links_display.insert(tk.END, href)

        except Exception as e:
            self.text_display.delete("1.0", tk.END)
            self.text_display.insert(tk.END, f"Error: {e}")

    def load_last_page(self):
        if os.path.exists("last_url.txt"):
            with open("last_url.txt", "r") as file:
                last_url = file.read().strip()
                self.url_entry.insert(0, last_url)
                self.load_page()

    def open_selected_link(self, event):
        selected_index = self.links_display.curselection()
        if selected_index:
            selected_url = self.links_display.get(selected_index[0])
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, selected_url)
            self.load_page()

    def increase_font(self):
        self.font_size += 2
        self.text_display.configure(font=("Arial", self.font_size))

    def decrease_font(self):
        self.font_size -= 2
        self.text_display.configure(font=("Arial", self.font_size))

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def apply_theme(self):
        if self.dark_mode:
            self.root.config(bg=self.bg_dark)
            self.text_display.config(bg=self.bg_dark, fg=self.fg_dark)
            self.theme_button.config(bg="gray", fg="white")  # Ensure visibility in dark mode
        else:
            self.root.config(bg=self.bg_light)
            self.text_display.config(bg=self.bg_light, fg=self.fg_light)
            self.theme_button.config(bg="white", fg="black")  # Ensure visibility in light mode

# Run the App
if __name__ == "__main__":
    root = tk.Tk()
    app = WebReaderApp(root)
    root.mainloop()
