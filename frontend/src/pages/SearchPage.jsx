import React, { useState, useEffect } from "react";
import { Container, Typography, Button, CssBaseline, CircularProgress, TextField, Box, InputAdornment, IconButton} from "@mui/material";
import UploadFileIcon from '@mui/icons-material/UploadFile';

import { ThemeProvider, createTheme } from "@mui/material/styles";

import HashtagZone from "../components/HashtagZone";
import HashtagRecommend from "../components/HashtagRecommend";
import PaperResult from "../components/PaperResult";
import { searchPapers } from "../api/paperApi";
import { fetchRecommendations  } from "../api/hashtagApi";
import { parsePdf } from "../api/pdfApi";

const darkTheme = createTheme({
  palette: { mode: "dark" }
});

const SearchPage = () => {
  const [hashtagOr, setHashtagOr] = useState([]);
  const [hashtagAnd, setHashtagAnd] = useState([]);
  const [hashtagNot, setHashtagNot] = useState([]);

  const [recommendations, setRecommendations] = useState([]);

  const [query, setQuery] = useState("");
  const [pdfFile, setPdfFile] = useState(null);
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

  const handlePdfUpload = async (event) => {
    const file = event.target.files[0];
    if (!file || file.type !== "application/pdf") {
      alert("Please upload a valid PDF file.");
      return;
    }

    try {
        const praseResult = await parsePdf(file); // praseResult = { title, hashtags }
        console.log(praseResult);
        setQuery(praseResult.title);
        setHashtagOr(praseResult.hashtags);
    } catch(err) {
        console.error("Failed to upload PDF:", err);
    }

    setPdfFile(file);
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Container maxWidth="xl" sx={{ pt: 4, pb: 6 }}>
        <Typography variant="h4" align="center" gutterBottom>
          Hashtag-Based Paper Search
        </Typography>

        <Box sx={{ display: 'flex', gap: 4, alignItems: 'flex-start' }}>
          <Box sx={{ flex: 1 }}>
            
            <Box mb={3}>
              <Typography variant="h6">Query</Typography>
              <TextField
                fullWidth
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                variant="outlined"
                placeholder="Enter your query or upload a PDF"
                InputProps={{     
                    endAdornment: (
                      <InputAdornment position="end">  
                        <IconButton component="label"> 
                          <UploadFileIcon />           
                          <input                      
                            type="file"
                            hidden
                            accept="application/pdf"
                            onChange={handlePdfUpload}
                          />
                        </IconButton>
                      </InputAdornment>
                    )
                  }}
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
          <Box
            sx={{
              width: '300px',
              position: 'sticky',
              top: '20px',
              alignSelf: 'flex-start',
              flexShrink: 0,
              maxHeight: '80vh',
              overflowY: 'auto',
              pr: 1  // optional: add right padding to avoid scroll bar overlay
            }}
          >
            <HashtagRecommend recommendations={recommendations} />
          </Box>
          
        </Box>
      </Container>
    </ThemeProvider>
  );
};

export default SearchPage;