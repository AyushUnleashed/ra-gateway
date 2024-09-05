from typing import Dict
from uuid import UUID
from src.models.base_models import Project

# Global dictionary to store projects in memory
projects_in_memory: Dict[UUID, Project] = {}