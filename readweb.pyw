import tkinter as tk
import requests
from bs4 import BeautifulSoup
import os
import re
import urllib.parse
#import webbrowser

class WebReaderApp:
    """A simple e-book style web reader with navigation, themes, and text formatting."""
    
    def __init__(self, root):
        """Initialize the WebReaderApp with UI elements and theme settings."""
        self.root = root
        self.root.title("E-Book Style Web Reader")

        # Theme settings
        self.theme = "light"
        self.bg_colors = {"light": "white", "dark": "#101524", "sepia": "#F4E1C1"}
        self.fg_colors = {"light": "black", "dark": "#EFDACA", "sepia": "#5C4033"}

        # Text display settings
        self.font_size = 14
        self.text_content = ""

        self.create_ui()

    def create_ui(self):
        """Set up the UI components."""
        # Top Control Panel
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10, fill="x")

        # URL Entry
        self.url_entry = tk.Entry(top_frame, width=50)
        self.url_entry.grid(row=0, column=0, padx=5)
        self.url_entry.bind("<Return>", self.load_page)

        tk.Button(top_frame, text="Load", command=self.load_page).grid(row=0, column=1, padx=5)
        tk.Button(top_frame, text="A+", command=self.increase_font).grid(row=0, column=2, padx=5)
        tk.Button(top_frame, text="A-", command=self.decrease_font).grid(row=0, column=3, padx=5)
        tk.Button(top_frame, text="Theme", command=self.toggle_theme, bg="gray", fg="white").grid(row=0, column=4, padx=5)

        # Text Display Frame
        frame = tk.Frame(self.root)
        frame.pack(pady=10, fill="both", expand=True)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        self.text_display = tk.Text(frame, wrap="word", font=("Arial", self.font_size + 2), height=20, width=60, yscrollcommand=scrollbar.set)
        self.text_display.pack(fill="both", expand=True)
        scrollbar.config(command=self.text_display.yview)

        # Navigation Buttons
        nav_frame = tk.Frame(self.root)
        nav_frame.pack(fill="x")

        tk.Button(nav_frame, text="← Previous Page", command=self.prev_page).pack(side="left", padx=20, pady=5)
        tk.Button(nav_frame, text="Next Page →", command=self.next_page).pack(side="right", padx=20, pady=5)

        # Keyboard shortcuts
        self.root.bind("<Left>", lambda event: self.prev_page())
        self.root.bind("<Right>", lambda event: self.next_page())

        # Load last page and apply theme
        self.load_last_page()
        self.apply_theme()

    def load_page(self, event=None):
        """Fetches and organizes web content into readable chapters."""
        url = self.url_entry.get()
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract headings and paragraphs
            headings = [h.get_text().strip() for h in soup.find_all(['h1', 'h2', 'h3'])]
            paragraphs = [p.get_text().strip() for p in soup.find_all('p') if len(p.get_text().strip()) > 50]

            # Structure text into chapters
            if headings:
                organized_text = "**Table of Contents:**\n\n" + "\n".join(headings) + "\n\n"
                chapters = {}

                for i, heading in enumerate(headings):
                    chapters[heading] = paragraphs[i:i+3] if i < len(paragraphs) else ["(No content available)"]

                for chapter, content in chapters.items():
                    organized_text += f"\n\n**{chapter}**\n" + "\n".join(content) + "\n"

            else:
                organized_text = "**Table of Contents:**\n\n(No headings detected)\n"

            # Display structured content
            self.text_display.delete("1.0", tk.END)
            self.text_display.insert(tk.END, organized_text)
            self.apply_text_format()

        except Exception as e:
            self.text_display.delete("1.0", tk.END)
            self.text_display.insert(tk.END, f"Error: {e}")

    def apply_text_format(self):
        """Formats headings to bold and increases font size."""
        self.text_display.tag_configure("bold", font=("Arial", self.font_size + 4, "bold"))

        # Apply bold formatting to headings
        for heading in self.text_display.get("1.0", tk.END).split("\n"):
            cleaned_heading = heading.replace("**", "").strip()  # Remove asterisks
            if heading.startswith("**") and heading.endswith("**"):
                start_idx = self.text_display.search(heading, "1.0", tk.END)
                end_idx = f"{start_idx} + {len(heading)} chars"
                self.text_display.delete(start_idx, end_idx)  # Remove original text
                self.text_display.insert(start_idx, cleaned_heading)  # Insert cleaned text
                self.text_display.tag_add("bold", start_idx, f"{start_idx} + {len(cleaned_heading)} chars")

        # Increase overall font size
        self.text_display.configure(font=("Arial", self.font_size + 2))

    def prev_page(self):
        """Scrolls up."""
        self.text_display.yview_scroll(-1, "pages")

    def next_page(self):
        """Scrolls down."""
        self.text_display.yview_scroll(1, "pages")

    def increase_font(self):
        """Increase font size."""
        self.font_size += 2
        self.text_display.configure(font=("Arial", self.font_size))

    def decrease_font(self):
        """Decrease font size."""
        self.font_size -= 2
        self.text_display.configure(font=("Arial", self.font_size))

    def toggle_theme(self):
        """Cycle through available themes."""
        themes = ["light", "sepia", "dark"]
        self.theme = themes[(themes.index(self.theme) + 1) % len(themes)]
        self.apply_theme()

    def apply_theme(self):
        """Apply selected theme to UI."""
        self.text_display.config(bg=self.bg_colors[self.theme], fg=self.fg_colors[self.theme])

    def load_last_page(self):
        """Load the last visited webpage."""
        if os.path.exists("last_url.txt"):
            with open("last_url.txt", "r") as file:
                self.url_entry.insert(0, file.read().strip())
            self.load_page()

if __name__ == "__main__":
    root = tk.Tk()
    app = WebReaderApp(root)
    root.mainloop()
