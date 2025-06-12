import tkinter as tk
import requests
from bs4 import BeautifulSoup
import os
import re

class WebReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("E-Book Style Web Reader")

        # Theme variables
        self.theme = "light"
        self.bg_colors = {"light": "white", "dark": "#2E2E2E", "sepia": "#F4E1C1"}
        self.fg_colors = {"light": "black", "dark": "white", "sepia": "#5C4033"}

        # Page tracking variables
        self.text_content = ""
        self.font_size = 14

        # Top Control Panel (Horizontal Layout)
        top_frame = tk.Frame(root)
        top_frame.pack(pady=10, fill="x")

        # Entry for URL
        self.url_entry = tk.Entry(top_frame, width=50)
        self.url_entry.grid(row=0, column=0, padx=5)
        self.url_entry.bind("<Return>", self.load_page)  # Bind Enter key

        # Load Button
        self.load_button = tk.Button(top_frame, text="Load", command=self.load_page)
        self.load_button.grid(row=0, column=1, padx=5)

        # Font Size Buttons
        self.increase_button = tk.Button(top_frame, text="A+", command=self.increase_font)
        self.increase_button.grid(row=0, column=2, padx=5)
        self.decrease_button = tk.Button(top_frame, text="A-", command=self.decrease_font)
        self.decrease_button.grid(row=0, column=3, padx=5)

        # Theme Toggle Button
        self.theme_button = tk.Button(top_frame, text="Theme", command=self.toggle_theme, bg="gray", fg="white")
        self.theme_button.grid(row=0, column=4, padx=5)

        # Frame for text and scrollbar
        frame = tk.Frame(root)
        frame.pack(pady=10, fill="both", expand=True)

        # Scrollbar
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        # Text Display (Justified text)
        self.text_display = tk.Text(frame, wrap="word", font=("Arial", self.font_size), height=20, width=60, yscrollcommand=scrollbar.set)
        self.text_display.pack(fill="both", expand=True)
        scrollbar.config(command=self.text_display.yview)

        # Navigation Buttons (Horizontal Row Below Text)
        nav_frame = tk.Frame(root)
        nav_frame.pack(fill="x")

        self.left_button = tk.Button(nav_frame, text="← Previous Page", command=self.prev_page)
        self.left_button.pack(side="left", padx=20, pady=5)
        self.right_button = tk.Button(nav_frame, text="Next Page →", command=self.next_page)
        self.right_button.pack(side="right", padx=20, pady=5)

        # Keyboard bindings for left/right arrows
        self.root.bind("<Left>", lambda event: self.prev_page())
        self.root.bind("<Right>", lambda event: self.next_page())

        # Load last visited page if available
        self.load_last_page()

        # Set default theme
        self.apply_theme()

    def load_page(self, event=None):
        """Loads the webpage into the reader."""
        url = self.url_entry.get()
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract and clean text content (removing extra new lines)
            raw_text = "\n".join([line.strip() for line in soup.get_text().split("\n") if line.strip()])
            self.text_content = self.make_urls_clickable(raw_text)

            # Save last visited page
            with open("last_url.txt", "w") as file:
                file.write(url)

            self.text_display.delete("1.0", tk.END)
            self.text_display.insert(tk.END, self.text_content)

            # Apply formatting (justify text)
            self.apply_text_format()

        except Exception as e:
            self.text_display.delete("1.0", tk.END)
            self.text_display.insert(tk.END, f"Error: {e}")

    def make_urls_clickable(self, text):
        """Identifies URLs and binds them to load in-app instead of a browser."""
        url_pattern = re.compile(r"https?://\S+")
        matches = url_pattern.findall(text)

        for url in matches:
            text = text.replace(url, f"{url}")

        return text

    def apply_text_format(self):
        """Formats text with justified alignment and makes URLs clickable."""
        self.text_display.tag_configure("justify", justify="left")
        self.text_display.tag_add("justify", "1.0", tk.END)

        # Bind URLs to load inside the app
        url_pattern = re.compile(r"https?://\S+")
        matches = url_pattern.findall(self.text_content)

        for url in matches:
            start_idx = self.text_display.search(url, "1.0", stopindex=tk.END)
            if start_idx:
                end_idx = f"{start_idx} + {len(url)}c"
                self.text_display.tag_add(url, start_idx, end_idx)
                self.text_display.tag_config(url, foreground="blue", underline=True)
                self.text_display.tag_bind(url, "<Button-1>", lambda event, u=url: self.load_new_page(u))

    def load_new_page(self, url):
        """Loads a new page inside the reader when a link is clicked."""
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, url)
        self.load_page()

    def load_last_page(self):
        """Loads last visited webpage."""
        if os.path.exists("last_url.txt"):
            with open("last_url.txt", "r") as file:
                last_url = file.read().strip()
                self.url_entry.insert(0, last_url)
                self.load_page()

    def prev_page(self):
        """Scrolls up by one screenful."""
        self.text_display.yview_scroll(-1, "pages")

    def next_page(self):
        """Scrolls down by one screenful."""
        self.text_display.yview_scroll(1, "pages")

    def increase_font(self):
        """Increases font size dynamically."""
        self.font_size += 2
        self.text_display.configure(font=("Arial", self.font_size))

    def decrease_font(self):
        """Decreases font size dynamically."""
        self.font_size -= 2
        self.text_display.configure(font=("Arial", self.font_size))

    def toggle_theme(self):
        """Cycles through light, dark, and sepia themes."""
        theme_options = ["light", "sepia", "dark"]
        current_index = theme_options.index(self.theme)
        self.theme = theme_options[(current_index + 1) % len(theme_options)]
        self.apply_theme()

    def apply_theme(self):
        """Applies selected theme to background and text colors."""
        bg_color = self.bg_colors[self.theme]
        fg_color = self.fg_colors[self.theme]
        
        self.root.config(bg=bg_color)
        self.text_display.config(bg=bg_color, fg=fg_color)
        self.theme_button.config(bg="gray", fg="white")
        self.left_button.config(bg=bg_color, fg=fg_color)
        self.right_button.config(bg=bg_color, fg=fg_color)

# Run the App
if __name__ == "__main__":
    root = tk.Tk()
    app = WebReaderApp(root)
    root.mainloop()
