from typing import List

from langchain_core.prompts import PromptTemplate
from langchain_google_vertexai import VertexAI

from .embeddings import EmbeddingsService


class TestCaseGenerator:
    def __init__(self):
        self.llm = VertexAI(
            model_name="gemini-pro",
        )
        self.embeddings_service = EmbeddingsService()
        self.template = """
        Based on the following requirements, generate detailed test cases:
        
        Requirement: {requirement}
        
        Related Context:
        {context}
        
        Generate test cases in the following format:
        - Test Case ID
        - Description
        - Pre-conditions
        - Test Steps
        - Expected Results
        """

        self.prompt = PromptTemplate(
            input_variables=["requirement", "context"],
            template=self.template,
        )

        self.chain = self.prompt | self.llm

    def initialize_context(self, documents: List[str]) -> None:
        """Initialize the vector database with context documents"""
        self.embeddings_service.create_database(documents)

    def generate_test_cases(self, requirement: str, acceptance_criteria: str) -> str:
        # Combine requirement and acceptance criteria for search
        search_query = f"{requirement} {acceptance_criteria}"

        # Get relevant context using similarity search
        relevant_contexts = self.embeddings_service.similarity_search(search_query)
        context = "\n\n".join(relevant_contexts)

        return self.chain.invoke({"requirement": requirement, "context": context})
