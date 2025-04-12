import { useState, useEffect } from 'react';
import { fetchRecommendations } from '../api/hashtagApi';

export const useHashtagRecommend = (hashtagOr, hashagAnd, hashtagNot) => {
  const [recommendations, setRecommendations] = useState([]);

  useEffect(
    () => {
      const fetchRecs = async () => {
        const selectedTags = Array.from(new Set([...hashtagOr, ...hashagAnd, ...hashtagNot]));
        
        if (selectedTags.length === 0) {
          setRecommendations([]);
          return;
        }
        
        try {
          const recs = await fetchRecommendations(selectedTags);
          setRecommendations(recs);
        } catch(err) {
          console.error("Failed to fetch recommendations:", err);
        }
      };
      
      fetchRecs();
    }, 
    [hashtagOr, hashagAnd, hashtagNot]
);

  return recommendations;
};
