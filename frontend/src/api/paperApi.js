const API_URL = import.meta.env.VITE_API_URL;

export const searchPapers = async ({ query, must, should, must_not, size = 20 }) => {
    const res = await fetch(`${API_URL}/api/v1/papers/search`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, must, should, must_not, size }),
    });
  
    if (!res.ok) throw new Error("Failed to fetch papers");
  
    return await res.json();
  };
  