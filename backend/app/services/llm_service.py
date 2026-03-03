import google.generativeai as genai
from typing import List, Tuple
from langchain.docstore.document import Document

class LLMService:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    async def generate_answer(self, query: str, context_docs: List[Document], history: List[dict]) -> Tuple[str, List[dict]]:
        context_text = "\n\n".join([
            f"--- SOURCE: {doc.metadata['source']} (Page {doc.metadata['page']}) ---\n{doc.page_content}"
            for doc in context_docs
        ])

        system_prompt = f"""
        You are a helpful AI assistant. Use the following context to answer the user's question.
        
        STRICT RULES:
        1. Use ONLY the provided context. 
        2. If the answer is not in the context, say: "The answer was not found in the uploaded documents."
        3. For every claim, cite the source in the format: [Document Name - Page X].
        4. Maintain a professional tone.

        CONTEXT:
        {context_text}
        """

        # Simple history formatting
        chat = self.model.start_chat(history=[])
        response = chat.send_message(f"{system_prompt}\n\nQuestion: {query}")
        
        sources = [
            {"doc_name": doc.metadata['source'], "page_number": doc.metadata['page']}
            for doc in context_docs
        ]
        
        # Deduplicate sources
        unique_sources = []
        seen = set()
        for s in sources:
            identifier = f"{s['doc_name']}-{s['page_number']}"
            if identifier not in seen:
                unique_sources.append(s)
                seen.add(identifier)

        return response.text, unique_sources
