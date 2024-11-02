from typing import Dict
from uuid import UUID
from src.models.base_models import Project
from cachetools import LRUCache

# Use LRUCache to store projects in memory with a maximum size of 50
projects_in_memory: Dict[UUID, Project] = LRUCache(maxsize=100)