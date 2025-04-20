import React, { useState, useEffect } from "react";
import { Container, Typography, Button, CssBaseline, CircularProgress, TextField, Box, Grid} from "@mui/material";
import { ThemeProvider, createTheme } from "@mui/material/styles";

import HashtagZone from "../components/HashtagZone";
import HashtagRecommend from "../components/HashtagRecommend";
import HashtagGraph from "../components/HashtagGraph";
import PaperResult from "../components/PaperResult";
import { searchPapers } from "../api/paperApi";
import { useSearchContext  } from "../context/SearchContext"
import { useHashtagRecommend } from "../hooks/useHashtagRecommend";

const darkTheme = createTheme({
  palette: { mode: "dark" }
});

const SearchPage = () => {
  const { 
    hashtagOr, setHashtagOr, 
    hashtagAnd, setHashtagAnd,
    hashtagNot, setHashtagNot,
    query, setQuery
  } = useSearchContext()
  
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false)

  const selectedTags = Array.from(new Set([...hashtagOr, ...hashtagAnd, ...hashtagNot]));
  const recommendations = useHashtagRecommend(hashtagOr, hashtagAnd, hashtagNot)

  const handleSearch = async () => {
    setLoading(true)
    setHasSearched(true)

    try {
      const result = await searchPapers({
        query: query,
        must: hashtagAnd,
        should: hashtagOr,
        must_not: hashtagNot,
      });
      setSearchResults(result);
    } catch (error) {
      console.error("Search failed:", error);
      setSearchResults([])
    } finally {
      setLoading(false)
    }
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Container maxWidth="xl" sx={{ pt: 4, pb: 6 }}>
        <Typography variant="h4" align="center" gutterBottom>
          Hashtag-Based Paper Search
        </Typography>

        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'center',  
          alignItems: 'flex-start',
          gap: 4,
          px: 2,
          pt: 6,
        }}>
          {/* Left: Search panel */}
          <Box sx={{ flex: 1, maxWidth: '900px' }}>
            {/* Search content */}
            <Box mb={3}>
              <Typography variant="h6">Query</Typography>
              <TextField
                fullWidth
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                variant="outlined"
                placeholder="Enter your query"
              />
            </Box>

            <HashtagZone title="OR" items={hashtagOr} setItems={setHashtagOr} />
            <HashtagZone title="AND" items={hashtagAnd} setItems={setHashtagAnd} />
            <HashtagZone title="NOT" items={hashtagNot} setItems={setHashtagNot} />

            <Button 
              variant="contained" 
              color="primary" 
              fullWidth 
              sx={{ mt: 2 }} 
              onClick={handleSearch}
              disable={loading}
            >
              {loading ? 'Searching...' : 'Search'}
            </Button>
            
            <Box mt={4}>
              {loading && (
                <Box display="flex" justifyContent="center" mt={2}>
                  <CircularProgress />
                </Box>
              )}
              
              {!loading && hasSearched && searchResults.length === 0 && (
                <Typography variant="body1" align="center">
                  No results found.
                </Typography>
              )}

              {!loading && searchResults.length > 0 && (
                searchResults.map((paper) => <PaperResult key={paper.id} paper={paper} />)
              )}
            </Box>
          </Box>
              
          {/* Right: Recommendation panel */}
          <Box
            sx={{
              width: '300px',
              position: 'sticky',
              top: '20px',
              alignSelf: 'flex-start',
              flexShrink: 0,
              maxHeight: '85vh',
              overflowY: 'auto',
              pr: 1  // optional: add right padding to avoid scroll bar overlay
            }}
          > 
            {/* Graph Visualization */}
            {selectedTags.length > 0 && (
              <>
                <Typography variant="subtitle1" sx={{ mt: 2 }}>
                  Tag Graph (Steps = 2)
                </Typography>
                <HashtagGraph tags={selectedTags} steps={2} />
              </>
            )}
           
            <HashtagRecommend recommendations={recommendations} />
          </Box>
        </Box>
      </Container>
    </ThemeProvider>
  );
};

export default SearchPage;