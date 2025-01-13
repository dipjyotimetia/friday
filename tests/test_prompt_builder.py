from typing import Dict

import pytest

from friday.services.prompt_builder import PromptBuilder, PromptTemplate


@pytest.fixture
def prompt_builder() -> PromptBuilder:
    """Fixture to create a fresh PromptBuilder instance for each test"""
    return PromptBuilder()


@pytest.fixture
def sample_variables() -> Dict:
    """Fixture providing sample variables for template testing"""
    return {
        "story_description": "User authentication feature",
        "confluence_content": "Implement OAuth2 flow",
        "unique_id": "001",
        "feature_description": "Login system",
        "technical_details": "REST API implementation",
        "system_description": "Web application",
        "security_requirements": "OWASP compliance",
        "performance_requirements": "Response time < 200ms",
    }


class TestPromptBuilder:
    def test_prompt_template_dataclass(self):
        """Test PromptTemplate dataclass initialization and attributes"""
        template = PromptTemplate(version="1.0", template="Test template")
        assert template.version == "1.0"
        assert template.template == "Test template"

    def test_init_default_templates(self, prompt_builder):
        """Test initialization of default templates"""
        expected_templates = [
            "test_case",
            "edge_case",
            "exploratory_testing",
            "security_testing",
            "performance_testing",
        ]

        for template_key in expected_templates:
            assert template_key in prompt_builder.templates
            assert isinstance(prompt_builder.templates[template_key], PromptTemplate)
            assert prompt_builder.templates[template_key].version == "1.0"

    def test_build_prompt_with_string_variables(self, prompt_builder, sample_variables):
        """Test building prompt with string variables"""
        result = prompt_builder.build_prompt("test_case", sample_variables)

        # Verify variables were replaced
        assert "{story_description}" not in result
        assert sample_variables["story_description"] in result
        assert sample_variables["confluence_content"] in result

        # Verify template structure is maintained
        assert "System: You are a Quality Enginner" in result
        assert "Test ID: TC-" in result

    def test_build_prompt_with_list_variables(self, prompt_builder):
        """Test building prompt with list variables"""
        variables = {
            "items": ["First item", "Second item", "Third item"],
            "text": "Sample text",
        }

        # Add a custom template for testing lists
        prompt_builder.add_custom_template(
            "list_template", "Items:\n{items}\nText: {text}"
        )

        result = prompt_builder.build_prompt("list_template", variables)

        # Verify list formatting
        assert "• First item" in result
        assert "• Second item" in result
        assert "• Third item" in result
        assert "Sample text" in result

    def test_invalid_template_key(self, prompt_builder, sample_variables):
        """Test error handling for invalid template key"""
        with pytest.raises(ValueError, match="Template 'invalid_key' not found"):
            prompt_builder.build_prompt("invalid_key", sample_variables)

    def test_get_template_version(self, prompt_builder):
        """Test getting template version"""
        version = prompt_builder.get_template_version("test_case")
        assert version == "1.0"

        with pytest.raises(ValueError, match="Template 'invalid_key' not found"):
            prompt_builder.get_template_version("invalid_key")

    def test_add_custom_template(self, prompt_builder):
        """Test adding and using custom template"""
        custom_template = "Custom template with {variable}"
        prompt_builder.add_custom_template("custom", custom_template, version="2.0")

        # Verify template was added
        assert "custom" in prompt_builder.templates
        assert prompt_builder.templates["custom"].template == custom_template
        assert prompt_builder.templates["custom"].version == "2.0"

        # Test using the custom template
        result = prompt_builder.build_prompt("custom", {"variable": "test value"})
        assert result == "Custom template with test value"

    def test_build_prompt_edge_case(self, prompt_builder):
        """Test building prompts with edge cases"""
        edge_cases = {
            "empty_string": "",
            "special_chars": "!@#$%^&*()",
            "numbers": "12345",
            "multiline": "Line 1\nLine 2\nLine 3",
        }

        prompt_builder.add_custom_template(
            "edge_case_template",
            "Values:\n{empty_string}\n{special_chars}\n{numbers}\n{multiline}",
        )

        result = prompt_builder.build_prompt("edge_case_template", edge_cases)

        # Verify edge cases are handled
        assert edge_cases["special_chars"] in result
        assert edge_cases["numbers"] in result
        assert edge_cases["multiline"] in result

    def test_template_content_structure(self, prompt_builder, sample_variables):
        """Test the structure of specific template types"""
        # Test edge case template
        edge_case_result = prompt_builder.build_prompt("edge_case", sample_variables)
        assert "Analyze the following feature" in edge_case_result
        assert "Boundary conditions" in edge_case_result

        # Test security testing template
        security_result = prompt_builder.build_prompt(
            "security_testing", sample_variables
        )
        assert "Security Tester" in security_result
        assert "Identify security vulnerabilities" in security_result

        # Test performance testing template
        performance_result = prompt_builder.build_prompt(
            "performance_testing", sample_variables
        )
        assert "Performance Test Engineer" in performance_result
        assert "Measure system response times" in performance_result

    def test_missing_variables(self, prompt_builder):
        """Test handling of missing template variables"""
        incomplete_variables = {
            "story_description": "Test story"
            # Missing other required variables
        }

        result = prompt_builder.build_prompt("test_case", incomplete_variables)

        # Variables that weren't provided should remain as template placeholders
        assert "{confluence_content}" in result
        assert "{unique_id}" in result
        assert "Test story" in result

    def test_additional_variables(self, prompt_builder):
        """Test handling of additional unused variables"""
        variables_with_extra = {
            **sample_variables,
            "extra_var": "This should be ignored",
        }

        result = prompt_builder.build_prompt("test_case", variables_with_extra)

        # Extra variables should not affect the result
        assert "This should be ignored" not in result
        assert sample_variables["story_description"] in result

    def test_template_immutability(self, prompt_builder, sample_variables):
        """Test that original templates are not modified after use"""
        original_template = prompt_builder.templates["test_case"].template
        prompt_builder.build_prompt("test_case", sample_variables)

        # Verify template wasn't modified
        assert prompt_builder.templates["test_case"].template == original_template
        assert "{story_description}" in prompt_builder.templates["test_case"].template
