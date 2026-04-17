import tkinter as tk
from tkinter import font
import math

class ModernCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Premium Calculator")
        self.root.geometry("360x520")
        self.root.resizable(False, False)
        self.root.configure(bg="#121212")

        self.expression = ""
        
        # Custom Fonts
        try:
            # Try to use a modern font if available
            self.display_font = font.Font(family="Segoe UI", size=36, weight="bold")
            self.button_font = font.Font(family="Segoe UI", size=14, weight="normal")
        except:
            self.display_font = ("Arial", 36, "bold")
            self.button_font = ("Arial", 14)

        # UI Components
        self._create_display()
        self._create_buttons()

    def _create_display(self):
        """Creates the result display area."""
        self.display_frame = tk.Frame(self.root, bg="#121212", height=120)
        self.display_frame.pack(expand=True, fill="both")

        self.label = tk.Label(
            self.display_frame, 
            text="0", 
            anchor="e", 
            bg="#121212", 
            fg="#FFFFFF", 
            padx=25, 
            font=self.display_font
        )
        self.label.pack(expand=True, fill="both")

    def _create_buttons(self):
        """Creates the grid of buttons."""
        self.buttons_frame = tk.Frame(self.root, bg="#121212", padx=10, pady=10)
        self.buttons_frame.pack(expand=True, fill="both")

        # Button Layout: (Label, Row, Column, Type)
        # Type: 0=Number, 1=Operator, 2=Special/Clear
        buttons = [
            ('C', 0, 0, 2), ('DEL', 0, 1, 2), ('%', 0, 2, 1), ('/', 0, 3, 1),
            ('7', 1, 0, 0), ('8', 1, 1, 0), ('9', 1, 2, 0), ('*', 1, 3, 1),
            ('4', 2, 0, 0), ('5', 2, 1, 0), ('6', 2, 2, 0), ('-', 2, 3, 1),
            ('1', 3, 0, 0), ('2', 3, 1, 0), ('3', 3, 2, 0), ('+', 3, 3, 1),
            ('0', 4, 0, 0), ('.', 4, 1, 0), ('=', 4, 2, 1, 2) # Label, R, C, T, ColSpan
        ]

        # Style configurations
        style = {
            0: {"bg": "#333333", "fg": "#FFFFFF", "active": "#444444"},  # Numbers
            1: {"bg": "#FF9500", "fg": "#FFFFFF", "active": "#FFB040"},  # Operators
            2: {"bg": "#A5A5A5", "fg": "#000000", "active": "#D4D4D4"},  # Specials
        }

        for btn_info in buttons:
            label = btn_info[0]
            r = btn_info[1]
            c = btn_info[2]
            btn_type = btn_info[3]
            colspan = btn_info[4] if len(btn_info) > 4 else 1

            btn = tk.Button(
                self.buttons_frame,
                text=label,
                font=self.button_font,
                bg=style[btn_type]["bg"],
                fg=style[btn_type]["fg"],
                activebackground=style[btn_type]["active"],
                activeforeground=style[btn_type]["fg"],
                borderwidth=0,
                cursor="hand2",
                command=lambda x=label: self._on_button_click(x)
            )
            btn.grid(row=r, column=c, columnspan=colspan, sticky="nsew", padx=5, pady=5)

        # Make buttons expand
        for i in range(4):
            self.buttons_frame.grid_columnconfigure(i, weight=1)
        for i in range(5):
            self.buttons_frame.grid_rowconfigure(i, weight=1)

    def _on_button_click(self, char):
        if char == "C":
            self.expression = ""
        elif char == "DEL":
            self.expression = self.expression[:-1]
        elif char == "=":
            try:
                # Basic sanitization and evaluation
                # Using eval with limited scope is generally okay for a local calculator
                result = str(eval(self.expression.replace('%', '/100')))
                self.expression = result
            except ZeroDivisionError:
                self.expression = "Error: Div/0"
            except Exception:
                self.expression = "Error"
        else:
            if "Error" in self.expression:
                self.expression = ""
            self.expression += str(char)
        
        self._update_display()

    def _update_display(self):
        text = self.expression if self.expression else "0"
        # Truncate if too long
        if len(text) > 12:
            text = text[:12]
        self.label.config(text=text)

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernCalculator(root)
    root.mainloop()
