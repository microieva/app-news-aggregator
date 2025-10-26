import re
from typing import List, Dict, Optional
from collections import defaultdict
from app.core.config import settings

class TopicMatcher:
    def __init__(self):
        self.topic_keywords = settings.TOPIC_KEYWORDS
        
        self.keyword_to_topic = {}
        for topic, keywords in self.topic_keywords.items():
            for keyword in keywords:
                self.keyword_to_topic[keyword.lower()] = topic
    
    async def analyze_content_for_topics(self, title: str, content: str, min_confidence: float = 0.3) -> List[Dict]:
        """
        Analyze both title and content to find relevant topics
        
        Returns:
            List of topics with confidence scores
        """
        full_text = f"{title} {content}".lower()
        topic_scores = defaultdict(int)
        total_matches = 0
        
        for keyword, topic in self.keyword_to_topic.items():
            # Use regex for whole word matching to avoid partial matches
            pattern = r'\b' + re.escape(keyword) + r'\b'
            matches = len(re.findall(pattern, full_text))
            
            if matches > 0:
                topic_scores[topic] += matches
                total_matches += matches
        
        if total_matches == 0:
            return []
        
        # Calculate confidence scores
        results = []
        for topic, score in topic_scores.items():
            confidence = score / total_matches
            if confidence >= min_confidence:
                results.append({
                    "topic": topic,
                    "confidence": confidence,
                    "matches": score
                })
        
        # Sort by confidence (highest first)
        results.sort(key=lambda x: x["confidence"], reverse=True)
        
        return results
    
    async def get_primary_topic(self, title: str, content: str, min_confidence: float = 0.3) -> Optional[str]:
        """Get the most relevant topic for the content"""
        topics = await self.analyze_content_for_topics(title, content, min_confidence)

        if not topics:
            return "other"
        else:
            return topics[0]["topic"]
    

    async def expand_search_queries(self, base_topic: str) -> List[str]:
        """Expand a topic into multiple search queries"""
        base_queries = [base_topic]
        
        if base_topic in self.topic_keywords:
            related_keywords = list(self.topic_keywords[base_topic])[:3]  # Take top 3 related keywords
            base_queries.extend(related_keywords)
        
        return base_queries
    
topic_matcher = TopicMatcher()