import React, { useState } from "react";

function App() {
  const [query, setQuery] = useState("");
  const [hashtag, setHashtag] = useState("");
  const [results, setResults] = useState([]);

  const handleSearch = async () => {
    try {
      const params = new URLSearchParams({
        query: query,
        hashtag: hashtag
      });
      const response = await fetch(`http://localhost:8000/search/?${params}`);
      const data = await response.json();
      setResults(data.results);
    } catch (error) {
      console.error("Error fetching search results:", error);
    }
  };

  return (
    <div style={{ margin: "2rem" }}>
      <h1>Hashtag-Based Paper Search</h1>
      <div>
        <label>Query: </label>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>
      <div>
        <label>Hashtag (optional): </label>
        <input
          type="text"
          value={hashtag}
          onChange={(e) => setHashtag(e.target.value)}
        />
      </div>
      <button onClick={handleSearch}>Search</button>

      <h2>Results</h2>
      <ul>
        {results.map((paper) => (
          <li key={paper.id}>
            <strong>{paper.title}</strong>
            <p>{paper.abstract}</p>
            <em>Hashtags: {paper.hashtags.join(", ")}</em>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;