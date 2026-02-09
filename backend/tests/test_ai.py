import pytest
from app.services.ai_summarizer import AISummarizer, SummarizationConfig

class TestAISummarizer:
    """Test AI summarizer (disabled by default)."""
    
    def test_ai_disabled_by_default(self):
        """Test that AI is disabled by default."""
        config = SummarizationConfig()
        summarizer = AISummarizer(config)
        
        assert summarizer.is_available() is False
    
    def test_extract_summary_without_ai(self):
        """Test fallback summary extraction."""
        config = SummarizationConfig(enabled=False)
        summarizer = AISummarizer(config)
        
        changelog = """
# Features
- Added new user authentication
- Added dark mode support

# Bug Fixes
- Fixed memory leak in worker
- Fixed login timeout issue

# Security
- Updated dependencies to fix CVE-2024-1234
"""
        result = summarizer._extract_summary(changelog)
        
        assert result["summary"] == "2 new features; 2 bug fixes; 1 security updates"
        assert len(result["features"]) == 2
        assert len(result["fixes"]) == 2
        assert len(result["security"]) == 1
        assert result["error"] is None
    
    def test_generate_release_summary_without_ai(self):
        """Test release summary without AI."""
        config = SummarizationConfig(enabled=False)
        summarizer = AISummarizer(config)
        
        summary = summarizer._extract_summary("## Fixes\n- Fixed bug")
        
        result = summarizer.generate_release_summary(
            "TestProject",
            "1.0.0",
            "## Fixes\n- Fixed bug"
        )
        
        assert "TestProject 1.0.0" in result
        assert "Bug Fixes" in result


class TestSummarizationConfig:
    """Test configuration."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = SummarizationConfig()
        
        assert config.enabled is False
        assert config.provider == "openai"
        assert config.model == "gpt-3.5-turbo"
        assert config.max_length == 200
        assert config.include_breaking is True
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = SummarizationConfig(
            enabled=True,
            api_key="test-key",
            model="gpt-4",
            max_length=500,
        )
        
        assert config.enabled is True
        assert config.api_key == "test-key"
        assert config.model == "gpt-4"
        assert config.max_length == 500
