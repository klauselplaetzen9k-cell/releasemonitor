from typing import Optional
from dataclasses import dataclass


@dataclass
class SummarizationConfig:
    """Configuration for AI summarization (optional)."""
    enabled: bool = False
    provider: str = "openai"  # openai, anthropic
    api_key: Optional[str] = None
    model: str = "gpt-3.5-turbo"
    max_length: int = 200  # Max summary length in words
    include_breaking: bool = True  # Highlight breaking changes


class AISummarizer:
    """Optional AI-powered changelog summarizer.
    
    This feature is DISABLED by default.
    Enable by setting AI_ENABLED=true and providing an API key.
    """
    
    def __init__(self, config: Optional[SummarizationConfig] = None):
        self.config = config or SummarizationConfig()
        self._client = None
    
    def is_available(self) -> bool:
        """Check if AI summarization is available."""
        if not self.config.enabled:
            return False
        if not self.config.api_key:
            return False
        return True
    
    async def summarize_changelog(
        self,
        changelog: str,
        project_name: str,
        version: str,
    ) -> dict:
        """Generate a summary of the changelog.
        
        Returns a dict with:
        - summary: Brief summary of changes
        - breaking: Breaking changes (if any)
        - features: List of new features
        - fixes: List of bug fixes
        - security: Security-related changes
        """
        if not self.is_available():
            return {
                "summary": None,
                "breaking": [],
                "features": [],
                "fixes": [],
                "security": [],
                "error": "AI summarization is not enabled"
            }
        
        # Import httpx only when needed (AI is optional)
        import httpx
        
        # For now, return a simple extraction-based summary
        # In production, this would call OpenAI/Anthropic API
        return self._extract_summary(changelog)
    
    def _extract_summary(self, changelog: str) -> dict:
        """Extract summary from changelog without AI (fallback)."""
        lines = changelog.split('\n') if changelog else []
        
        breaking = []
        features = []
        fixes = []
        security = []
        
        for line in lines:
            line_lower = line.lower()
            if 'breaking' in line_lower or '### breaking':
                breaking.append(line.strip('#- '))
            elif 'feature' in line_lower or 'feat' in line_lower:
                features.append(line.strip('#- '))
            elif 'fix' in line_lower or 'bug' in line_lower or '### fix':
                fixes.append(line.strip('#- '))
            elif 'security' in line_lower or 'cve' in line_lower or 'vulnerability' in line_lower:
                security.append(line.strip('#- '))
        
        # Create a brief summary
        summary_parts = []
        if features:
            summary_parts.append(f"{len(features)} new features")
        if fixes:
            summary_parts.append(f"{len(fixes)} bug fixes")
        if security:
            summary_parts.append(f"{len(security)} security updates")
        
        summary = "; ".join(summary_parts) if summary_parts else "See full changelog"
        
        return {
            "summary": summary,
            "breaking": breaking[:5],  # Limit to 5
            "features": features[:10],
            "fixes": fixes[:10],
            "security": security[:5],
            "error": None
        }
    
    async def generate_release_summary(
        self,
        project_name: str,
        version: str,
        changelog: str,
    ) -> str:
        """Generate a human-readable release summary."""
        data = await self.summarize_changelog(changelog, project_name, version)
        
        if data.get("error"):
            return f"**{project_name} {version}**\n\n" + changelog[:500]
        
        lines = [f"**{project_name} {version}**"]
        
        if data["breaking"]:
            lines.append("\n🚨 **Breaking Changes:**")
            for item in data["breaking"]:
                lines.append(f"- {item}")
        
        if data["features"]:
            lines.append("\n✨ **New Features:**")
            for item in data["features"][:5]:
                lines.append(f"- {item}")
        
        if data["fixes"]:
            lines.append("\n🐛 **Bug Fixes:**")
            for item in data["fixes"][:5]:
                lines.append(f"- {item}")
        
        if data["security"]:
            lines.append("\n🔒 **Security:**")
            for item in data["security"]:
                lines.append(f"- {item}")
        
        return "\n".join(lines)


# Global instance
ai_summarizer = AISummarizer()


async def summarize_release(
    project_name: str,
    version: str,
    changelog: str,
) -> str:
    """Convenience function to summarize a release."""
    return await ai_summarizer.generate_release_summary(project_name, version, changelog)
