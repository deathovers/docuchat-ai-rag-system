import tiktoken
import re
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import ChatPromptTemplate

class RAGResponse(BaseModel):
    """Schema for structured LLM response to ensure robust parsing."""
    answer: str = Field(description="The answer to the user's question based strictly on the provided context.")
    used_chunk_ids: List[int] = Field(description="The list of integer IDs (e.g., 0, 1, 2) of the context chunks used to formulate the answer.")

class RAGService:
    def __init__(self, api_key: str):
        self.embeddings = OpenAIEmbeddings(openai_api_key=api_key, model="text-embedding-3-small")
        self.llm = ChatOpenAI(openai_api_key=api_key, model="gpt-4o", temperature=0)
        self.tokenizer = tiktoken.encoding_for_model("gpt-4o")
        self.relevance_threshold = 0.5
        self.max_context_tokens = 4000

    async def get_answer(self, vector_store: FAISS, query: str) -> Dict[str, Any]:
        """Retrieves context and generates a grounded response with verified citations."""
        # Sanitize Input
        clean_query = query.strip().replace("{", "[").replace("}", "]")
        
        try:
            # 1. Similarity Search with Relevance Thresholding
            docs_with_scores = vector_store.similarity_search_with_relevance_scores(clean_query, k=8)
            filtered_docs = [doc for doc, score in docs_with_scores if score >= self.relevance_threshold]

            if not filtered_docs:
                return {
                    "answer": "The answer was not found in the uploaded documents (no relevant context found).",
                    "sources": []
                }

            # 2. Document-Level Truncation (Fixes Destructive Truncation)
            # We stop adding full chunks before hitting the token limit to avoid cutting IDs or content.
            final_docs = []
            current_tokens = 0
            
            for i, doc in enumerate(filtered_docs):
                # Safe metadata access (Fixes Unsafe Metadata Access)
                fname = doc.metadata.get("file_name", "Unknown")
                page = doc.metadata.get("page_number", "Unknown")
                
                chunk_repr = f"[[ID:{i}]] Source: {fname}, Page: {page}\nContent: {doc.page_content}\n\n"
                chunk_tokens = len(self.tokenizer.encode(chunk_repr))
                
                if current_tokens + chunk_tokens > self.max_context_tokens:
                    break
                
                final_docs.append(doc)
                current_tokens += chunk_tokens

            # Construct the final context string from the safe list
            context_str = ""
            for i, doc in enumerate(final_docs):
                fname = doc.metadata.get("file_name", "Unknown")
                page = doc.metadata.get("page_number", "Unknown")
                context_str += f"[[ID:{i}]] Source: {fname}, Page: {page}\nContent: {doc.page_content}\n\n"

            # 3. Structured Output Generation (Fixes Brittle Parsing)
            # Using with_structured_output ensures the LLM returns a valid JSON matching our schema.
            structured_llm = self.llm.with_structured_output(RAGResponse)
            
            prompt = ChatPromptTemplate.from_template("""
            You are a helpful assistant. Answer the question strictly using the provided context.
            If the answer is not in the context, say "The answer was not found in the uploaded documents."
            
            For every claim, cite the source file and page number in brackets like [Source: filename, Page: #].
            
            Context:
            {context}
            
            Question: {question}
            """)

            chain = prompt | structured_llm
            result = await chain.ainvoke({"context": context_str, "question": clean_query})
            
            # 4. Map Used IDs back to Metadata
            sources = []
            for idx in result.used_chunk_ids:
                if idx < len(final_docs):
                    doc = final_docs[idx]
                    sources.append({
                        "file_name": doc.metadata.get("file_name", "Unknown"),
                        "page": doc.metadata.get("page_number", "Unknown")
                    })
            
            # Deduplicate sources
            unique_sources = list({f"{s['file_name']}-{s['page']}": s for s in sources}.values())

            return {
                "answer": result.answer,
                "sources": unique_sources
            }

        except Exception as e:
            return {
                "answer": f"An error occurred while processing your request: {str(e)}",
                "sources": []
            }
