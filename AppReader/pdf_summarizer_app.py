import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional
from pdf_processor import PDFProcessor
from summarize import Summarizer
import threading

class PDFSummarizerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Enhanced PDF Summarizer")
        self.root.geometry("900x700")
        
        # Configuration
        self.pdf_processor = PDFProcessor()
        self.summarizer = Summarizer()
        self.current_file = None
        self.is_processing = False
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize all UI components."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # File selection
        file_frame = ttk.LabelFrame(main_frame, text="PDF Document", padding="10")
        file_frame.pack(fill=tk.X, pady=5)
        
        self.file_label = ttk.Label(file_frame, text="No file selected")
        self.file_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        select_btn = ttk.Button(file_frame, text="Browse...", command=self.select_file)
        select_btn.pack(side=tk.RIGHT)
        
        # PDF content preview
        preview_frame = ttk.LabelFrame(main_frame, text="Document Content", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.preview_text = tk.Text(preview_frame, wrap=tk.WORD, height=10)
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(preview_frame, command=self.preview_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.preview_text['yscrollcommand'] = scrollbar.set
        
        # User instructions
        instruction_frame = ttk.LabelFrame(main_frame, text="Summary Instructions", padding="10")
        instruction_frame.pack(fill=tk.X, pady=5)
        
        self.instruction_text = tk.Text(instruction_frame, wrap=tk.WORD, height=3)
        self.instruction_text.pack(fill=tk.X)
        self.instruction_text.insert("1.0", "Summarize the key points of this document...")
        
        # Controls
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        self.summarize_btn = ttk.Button(
            control_frame, 
            text="Generate Summary", 
            command=self.start_summarization,
            state=tk.DISABLED
        )
        self.summarize_btn.pack(side=tk.RIGHT)
        
        # Progress
        self.progress = ttk.Progressbar(control_frame, mode='determinate')
        self.status_label = ttk.Label(control_frame, text="Ready")
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Summary output
        summary_frame = ttk.LabelFrame(main_frame, text="Summary", padding="10")
        summary_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.summary_text = tk.Text(summary_frame, wrap=tk.WORD)
        self.summary_text.pack(fill=tk.BOTH, expand=True)
        
        summary_scroll = ttk.Scrollbar(summary_frame, command=self.summary_text.yview)
        summary_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.summary_text['yscrollcommand'] = summary_scroll.set
        
    def select_file(self):
        """Handle PDF file selection."""
        file_path = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        
        if file_path:
            self.current_file = file_path
            self.file_label.config(text=file_path)
            self.load_file_contents(file_path)
            self.summarize_btn.config(state=tk.NORMAL)
    
    def load_file_contents(self, file_path: str):
        """Load and display PDF contents."""
        try:
            text = self.pdf_processor.extract_text(file_path)
            cleaned_text = self.pdf_processor.clean_text(text)
            self.preview_text.delete("1.0", tk.END)
            self.preview_text.insert("1.0", cleaned_text)
            self.status("File loaded successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load PDF: {str(e)}")
            self.status("Error loading file")
    
    def start_summarization(self):
        """Start the summarization process in a separate thread."""
        if self.is_processing:
            return
            
        instruction = self.instruction_text.get("1.0", tk.END).strip()
        if not instruction:
            messagebox.showwarning("Warning", "Please enter summary instructions")
            return
            
        if not self.current_file:
            messagebox.showwarning("Warning", "Please select a PDF file first")
            return
            
        self.is_processing = True
        self.summarize_btn.config(state=tk.DISABLED)
        self.status("Processing...")
        self.progress["value"] = 0
        
        # Run in background thread to keep UI responsive
        threading.Thread(
            target=self.run_summarization,
            args=(self.current_file, instruction),
            daemon=True
        ).start()
    
    def run_summarization(self, file_path: str, instruction: str):
        """Perform the actual summarization work."""
        try:
            # Step 1: Extract and chunk text
            self.update_status("Extracting text...")
            text = self.pdf_processor.extract_text(file_path)
            chunks = self.pdf_processor.smart_chunking(text)
            
            # Step 2: Process chunks
            self.update_status("Summarizing chunks...")
            self.progress["maximum"] = len(chunks) + 1  # +1 for final step
            
            summary = self.summarizer.summarize_chunks(chunks, instruction)
            
            # Update UI with results
            self.root.after(0, self.display_summary, summary)
            self.root.after(0, self.status, "Summary complete")
            
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Error", f"Summarization failed: {str(e)}")
            self.root.after(0, self.status, "Error during summarization")
        finally:
            self.root.after(0, lambda: self.summarize_btn.config(state=tk.NORMAL))
            self.is_processing = False
    
    def display_summary(self, summary: str):
        """Display the generated summary."""
        self.summary_text.delete("1.0", tk.END)
        self.summary_text.insert("1.0", summary)
        self.progress["value"] = self.progress["maximum"]  # Complete progress
    
    def status(self, message: str):
        """Update status message."""
        self.status_label.config(text=message)
    
    def update_status(self, message: str):
        """Thread-safe status update."""
        self.root.after(0, self.status, message)
        self.root.after(0, lambda: self.progress.step(1))
    
    def run(self):
        """Start the application."""
        self.root.mainloop()