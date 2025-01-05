from langchain_core.prompts import PromptTemplate
from langchain_google_vertexai import VertexAI


class TestCaseGenerator:
    def __init__(self):
        self.llm = VertexAI(
            model_name="gemini-pro",
        )

        self.template = """
        Based on the following requirement and acceptance criteria, generate detailed test cases:
        
        Requirement: {requirement}
        Acceptance Criteria: {acceptance_criteria}
        
        Generate test cases in the following format:
        - Test Case ID
        - Description
        - Pre-conditions
        - Steps
        - Expected Results
        """

        self.prompt = PromptTemplate(
            input_variables=["requirement", "acceptance_criteria"],
            template=self.template,
        )

        self.chain = self.prompt | self.llm

    def generate_test_cases(self, requirement, acceptance_criteria):
        return self.chain.invoke(
            {"requirement": requirement, "acceptance_criteria": acceptance_criteria}
        )
