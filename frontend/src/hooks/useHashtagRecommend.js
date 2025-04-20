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
        
        const recs = await fetchRecommendations(selectedTags);
        setRecommendations(recs);
      };
      
      fetchRecs();
    }, 
    [hashtagOr, hashagAnd, hashtagNot]
);

  return recommendations;
};
