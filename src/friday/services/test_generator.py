from typing import List

from langchain_core.prompts import PromptTemplate

from friday.llm.llm import ModelProvider, get_llm_client
from friday.services.embeddings import EmbeddingsService


class TestCaseGenerator:
    def __init__(self, provider: ModelProvider = "vertex"):
        self.llm = get_llm_client(provider)
        self.embeddings_service = EmbeddingsService(provider=provider)
        self.template = """
        Based on the following requirements, generate detailed test cases:
        
        Requirement: {requirement}
        
        Related Context:
        {context}
        
        Generate test cases in the following format:
         - Test Case ID: <unique id>
         - Title: [Brief description]
         - Preconditions: [List any required setup]
         - Test Steps:
             1. [Step 1]
             2. [Step 2]
         - Expected Results: [What should happen]
        """

        self.prompt = PromptTemplate(
            input_variables=["requirement", "context"],
            template=self.template,
        )

        self.chain = self.prompt | self.llm

    def initialize_context(self, documents: List[str]) -> None:
        """Initialize the vector database with context documents"""
        self.embeddings_service.create_database(documents)

    def generate_test_cases(self, requirement: str) -> str:
        """Generate test cases based on the given requirement"""
        search_query = f"{requirement}"

        relevant_contexts = self.embeddings_service.similarity_search(search_query)
        context = "\n\n".join(relevant_contexts)

        return self.chain.invoke({"requirement": requirement, "context": context})
