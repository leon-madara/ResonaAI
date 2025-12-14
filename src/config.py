"""Public config surface for shared voice pipeline code.

Re-exports the backend core settings so imports remain stable as `src.config`.
"""

from apps.backend.core.config import settings

__all__ = ["settings"]
