import tkinter as tk
import requests
from bs4 import BeautifulSoup

class WebReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Web Page Reader")
        
        # Entry for URL
        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.pack(pady=10)
        
        # Load Button
        self.load_button = tk.Button(root, text="Load", command=self.load_page)
        self.load_button.pack(pady=5)
        
        # Text Display
        self.text_display = tk.Text(root, wrap="word", font=("Arial", 12), height=20, width=60)
        self.text_display.pack(pady=10)
        
        # Font Size Controls
        self.font_size = 12
        self.increase_button = tk.Button(root, text="Increase Font", command=self.increase_font)
        self.increase_button.pack(pady=5)
        self.decrease_button = tk.Button(root, text="Decrease Font", command=self.decrease_font)
        self.decrease_button.pack(pady=5)
    
    def load_page(self):
        url = self.url_entry.get()
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            text_content = soup.get_text()
            
            self.text_display.delete("1.0", tk.END)
            self.text_display.insert(tk.END, text_content)
        except Exception as e:
            self.text_display.delete("1.0", tk.END)
            self.text_display.insert(tk.END, f"Error: {e}")
    
    def increase_font(self):
        self.font_size += 2
        self.text_display.configure(font=("Arial", self.font_size))

    def decrease_font(self):
        self.font_size -= 2
        self.text_display.configure(font=("Arial", self.font_size))

# Run the App
if __name__ == "__main__":
    root = tk.Tk()
    app = WebReaderApp(root)
    root.mainloop()
