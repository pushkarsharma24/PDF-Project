import fitz  # PyMuPDF
import re
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox

def extract_headings_and_subheadings(pdf_path):
    doc = fitz.open(pdf_path)
    headings_and_subheadings = []

    # Define refined regex patterns for headings and subheadings
    heading_pattern = re.compile(r'^(Chapter|Section|[A-Z][A-Z0-9].*)$')
    subheading_pattern = re.compile(r'^\d+\.\d+.*|^[A-Z][A-Za-z\s]{3,}$')  # Ensuring subheadings are longer and more structured

    current_context = None
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        lines = text.split("\n")

        # Skip lines that might be part of a table
        filtered_lines = [line for line in lines if not is_table_line(line)]

        for line in filtered_lines:
            line = line.strip()
            if heading_pattern.match(line):
                if current_context:
                    headings_and_subheadings.append(current_context)
                current_context = ("Heading", line, [])
            elif subheading_pattern.match(line):
                if current_context:
                    headings_and_subheadings.append(current_context)
                current_context = ("Subheading", line, [])
            elif current_context:
                current_context[2].append(line)
    if current_context:
        headings_and_subheadings.append(current_context)

    return headings_and_subheadings

def is_table_line(line):
    # Basic heuristic to identify table lines
    # This can be customized based on the specific table patterns you encounter
    return len(line) < 10 or re.search(r'\d+', line)  # Simple check for short lines or lines with numbers

def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if file_path:
        status_var.set("Loading PDF...")
        root.update_idletasks()  # Update the status message
        try:
            headings_and_subheadings = extract_headings_and_subheadings(file_path)
            display_headings_and_subheadings(headings_and_subheadings)
            status_var.set("Done")
        except Exception as e:
            status_var.set("Error")
            messagebox.showerror("Error", f"An error occurred: {e}")

def display_headings_and_subheadings(headings_and_subheadings):
    text_area.delete(1.0, tk.END)
    for item_type, text, context in headings_and_subheadings:
        if item_type == "Heading":
            text_area.insert(tk.END, f"Heading: {text}\n", "heading")
        elif item_type == "Subheading":
            text_area.insert(tk.END, f"  Subheading: {text}\n", "subheading")
        for line in context:
            text_area.insert(tk.END, f"    {line}\n")

def save_to_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML Files", "*.html")])
    if file_path:
        try:
            # Create an HTML file
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write("<!DOCTYPE html>\n")
                file.write("<html lang='en'>\n")
                file.write("<head>\n")
                file.write("<meta charset='UTF-8'>\n")
                file.write("<meta name='viewport' content='width=device-width, initial-scale=1.0'>\n")
                file.write("<title>Extracted PDF Content</title>\n")
                file.write("<style>\n")
                file.write("body { font-family: Arial, sans-serif; margin: 20px; }\n")
                file.write(".heading { color: blue; font-size: 18px; font-weight: bold; margin-top: 20px; }\n")
                file.write(".subheading { color: gold; font-size: 16px; font-weight: bold; margin-left: 20px; margin-top: 10px; }\n")
                file.write(".context { margin-left: 40px; margin-top: 5px; }\n")
                file.write("</style>\n")
                file.write("</head>\n")
                file.write("<body>\n")

                content = text_area.get(1.0, tk.END)
                for line in content.split('\n'):
                    line = line.strip()
                    if line.startswith("Heading:"):
                        file.write(f"<p class='heading'>{line}</p>\n")
                    elif line.startswith("  Subheading:"):
                        file.write(f"<p class='subheading'>{line.strip()}</p>\n")
                    elif line.startswith("    "):
                        if line.strip():  # Only write non-empty lines
                            file.write(f"<p class='context'>{line.strip()}</p>\n")
                
                file.write("</body>\n")
                file.write("</html>\n")
            
            status_var.set("File saved")
        except Exception as e:
            status_var.set("Error")
            messagebox.showerror("Error", f"An error occurred while saving: {e}")

# Setup Tkinter window
root = tk.Tk()
root.title("PDF Headings and Subheadings Extractor")

# Create and place widgets
open_button = tk.Button(root, text="Open PDF", command=open_file)
open_button.pack(pady=5)

save_button = tk.Button(root, text="Save to HTML", command=save_to_file)
save_button.pack(pady=5)

text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=100, height=30)  # Increased size
text_area.pack(pady=10)

# Status bar
status_var = tk.StringVar()
status_bar = tk.Label(root, textvariable=status_var, relief=tk.SUNKEN, anchor=tk.W)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)
status_var.set("Ready")

# Apply tags for styling
text_area.tag_config("heading", foreground="blue", font=("Helvetica", 12, "bold"))
text_area.tag_config("subheading", foreground="gold", font=("Helvetica", 10, "bold"))

# Run the application
root.mainloop()

