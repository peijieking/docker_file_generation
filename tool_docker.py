import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from collections import defaultdict

class DockerfileGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Dockerfile Generator")
        self.root.geometry("1000x700")
        
        # Dockerfile keywords categorized and sorted
        self.docker_keywords = {
            'FROM': {'description': 'Set the base image', 'example': 'FROM ubuntu:22.04'},
            'RUN': {'description': 'Execute commands in the container', 'example': 'RUN apt-get update && apt-get install -y python3'},
            'CMD': {'description': 'Default command to run when container starts', 'example': 'CMD ["python3", "app.py"]'},
            'ENTRYPOINT': {'description': 'Container entry point', 'example': 'ENTRYPOINT ["python3"]'},
            'WORKDIR': {'description': 'Set working directory', 'example': 'WORKDIR /app'},
            'COPY': {'description': 'Copy files from host to container', 'example': 'COPY . /app'},
            'ADD': {'description': 'Copy files with additional features', 'example': 'ADD https://example.com/file.tar.gz /app'},
            'ENV': {'description': 'Set environment variables', 'example': 'ENV PYTHON_VERSION 3.10'},
            'ARG': {'description': 'Build-time variables', 'example': 'ARG BUILD_VERSION=1.0'},
            'LABEL': {'description': 'Add metadata', 'example': 'LABEL maintainer="user@example.com"'},
            'EXPOSE': {'description': 'Expose port', 'example': 'EXPOSE 8000'},
            'VOLUME': {'description': 'Create volume', 'example': 'VOLUME ["/data"]'},
            'USER': {'description': 'Set user', 'example': 'USER appuser'},
            'ONBUILD': {'description': 'Trigger instruction on child images', 'example': 'ONBUILD COPY . /app'},
            'STOPSIGNAL': {'description': 'Set stop signal', 'example': 'STOPSIGNAL SIGTERM'},
            'HEALTHCHECK': {'description': 'Health check', 'example': 'HEALTHCHECK CMD curl -f http://localhost/ || exit 1'},
            'SHELL': {'description': 'Set default shell', 'example': 'SHELL ["/bin/bash", "-c"]'}
        }
        
        # Quick templates for popular applications
        self.quick_templates = {
            'Python Flask': '''FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0"]''',
            'Node.js Express': '''FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["node", "server.js"]''',
            'Django': '''FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]''',
            'React': '''FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]''',
            'Spring Boot': '''FROM openjdk:17-jdk-slim
WORKDIR /app
COPY target/*.jar app.jar
EXPOSE 8080
CMD ["java", "-jar", "app.jar"]''',
            'PHP Apache': '''FROM php:8.2-apache
WORKDIR /var/www/html
COPY . .
EXPOSE 80'''
        }
        
        self.init_ui()
        
    def init_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Left panel - Keywords and Templates
        left_panel = ttk.LabelFrame(main_frame, text="Dockerfile Keywords & Templates", padding="10")
        left_panel.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(1, weight=1)
        
        # Keywords list
        ttk.Label(left_panel, text="Keywords (sorted by category):").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # Categorize keywords by first letter
        categorized_keywords = defaultdict(list)
        for keyword in sorted(self.docker_keywords.keys()):
            categorized_keywords[keyword[0]].append(keyword)
        
        # Create Treeview for categorized keywords
        keywords_frame = ttk.Frame(left_panel)
        keywords_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Create Treeview
        self.keywords_tree = ttk.Treeview(keywords_frame, columns=('description'), show='tree')
        self.keywords_tree.heading('#0', text='Dockerfile Keywords')
        
        # Add scrollbar
        tree_scrollbar = ttk.Scrollbar(keywords_frame, orient="vertical", command=self.keywords_tree.yview)
        self.keywords_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        self.keywords_tree.pack(side="left", fill="both", expand=True)
        tree_scrollbar.pack(side="right", fill="y")
        
        # Populate Treeview with categorized keywords
        for category, keywords in sorted(categorized_keywords.items()):
            # Add category as parent node
            parent_node = self.keywords_tree.insert('', tk.END, text=category, open=True)
            
            # Add keywords as child nodes
            for keyword in keywords:
                self.keywords_tree.insert(parent_node, tk.END, text=keyword, tags=(keyword,))
        
        # Bind selection event
        self.keywords_tree.bind('<<TreeviewSelect>>', self.on_treeview_select)
        
        # Quick templates
        ttk.Label(left_panel, text="Quick Templates:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        template_combo = ttk.Combobox(left_panel, values=list(self.quick_templates.keys()), state="readonly")
        template_combo.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        template_combo.bind('<<ComboboxSelected>>', lambda e: self.on_template_select(template_combo))
        
        # Button to apply template
        apply_template_btn = ttk.Button(left_panel, text="Apply Template", command=lambda: self.apply_template(template_combo))
        apply_template_btn.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Keyword details panel
        details_panel = ttk.LabelFrame(left_panel, text="Keyword Details", padding="10")
        details_panel.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        details_panel.columnconfigure(0, weight=1)
        
        self.keyword_desc_label = ttk.Label(details_panel, text="Select a keyword to see details", wraplength=250)
        self.keyword_desc_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.keyword_example_label = ttk.Label(details_panel, text="", foreground="blue", wraplength=250)
        self.keyword_example_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        # Add to Dockerfile button
        add_to_dockerfile_btn = ttk.Button(details_panel, text="Add to Dockerfile", command=self.add_selected_keyword)
        add_to_dockerfile_btn.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        # Right panel - Dockerfile editor
        right_panel = ttk.LabelFrame(main_frame, text="Dockerfile Content", padding="10")
        right_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(0, weight=1)
        
        self.dockerfile_text = scrolledtext.ScrolledText(right_panel, wrap=tk.WORD, width=60, height=20)
        self.dockerfile_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Button panel
        button_panel = ttk.Frame(main_frame)
        button_panel.grid(row=1, column=1, sticky=(tk.W, tk.E))
        button_panel.columnconfigure(0, weight=1)
        
        # Save button
        save_btn = ttk.Button(button_panel, text="Save Dockerfile", command=self.save_dockerfile)
        save_btn.grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        # Clear button
        clear_btn = ttk.Button(button_panel, text="Clear", command=self.clear_dockerfile)
        clear_btn.grid(row=0, column=1, sticky=tk.W)
        
        # Help button
        help_btn = ttk.Button(button_panel, text="Help", command=self.show_help)
        help_btn.grid(row=0, column=2, sticky=tk.E, padx=(5, 0))
        
    def on_treeview_select(self, event):
        """Handle Treeview selection"""
        selection = self.keywords_tree.selection()
        if selection:
            item = self.keywords_tree.item(selection[0])
            keyword = item['text']
            
            # Check if it's a keyword node (not a category)
            if keyword in self.docker_keywords:
                info = self.docker_keywords[keyword]
                self.keyword_desc_label.config(text=f"{keyword}: {info['description']}")
                self.keyword_example_label.config(text=f"Example: {info['example']}")
                # Store current selected keyword for adding to Dockerfile
                self.current_selected_keyword = keyword
            
    def on_template_select(self, combo):
        """Handle template selection from combobox"""
        template_name = combo.get()
        if template_name:
            template_content = self.quick_templates[template_name]
            # Preview template in a message box
            messagebox.showinfo("Template Preview", f"{template_name} template:\n\n{template_content}")
            
    def apply_template(self, combo):
        """Apply selected template to Dockerfile editor"""
        template_name = combo.get()
        if not template_name:
            messagebox.showwarning("No Template Selected", "Please select a template first")
            return
            
        template_content = self.quick_templates[template_name]
        self.dockerfile_text.delete(1.0, tk.END)
        self.dockerfile_text.insert(tk.END, template_content)
        messagebox.showinfo("Template Applied", f"{template_name} template has been applied")
        
    def add_selected_keyword(self):
        """Add selected keyword example to Dockerfile"""
        if hasattr(self, 'current_selected_keyword'):
            keyword = self.current_selected_keyword
            example = self.docker_keywords[keyword]['example']
            self.dockerfile_text.insert(tk.END, example + '\n')
        else:
            messagebox.showwarning("No Keyword Selected", "Please select a keyword first")
            
    def save_dockerfile(self):
        """Save Dockerfile content to file"""
        content = self.dockerfile_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("Empty Dockerfile", "Dockerfile content is empty")
            return
            
        try:
            with open('Dockerfile', 'w') as f:
                f.write(content)
            messagebox.showinfo("Save Successful", "Dockerfile has been saved successfully")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save Dockerfile: {str(e)}")
            
    def clear_dockerfile(self):
        """Clear Dockerfile editor"""
        self.dockerfile_text.delete(1.0, tk.END)
        
    def show_help(self):
        """Show help information"""
        help_text = """Dockerfile Generator Help:

1. Select Dockerfile keywords from the left panel to see their descriptions and examples.
2. Click "Add to Dockerfile" to add the selected keyword example to the editor.
3. Use quick templates for popular applications by selecting from the dropdown and clicking "Apply Template".
4. Edit the Dockerfile content in the right panel.
5. Click "Save Dockerfile" to save the content to a file named "Dockerfile".
6. Click "Clear" to empty the editor.

Dockerfile keywords are categorized by their first letter for easy navigation."""
        messagebox.showinfo("Help", help_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = DockerfileGenerator(root)
    root.mainloop()