from app.services.sources.base import Release, ReleaseSource
from app.services.sources.github import GitHubSource
from app.services.sources.npm import npmSource
from app.services.sources.pypi import PyPISource

# Map source names to source classes
SOURCE_CLASSES = {
    "github": GitHubSource,
    "npm": npmSource,
    "pypi": PyPISource,
}


def get_source(source_name: str) -> ReleaseSource:
    """Factory function to get a release source instance."""
    source_class = SOURCE_CLASSES.get(source_name.lower())
    if not source_class:
        raise ValueError(f"Unknown release source: {source_name}")
    return source_class()


__all__ = [
    "Release",
    "ReleaseSource", 
    "GitHubSource",
    "npmSource",
    "PyPISource",
    "get_source",
    "SOURCE_CLASSES",
]
