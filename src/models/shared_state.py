from typing import Dict
from uuid import UUID
from src.models.base_models import Project
from cachetools import LRUCache
from src.workflow.wrokflow_utils import delete_working_directory
import asyncio

class ProjectLRUCache(LRUCache):
    """LRU Cache for projects with automatic file cleanup on removal."""

    def _cleanup_project(self, key: UUID):
        """Delete project working directory asynchronously."""
        delete_working_directory(str(key))

    def __delitem__(self, key):
        """Override delete to cleanup project files before removal."""
        try:
            self._cleanup_project(key)
        except Exception as e:
            # Log the error but don't prevent cache operation
            print(f"Warning: Failed to cleanup project {key}: {e}")
        finally:
            # Always perform the original delete operation
            super().__delitem__(key)

    def popitem(self):
        """Override popitem to cleanup project files before removal."""
        # Get the key that will be removed (LRU item)
        # In cachetools LRUCache, it's the first key in the internal dictionary
        if not self:
            raise KeyError('Cache is empty')

        key = next(iter(self))
        try:
            self._cleanup_project(key)
        except Exception as e:
            print(f"Warning: Failed to cleanup project {key}: {e}")

        # Perform the original popitem operation
        return super().popitem()

# Usage
projects_in_memory: Dict[UUID, Project] = ProjectLRUCache(maxsize=30)