from langchain_core.prompts import PromptTemplate
from langchain_google_vertexai import VertexAI


class TestCaseGenerator:
    def __init__(self):
        self.llm = VertexAI(
            model_name="gemini-pro",
        )

        self.template = """
        Based on the following requirements, generate detailed test cases:
        
        Requirement: {requirement}
        
        Generate test cases in the following format:
        - Test Case ID
        - Description
        - Pre-conditions
        - Test Steps
        - Expected Results
        """

        self.prompt = PromptTemplate(
            input_variables=["requirement"],
            template=self.template,
        )

        self.chain = self.prompt | self.llm

    def generate_test_cases(self, requirement, acceptance_criteria):
        return self.chain.invoke({"requirement": requirement})
