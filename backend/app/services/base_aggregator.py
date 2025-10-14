from abc import ABC, abstractmethod
from typing import List, Dict

class BaseAggregator(ABC):
    """Base class for all content aggregators"""
    
    @abstractmethod
    async def fetch_articles(self, topic: str, limit: int = 10) -> List[Dict]:
        """Fetch articles for a given topic"""
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        """Return the name of this aggregator source"""
        pass