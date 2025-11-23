import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json

# Dockerfile keywords with descriptions, categorized and sorted
DOCKER_KEYWORDS = {
    'Base Image': {
        'FROM': 'Specifies the base image to use for the Dockerfile'
    },
    'Maintainer': {
        'MAINTAINER': 'Specifies the maintainer of the Dockerfile (deprecated in favor of LABEL)'
    },
    'Run Commands': {
        'RUN': 'Executes a command in the container during build time',
        'CMD': 'Specifies the default command to run when the container starts',
        'ENTRYPOINT': 'Configures the container to run as an executable'
    },
    'File Operations': {
        'COPY': 'Copies files or directories from the host to the container',
        'ADD': 'Copies files or directories from the host or URL to the container'
    },
    'Environment': {
        'ENV': 'Sets environment variables that persist in the container',
        'ARG': 'Defines build-time variables that can be passed to the build process'
    },
    'Working Directory': {
        'WORKDIR': 'Sets the working directory for subsequent commands'
    },
    'User': {
        'USER': 'Specifies the user to run the container as'
    },
    'Expose Ports': {
        'EXPOSE': 'Informs Docker that the container listens on specified ports at runtime'
    },
    'Volumes': {
        'VOLUME': 'Creates a mount point for external volumes or other containers'
    },
    'Labels': {
        'LABEL': 'Adds metadata to the image in the form of key-value pairs'
    },
    'Onbuild': {
        'ONBUILD': 'Adds a trigger instruction to be executed when the image is used as a base image'
    },
    'Healthcheck': {
        'HEALTHCHECK': 'Configures how Docker checks if the container is still working'
    },
    'Shell': {
        'SHELL': 'Overrides the default shell used for RUN, CMD, and ENTRYPOINT commands'
    },
    'Stop Signal': {
        'STOPSIGNAL': 'Specifies the signal to send to the container to stop it'
    }
}

# Sort keywords alphabetically within each category
for category in DOCKER_KEYWORDS:
    DOCKER_KEYWORDS[category] = dict(sorted(DOCKER_KEYWORDS[category].items()))

# Quick templates for common applications
QUICK_TEMPLATES = {
    'Python': '''FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]''',
    'Node.js': '''FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "start"]''',
    'Java': '''FROM openjdk:11-jre-slim
WORKDIR /app
COPY target/*.jar app.jar
EXPOSE 8080
CMD ["java", "-jar", "app.jar"]''',
    'Go': '''FROM golang:1.17-alpine
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN go build -o main .
EXPOSE 8080
CMD ["./main"]''',
    'PHP': '''FROM php:8.0-apache
WORKDIR /var/www/html
COPY . .
EXPOSE 80''',
    'Nginx': '''FROM nginx:alpine
COPY nginx.conf /etc/nginx/nginx.conf
COPY html /usr/share/nginx/html
EXPOSE 80 443'''
}

class DockerfileGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Dockerfile Generator")
        self.root.geometry("1200x700")
        
        # Create main frame with padding
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.main_frame.rowconfigure(3, weight=1)
        
        # Create widgets
        self.create_widgets()
        
    def create_widgets(self):
        # Title
        title_label = ttk.Label(self.main_frame, text="Dockerfile Generator", font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Left Panel - Keywords
        left_frame = ttk.Frame(self.main_frame)
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(0, weight=1)
        
        # Keywords Section
        keywords_frame = ttk.LabelFrame(left_frame, text="Dockerfile Keywords", padding="5")
        keywords_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        keywords_frame.columnconfigure(0, weight=1)
        keywords_frame.rowconfigure(0, weight=1)
        
        # Treeview for keywords
        self.keyword_tree = ttk.Treeview(keywords_frame, columns=('Keyword',), show='tree')
        self.keyword_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add scrollbar
        keyword_scroll = ttk.Scrollbar(keywords_frame, orient=tk.VERTICAL, command=self.keyword_tree.yview)
        keyword_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.keyword_tree.configure(yscrollcommand=keyword_scroll.set)
        
        # Populate keyword tree
        self.populate_keyword_tree()
        
        # Bind events
        self.keyword_tree.bind('<Double-1>', self.add_keyword)
        self.keyword_tree.bind('<<TreeviewSelect>>', self.show_keyword_description)
        
        # Right Panel - Upper, Middle, Lower sections
        right_frame = ttk.Frame(self.main_frame)
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0), pady=(0, 10))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)  # Middle section takes most space
        
        # Upper Section - Keyword Description and Input
        upper_frame = ttk.LabelFrame(right_frame, text="Keyword Information", padding="5")
        upper_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 10))
        upper_frame.columnconfigure(0, weight=1)
        
        # Keyword Description
        desc_label = ttk.Label(upper_frame, text="Description:", font=('Arial', 10, 'bold'))
        desc_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.description_text = tk.Text(upper_frame, wrap=tk.WORD, font=('Arial', 9), state='disabled', height=4)
        self.description_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        desc_scroll = ttk.Scrollbar(upper_frame, orient=tk.VERTICAL, command=self.description_text.yview)
        desc_scroll.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.description_text.configure(yscrollcommand=desc_scroll.set)
        
        # User Input Section
        input_label = ttk.Label(upper_frame, text="Manual Input:", font=('Arial', 10, 'bold'))
        input_label.grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        self.manual_input = ttk.Entry(upper_frame, width=50)
        self.manual_input.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        add_input_btn = ttk.Button(upper_frame, text="Add to Dockerfile", command=self.add_manual_input)
        add_input_btn.grid(row=3, column=1, padx=(5, 0))
        
        # Middle Section - Dockerfile Preview
        middle_frame = ttk.LabelFrame(right_frame, text="Dockerfile Preview", padding="5")
        middle_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        middle_frame.columnconfigure(0, weight=1)
        middle_frame.rowconfigure(0, weight=1)
        
        self.dockerfile_text = tk.Text(middle_frame, wrap=tk.WORD, font=('Courier', 10))
        self.dockerfile_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        content_scroll = ttk.Scrollbar(middle_frame, orient=tk.VERTICAL, command=self.dockerfile_text.yview)
        content_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.dockerfile_text.configure(yscrollcommand=content_scroll.set)
        
        # Lower Section - Quick Templates and Buttons
        lower_frame = ttk.LabelFrame(right_frame, text="Quick Templates", padding="5")
        lower_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.S))
        lower_frame.columnconfigure(0, weight=1)
        
        self.template_var = tk.StringVar()
        template_combo = ttk.Combobox(lower_frame, textvariable=self.template_var, values=list(QUICK_TEMPLATES.keys()), state='readonly', width=30)
        template_combo.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        load_template_btn = ttk.Button(lower_frame, text="Load Template", command=self.load_template)
        load_template_btn.grid(row=0, column=1, padx=(0, 10))
        
        clear_btn = ttk.Button(lower_frame, text="Clear", command=self.clear_content)
        clear_btn.grid(row=0, column=2, padx=(0, 10))
        
        save_btn = ttk.Button(lower_frame, text="Save Dockerfile", command=self.save_dockerfile)
        save_btn.grid(row=0, column=3)
        
        # Configure grid weights for main frame
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=3)
        self.main_frame.rowconfigure(1, weight=1)
        
    def populate_keyword_tree(self):
        # Add categories and keywords to treeview
        for category in sorted(DOCKER_KEYWORDS.keys()):
            parent = self.keyword_tree.insert('', 'end', text=category)
            for keyword, description in DOCKER_KEYWORDS[category].items():
                self.keyword_tree.insert(parent, 'end', text=keyword, values=(keyword, description))
    
    def show_keyword_description(self, event):
        # Get selected item
        item = self.keyword_tree.selection()[0]
        values = self.keyword_tree.item(item, 'values')
        
        if values and len(values) > 1:
            description = values[1]
            # Update description text widget
            self.description_text.config(state='normal')
            self.description_text.delete(1.0, tk.END)
            self.description_text.insert(1.0, description)
            self.description_text.config(state='disabled')
        else:
            # Clear description if a category is selected
            self.description_text.config(state='normal')
            self.description_text.delete(1.0, tk.END)
            self.description_text.config(state='disabled')
    
    def add_manual_input(self):
        # Get user input
        input_text = self.manual_input.get().strip()
        
        if input_text:
            # Insert input at cursor position
            cursor_pos = self.dockerfile_text.index(tk.INSERT)
            self.dockerfile_text.insert(cursor_pos, f"{input_text}\n")
            # Clear input field
            self.manual_input.delete(0, tk.END)
            # Set focus back to text widget
            self.dockerfile_text.focus()
        
    def add_keyword(self, event):
        # Get selected item
        item = self.keyword_tree.selection()[0]
        values = self.keyword_tree.item(item, 'values')
        
        if values and len(values) > 0:
            keyword = values[0]
            # Insert keyword at cursor position
            cursor_pos = self.dockerfile_text.index(tk.INSERT)
            self.dockerfile_text.insert(cursor_pos, f"{keyword} ")
            # Move cursor after the inserted text
            self.dockerfile_text.mark_set(tk.INSERT, f"{cursor_pos}+{len(keyword)+1}c")
            # Set focus back to text widget
            self.dockerfile_text.focus()
        
    def load_template(self):
        template_name = self.template_var.get()
        if template_name:
            template_content = QUICK_TEMPLATES[template_name]
            self.dockerfile_text.delete(1.0, tk.END)
            self.dockerfile_text.insert(1.0, template_content)
        else:
            messagebox.showwarning("Warning", "Please select a template first!")
        
    def clear_content(self):
        self.dockerfile_text.delete(1.0, tk.END)
        
    def save_dockerfile(self):
        content = self.dockerfile_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("Warning", "Dockerfile content is empty!")
            return
        
        # Ask for file path
        file_path = filedialog.asksaveasfilename(
            defaultextension=".dockerfile",
            filetypes=[("Dockerfile", "*.dockerfile"), ("All Files", "*.*")],
            initialfile="Dockerfile"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(content)
                messagebox.showinfo("Success", f"Dockerfile saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save Dockerfile: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DockerfileGenerator(root)
    root.mainloop()