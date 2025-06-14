import ollama
from typing import Optional
import time

class Summarizer:
    DEFAULT_MODEL = "llama3"
    DEFAULT_TEMPERATURE = 0.3
    DEFAULT_MAX_TOKENS = 2000

    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model
        self.last_response_time = None

    def summarize(self, text: str, instruction: str, temperature: float = DEFAULT_TEMPERATURE) -> Optional[str]:
        """
        Summarizes text based on given instructions.
        
        Args:
            text: The text to summarize
            instruction: How to summarize the text
            temperature: Creativity control (0-1)
            
        Returns:
            The summary or None if failed
        """
        system_prompt = (
            f"You are an AI assistant focused on summarizing information. "
            f"Your task is to process the following content according to these instructions: {instruction}. "
            f"Provide a clear, concise summary preserving all key information."
        )

        try:
            start_time = time.time()
            response = ollama.chat(
                model=self.model,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': text}
                ],
                options={
                    'temperature': temperature,
                    'num_ctx': self.DEFAULT_MAX_TOKENS
                }
            )
            self.last_response_time = time.time() - start_time
            return response['message']['content']
        except Exception as e:
            print(f"Summarization error: {str(e)}")
            return None

    def summarize_chunks(self, chunks: list, instruction: str) -> str:
        """Summarizes text chunks with a final consolidation step."""
        summaries = []
        
        for chunk in chunks:
            summary = self.summarize(chunk, instruction)
            if summary:
                summaries.append(summary)
        
        if not summaries:
            return "Failed to generate summary."
        
        # Final consolidation
        combined = "\n\n".join(summaries)
        final_instruction = (
            f"Combine these partial summaries into one coherent summary "
            f"following the original instructions: {instruction}"
        )
        return self.summarize(combined, final_instruction) or "Failed to generate final summary."