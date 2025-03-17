# pdfReader.py
import os
import PyPDF2
import tkinter as tk
from tkinter import ttk  # Add this import for the progress bar
from tkinter import filedialog
from summarize import Main_agent
from math import ceil

__all__ = ['info_input', 'user_input']

# Global variables
info_input = ""
user_input = ""
CHUNK_SIZE = 1000  # Approximate characters per chunk

def split_text_into_chunks(text, chunk_size=CHUNK_SIZE):
    """
    Splits text into chunks of approximately equal size.
    
    Parameters:
    text (str): The text to split
    chunk_size (int): Target size for each chunk in characters
    
    Returns:
    list: List of text chunks
    """
    # Split by sentences to maintain context
    sentences = text.replace('\n', ' ').split('. ')
    chunks = []
    current_chunk = []
    current_size = 0
    
    for sentence in sentences:
        sentence = sentence.strip() + '. '
        sentence_size = len(sentence)
        
        if current_size + sentence_size > chunk_size and current_chunk:
            chunks.append(''.join(current_chunk))
            current_chunk = []
            current_size = 0
            
        current_chunk.append(sentence)
        current_size += sentence_size
    
    if current_chunk:
        chunks.append(''.join(current_chunk))
    
    return chunks

def extract_pdf_text(pdf_path):
    """
    Extracts the text content from a PDF file.
    
    Parameters:
    pdf_path (str): The file path of the PDF document.
    
    Returns:
    str: The text content of the PDF file.
    """
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ''
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
    return text

def select_pdf_file():
    """
    Opens a file dialog to allow the user to select a PDF file.
    """
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if file_path:
        global info_input
        text_content = extract_pdf_text(file_path)
        info_input = text_content
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, text_content)

def get_response():
    global user_input, info_input
    if not info_input or not user_input:
        return "Error: Missing required inputs to generate a response."
    
    # Split the text into chunks
    chunks = split_text_into_chunks(info_input)
    
    # Process each chunk
    responses = []
    progress_var.set(0)
    total_chunks = len(chunks)
    
    for i, chunk in enumerate(chunks, 1):
        response = Main_agent(user_input, chunk)
        responses.append(response)
        # Update progress bar
        progress = (i / total_chunks) * 100
        progress_var.set(progress)
        root.update_idletasks()
    
    # Combine responses with a summary prompt
    combined_response = "\n\n".join(responses)
    final_summary = Main_agent(
        "Provide a coherent summary combining all the following information: " + user_input,
        combined_response
    )
    
    return final_summary

def get_user_input():
    """
    Retrieves the user's input from the text box and processes the response.
    """
    global user_input, info_input
    user_input = user_text.get("1.0", tk.END).strip()
    
    # Disable input while processing
    get_input_button.config(state=tk.DISABLED)
    progress_label.pack()
    progress_bar.pack()
    
    # Get and display response
    response = get_response()
    response_text.delete("1.0", tk.END)
    response_text.insert(tk.END, response)
    
    # Re-enable input and hide progress
    get_input_button.config(state=tk.NORMAL)
    progress_label.pack_forget()
    progress_bar.pack_forget()

# Create the main window
root = tk.Tk()
root.title("PDF Summarizer")

# Create the select file button
select_button = tk.Button(root, text="Select PDF File", command=select_pdf_file)
select_button.pack(pady=10)

# Create the text output area and scrollbar for PDF content
text_frame = tk.Frame(root)
text_frame.pack(pady=10)

output_text = tk.Text(text_frame, height=15, width=80, wrap=tk.WORD)
output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(text_frame, command=output_text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

output_text['yscrollcommand'] = scrollbar.set

# Create the user input area
user_frame = tk.Frame(root)
user_frame.pack(pady=10)

user_label = tk.Label(user_frame, text="Enter your query:")
user_label.pack(side=tk.LEFT)

user_text = tk.Text(user_frame, height=3, width=50)
user_text.pack(side=tk.LEFT, padx=10)

get_input_button = tk.Button(user_frame, text="Process", command=get_user_input)
get_input_button.pack(side=tk.LEFT)

# Progress bar
progress_var = tk.DoubleVar()
progress_label = tk.Label(root, text="Processing chunks...")
progress_bar = ttk.Progressbar(  # Changed from tk.ttk to just ttk
    root,
    variable=progress_var,
    maximum=100,
    length=300,
    mode='determinate'
)

# Response text area
response_frame = tk.Frame(root)
response_frame.pack(pady=10, fill=tk.BOTH, expand=True)

response_label = tk.Label(response_frame, text="Summary:")
response_label.pack()

response_text = tk.Text(response_frame, height=15, width=80, wrap=tk.WORD)
response_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

response_scrollbar = tk.Scrollbar(response_frame, command=response_text.yview)
response_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

response_text['yscrollcommand'] = response_scrollbar.set

# Run the main event loop
if __name__ == "__main__":
    root.mainloop()