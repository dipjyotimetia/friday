from dataclasses import dataclass
from typing import Dict, List, Union


@dataclass
class PromptTemplate:
    version: str
    template: str


class PromptBuilder:
    def __init__(self):
        self.templates = {
            "test_case": PromptTemplate(
                version="1.0",
                template="""
                System: You are a Quality Enginner who specializes in creating comprehensive test scenarios.
                
                Input:
                JIRA Story: {story_description}
                Additional Context: {confluence_content}
                
                Instructions:
                1. Generate detailed test cases following this structure:
                2. Include all specified test types
                3. Ensure each test case has clear steps
                4. Prioritize based on business impact
                
                Format each test case as follows:
                Test ID: TC-{unique_id}
                Title: [Brief description]
                Preconditions: [List any required setup]
                Test Steps:
                1. [Step 1]
                2. [Step 2]
                Expected Results: [What should happen]
                Test Type: [Functional/Integration/Edge Case]
                Priority: [High/Medium/Low]
                
                Output the test cases in a structured format that can be imported into a test management system.
                """,
            ),
            "edge_case": PromptTemplate(
                version="1.0",
                template="""
                Analyze the following feature and identify potential edge cases:
                
                Feature Description: {feature_description}
                Technical Implementation: {technical_details}
                
                Consider:
                - Boundary conditions
                - Data validation scenarios
                - System state variations
                - Integration points
                - Performance conditions
                """,
            ),
            "exploratory_testing": PromptTemplate(
                version="1.0",
                template="""
                System: You are a User Acceptance Tester responsible for exploratory testing.
                
                Feature Description: {feature_description}
                Technical Implementation: {technical_details}
                
                Approach:
                - Identify test scenarios based on feature functionality
                - Execute test cases manually
                - Document defects and observations
                - Provide feedback on usability and user experience
                """,
            ),
            "security_testing": PromptTemplate(
                version="1.0",
                template="""
                System: You are a Security Tester responsible for conducting security testing.
                
                System Description: {system_description}
                Security Requirements: {security_requirements}
                
                Objectives:
                - Identify security vulnerabilities
                """,
            ),
            "performance_testing": PromptTemplate(
                version="1.0",
                template="""
                System: You are a Performance Test Engineer responsible for conducting performance testing.
                
                System Description: {system_description}
                Performance Requirements: {performance_requirements}
                
                Objectives:
                - Identify performance bottlenecks
                - Measure system response times
                - Analyze system resource utilization
                """,
            ),
        }

    def build_prompt(
        self,
        template_key: str,
        variables: Dict[str, Union[str, List[str]]],
    ) -> str:
        """
        Builds a prompt using the specified template and variables.
        Supports both string and list variables.

        Args:
            template_key: Key identifying the template to use
            variables: Dictionary of variables to insert into template
                    Values can be strings or lists of strings

        Returns:
            Formatted prompt string with variables replaced

        Example:
            variables = {
                "items": ["item1", "item2"],
                "text": "some text"
            }
        """
        if template_key not in self.templates:
            raise ValueError(f"Template '{template_key}' not found")

        template = self.templates[template_key].template

        # Replace variables in template
        for key, value in variables.items():
            if isinstance(value, list):
                # Convert list to bullet points
                formatted_value = "\n".join(f"• {item}" for item in value)
            else:
                formatted_value = str(value)
            template = template.replace(f"{{{key}}}", formatted_value)

        return template.strip()

    def get_template_version(self, template_key: str) -> str:
        """
        Returns the version of the specified template
        """
        return self.templates[template_key].version

    def add_custom_template(
        self, key: str, template: str, version: str = "1.0"
    ) -> None:
        """
        Adds a custom template to the prompt builder
        """
        self.templates[key] = PromptTemplate(version=version, template=template)
