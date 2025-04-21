import React, { useState } from "react";
import { Typography, Button, CssBaseline, CircularProgress, TextField, Box, InputAdornment, IconButton} from "@mui/material";
import UploadFileIcon from '@mui/icons-material/UploadFile';

import { ThemeProvider, createTheme } from "@mui/material/styles";

import HashtagZone from "../components/HashtagZone";
import HashtagRecommend from "../components/HashtagRecommend";
import HashtagGraph from "../components/HashtagGraph";
import PaperResult from "../components/PaperResult";
import { searchPapers } from "../api/paperApi";
import { useSearchContext  } from "../context/SearchContext"
import { useHashtagRecommend } from "../hooks/useHashtagRecommend";
import { parsePdf } from "../api/pdfApi";

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

  const [pdfFile, setPdfFile] = useState(null);

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
      {/* Title center block */}
      <Typography
        variant="h4"
        gutterBottom
        sx={{ textAlign: 'center', mt: 4 }}
      >
        Hashtag-Based Paper Search
      </Typography>

      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          width: '100%',
          minHeight: '100vh',
          px: 2,
          py: 6,
        }}
      >

        {/* Centered dynamic content wrapper */}
        <Box
          sx={{
            display: 'flex',
            alignItems: 'flex-start',
            width: '100%',
            maxWidth: '1200px',
            flexDirection: {
              xs: 'column', // stack on small screens
              md: 'row',
            },
            gap: 4,
          }}
        >
          {/* Left: Search panel */}
          <Box 
             sx={{
              width: {
                xs: '100%',
                md: hasSearched ? 'calc(100% - 340px)' : '100%', // account for right panel
              },
              maxWidth: '900px',
              flexGrow: 1,
            }}
          >
            {/* Search content */}
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

          {/* Right: Graph & Recommendation panel */}
          <Box
            sx={{
              width: {
                xs: "100%",  // full width on mobile
                md: "300px", // fixed on desktop
              },
              position: {
                xs: "relative",
                md: "sticky",
              },
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
      </Box>
    </ThemeProvider>
  );
};

export default SearchPage;