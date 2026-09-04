# ============================================================
#  SortIt — Storage Abstract Base Class (storage_interface.py)
# ============================================================

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class StorageBackend(ABC):
    """Abstract interface for storage backends (audit logs, corrections, scans)."""

    @abstractmethod
    def save_correction(self, record: Dict[str, Any]) -> None:
        """Save a user correction / override record."""
        pass

    @abstractmethod
    def get_corrections(self) -> List[Dict[str, Any]]:
        """Retrieve all recorded corrections."""
        pass
