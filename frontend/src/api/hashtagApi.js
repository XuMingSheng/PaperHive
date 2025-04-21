const API_URL = import.meta.env.VITE_API_URL;

export const fetchHashtag = async (tag) => {
    const res = await fetch(
      `${API_URL}/api/v1/hashtags/${tag}`
    )
    
    if (!res.ok) throw new Error("Failed to fetch tag");
    
    return await res.json()
}; 


export const fetchAutocomplete = async (input) => {
    if (!input) return [];
  
    const res = await fetch(
      `${API_URL}/api/v1/hashtags/search_name?query=${encodeURIComponent(input)}`
    );
  
    if (!res.ok) throw new Error("Failed to fetch suggestions");
  
    const suggestions = await res.json();
    return suggestions.map((s) => s.name);
};


export const fetchRecommendations = async (selectedTags) => {
  const res = await fetch(`${API_URL}/api/v1/hashtags/recommend`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(selectedTags),
  });

  if (!res.ok) throw new Error("Failed to fetch hashtag recommendations");

  return await res.json();
};


export const fetchGraph = async (tags) => {
  const res = await fetch(`${API_URL}/api/v1/hashtags/graph`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(tags)
  });

  if (!res.ok) throw new Error("Failed to fetch hashtag graph");
  
  return await res.json();
};
