import React, { useState, useEffect } from "react";
import { Container, Typography, Button, CssBaseline, CircularProgress, TextField, Box, Grid} from "@mui/material";
import { ThemeProvider, createTheme } from "@mui/material/styles";

import HashtagZone from "../components/HashtagZone";
import HashtagRecommend from "../components/HashtagRecommend";
import PaperResult from "../components/PaperResult";
import { searchPapers } from "../api/paperApi";
import { fetchRecommendations  } from "../api/hashtagApi";

const darkTheme = createTheme({
  palette: { mode: "dark" }
});

const SearchPage = () => {
  const [hashtagOr, setHashtagOr] = useState([]);
  const [hashtagAnd, setHashtagAnd] = useState([]);
  const [hashtagNot, setHashtagNot] = useState([]);

  const [recommendations, setRecommendations] = useState([]);

  const [query, setQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false)

  useEffect(
    () => {
      const fetchRecs = async () => {
        const selectedTags = Array.from(new Set([...hashtagOr, ...hashtagAnd, ...hashtagNot]));
        
        if (selectedTags.length == 0) {
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
    [hashtagOr, hashtagAnd, hashtagNot]
  );

  const handleSearch = async () => {
    setLoading(true)
    setHasSearched(true)

    try {
      const result = await searchPapers({
        query: query,
        must: hashtagOr,
        should: hashtagAnd,
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
      <Container maxWidth="md" sx={{ pt: 4, pb: 6 }}>
        <Typography variant="h4" align="center" gutterBottom>
          Hashtag-Based Paper Search
        </Typography>

        <Grid container spacing={4}>
          <Grid item xs={12} md={8}>
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
          </Grid>
          <Grid item xs={12} md={4}>
              <HashtagRecommend recommendations={recommendations} />
          </Grid>
        </Grid>
      </Container>
    </ThemeProvider>
  );
};

export default SearchPage;