import re
import tiktoken
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from app.core.config import settings

class RAGService:
    def __init__(self, api_key: str):
        self.embeddings = OpenAIEmbeddings(openai_api_key=api_key, model="text-embedding-3-small")
        self.llm = ChatOpenAI(openai_api_key=api_key, model="gpt-4o", temperature=0)
        self.tokenizer = tiktoken.encoding_for_model("gpt-4o")
        self.relevance_threshold = 0.5
        self.max_context_tokens = 4000

    def create_vector_store(self, documents: List[Document]) -> FAISS:
        """Creates an in-memory FAISS index from documents."""
        try:
            return FAISS.from_documents(documents, self.embeddings)
        except Exception as e:
            raise RuntimeError(f"Failed to create vector store: {str(e)}")

    async def get_answer(self, vector_store: FAISS, query: str) -> Dict[str, Any]:
        """Retrieves context and generates a grounded response with verified citations."""
        # 1. Sanitize Input
        clean_query = query.strip().replace("{", "[").replace("}", "]")
        
        try:
            # 2. Similarity Search with Relevance Thresholding
            # Note: similarity_search_with_relevance_scores returns (doc, score)
            docs_with_scores = vector_store.similarity_search_with_relevance_scores(clean_query, k=5)
            filtered_docs = [doc for doc, score in docs_with_scores if score >= self.relevance_threshold]

            if not filtered_docs:
                return {
                    "answer": "The answer was not found in the uploaded documents (no relevant context found).",
                    "sources": []
                }

            # 3. Context Construction & Token Validation
            context_parts = []
            for i, d in enumerate(filtered_docs):
                part = f"[[ID:{i}]] Source: {d.metadata['file_name']}, Page: {d.metadata['page_number']}\nContent: {d.page_content}"
                context_parts.append(part)
            
            context_str = "\n\n".join(context_parts)
            
            # Truncate if over limit
            tokens = self.tokenizer.encode(context_str)
            if len(tokens) > self.max_context_tokens:
                context_str = self.tokenizer.decode(tokens[:self.max_context_tokens])

            # 4. Prompt Engineering for Strict Grounding
            prompt = ChatPromptTemplate.from_template("""
            You are a helpful assistant. Answer the question strictly using the provided context.
            If the answer is not in the context, say "The answer was not found in the uploaded documents."
            
            For every claim, cite the source file and page number in brackets like [Source: filename, Page: #].
            
            Context:
            {context}
            
            Question: {question}
            
            Instructions:
            - Provide a detailed answer.
            - At the end of your response, list the IDs of the chunks you used. 
            Format: USED_CHUNKS: [ID:0, ID:2]
            """)

            chain = prompt | self.llm
            response = await chain.ainvoke({"context": context_str, "question": clean_query})
            
            # 5. Extract Used Sources
            answer_text = response.content
            used_ids = self._parse_used_ids(answer_text)
            
            # Clean the answer text from the ID list
            final_answer = re.sub(r"USED_CHUNKS:.*", "", answer_text, flags=re.DOTALL).strip()
            
            # Map IDs back to metadata
            sources = []
            for idx in used_ids:
                if idx < len(filtered_docs):
                    doc = filtered_docs[idx]
                    sources.append({
                        "file_name": doc.metadata["file_name"],
                        "page": doc.metadata["page_number"]
                    })
            
            # Deduplicate sources
            unique_sources = list({f"{s['file_name']}-{s['page']}": s for s in sources}.values())

            return {
                "answer": final_answer,
                "sources": unique_sources
            }

        except Exception as e:
            return {
                "answer": f"An error occurred while processing your request: {str(e)}",
                "sources": []
            }

    def _parse_used_ids(self, text: str) -> List[int]:
        """Extracts chunk IDs from the LLM response."""
        match = re.search(r"USED_CHUNKS:\s*\[(.*?)\]", text)
        if not match:
            return []
        ids_str = match.group(1)
        # Extract numbers from strings like "ID:0"
        return [int(re.search(r"\d+", i).group()) for i in ids_str.split(",") if "ID:" in i]
