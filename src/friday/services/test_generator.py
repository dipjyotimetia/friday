from typing import List, Literal

from langchain_core.prompts import PromptTemplate
from langchain_google_vertexai import VertexAI
from langchain_openai import ChatOpenAI

from friday.services.embeddings import EmbeddingsService

ModelProvider = Literal["vertex", "openai"]


class TestCaseGenerator:
    def __init__(self, provider: ModelProvider = "vertex"):
        if provider == "vertex":
            self.llm = VertexAI(
                model_name="gemini-pro",
            )
        elif provider == "openai":
            self.llm = ChatOpenAI(
                model_name="gpt-4-turbo-preview",
                temperature=0,
                max_tokens=1024,
                timeout=None,
                max_retries=2,
            )
        # For OpenAI embeddings
        # self.embeddings_service = EmbeddingsService(provider="openai")
        self.embeddings_service = EmbeddingsService()
        self.template = """
        Based on the following requirements, generate detailed test cases:
        
        Requirement: {requirement}
        
        Related Context:
        {context}
        
        Generate test cases in the following format:
         - Test Case ID
         - Title: [Brief description]
         - Description
         - Preconditions: [List any required setup]
        Test Steps:
         1. [Step 1]
         2. [Step 2]
        Expected Results:  [What should happen]
        
        Consider:
        - Boundary conditions
        - Data validation scenarios
        - System state variations
        - Integration points
        - Performance conditions
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
