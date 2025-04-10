import React, { useState, useEffect } from "react";
import {
  Container,
  Typography,
  TextField,
  Autocomplete,
  Chip,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Box
} from "@mui/material";

function App() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [tableData, setTableData] = useState({ columns: [], rows: [] });
  const [queryDict, setQueryDict] = useState([]);
  const [hashtagDict, setHashtagDict] = useState([]);

  const [hashtagOr, setHashtagOr] = useState([]);
  const [hashtagAnd, setHashtagAnd] = useState([]);
  const [hashtagNot, setHashtagNot] = useState([]);

  const [pdfFile, setPdfFile] = useState(null);

  useEffect(() => {
    fetch("/query_keywords.json")
      .then((res) => res.json())
      .then((data) => setQueryDict(data))
      .catch((err) => console.error("Failed to load query dictionary:", err));

    fetch("/hashtag_keywords.json")
      .then((res) => res.json())
      .then((data) => setHashtagDict(data))
      .catch((err) => console.error("Failed to load hashtag dictionary:", err));
  }, []);

  const handleSearch = async () => {
    console.log("Searching...");

    try {
      const params = new URLSearchParams({
        query,
        or: hashtagOr.join(","),
        and: hashtagAnd.join(","),
        not: hashtagNot.join(",")
      });

      const response = await fetch(`http://localhost:8000/search/?${params}`);
      const data = await response.json();

      console.log("✅ results:", data.results);
      console.log("✅ count:", data.results.length);

      setResults(data.results || []);
      setTableData(data.table || { columns: [], rows: [] });
    } catch (error) {
      console.error("Error fetching search results:", error);
    }
  };

  const uploadPdfToBackend = async (file) => {
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/upload-pdf/", {
        method: "POST",
        body: formData
      });
      const result = await response.json();
      console.log("✅ Uploaded PDF result:", result);
      alert("PDF uploaded successfully!");
    } catch (err) {
      console.error("❌ Error uploading PDF:", err);
      alert("Failed to upload PDF.");
    }
  };

  const handlePdfUpload = (event) => {
    const file = event.target.files[0];
    if (file && file.type === "application/pdf") {
      setPdfFile(file);
      console.log("📄 PDF selected:", file.name);
      uploadPdfToBackend(file);
    } else {
      setPdfFile(null);
      alert("Please upload a valid PDF file.");
    }
  };

  const handleCategoryChange = (categorySetter, value, other1, other2, other1Setter, other2Setter) => {
    const cleanValue = [...new Set(value)];
    const newOther1 = other1.filter((tag) => !cleanValue.includes(tag));
    const newOther2 = other2.filter((tag) => !cleanValue.includes(tag));

    categorySetter(cleanValue);
    other1Setter(newOther1);
    other2Setter(newOther2);
  };

  const renderHashtagInput = (label, value, setter, other1, other2, other1Setter, other2Setter) => {
    const filteredOptions = hashtagDict.filter(
      (tag) => !other1.includes(tag) && !other2.includes(tag)
    );

    return (
      <Box mb={3}>
        <Typography variant="h6" gutterBottom>{label}</Typography>
        <Autocomplete
          multiple
          freeSolo
          options={filteredOptions}
          value={value}
          onChange={(event, newValue) => handleCategoryChange(setter, newValue, other1, other2, other1Setter, other2Setter)}
          renderTags={(value, getTagProps) =>
            value.map((option, index) => (
              <Chip
                variant="outlined"
                label={option}
                {...getTagProps({ index })}
                key={option}
              />
            ))
          }
          renderInput={(params) => (
            <TextField {...params} placeholder="Add hashtags" variant="outlined" fullWidth />
          )}
        />
      </Box>
    );
  };

  return (
    <Container maxWidth="md" sx={{ pt: 4, pb: 6 }}>
      <Typography variant="h4" align="center" gutterBottom>
        Hashtag-Based Paper Search
      </Typography>

      <Box mb={4}>
        <Typography variant="h6" gutterBottom>Query</Typography>
        <TextField
          fullWidth
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter your query"
          variant="outlined"
        />
      </Box>

      {renderHashtagInput("Hashtag OR", hashtagOr, setHashtagOr, hashtagAnd, hashtagNot, setHashtagAnd, setHashtagNot)}
      {renderHashtagInput("Hashtag AND", hashtagAnd, setHashtagAnd, hashtagOr, hashtagNot, setHashtagOr, setHashtagNot)}
      {renderHashtagInput("Hashtag NOT", hashtagNot, setHashtagNot, hashtagOr, hashtagAnd, setHashtagOr, setHashtagAnd)}

      <Box mb={3}>
        <Typography variant="h6" gutterBottom>Upload PDF (optional)</Typography>
        <Button variant="outlined" component="label">
          Upload PDF
          <input type="file" hidden accept="application/pdf" onChange={handlePdfUpload} />
        </Button>
        {pdfFile && (
          <Typography variant="body2" style={{ marginTop: "0.5rem" }}>
            Selected: {pdfFile.name}
          </Typography>
        )}
      </Box>

      <Box textAlign="center" mb={5}>
        <Button variant="contained" color="primary" size="large" onClick={handleSearch}>
          Search
        </Button>
      </Box>

      <Typography variant="h6" gutterBottom>
        Results
      </Typography>
      {results.length > 0 ? (
        results.map((paper, index) => (
          <Paper key={index} elevation={2} sx={{ p: 2, mb: 2 }}>
            <Typography variant="subtitle1"><strong>{paper.title}</strong></Typography>
            <Typography variant="body2">{paper.abstract}</Typography>
            <Typography variant="caption">
              Hashtags: {paper.hashtags.join(", ")}
            </Typography>
          </Paper>
        ))
      ) : (
        <Typography variant="body1">No results yet.</Typography>
      )}

      {tableData.columns.length > 0 && tableData.rows.length > 0 && (
        <>
          <Typography variant="h6" sx={{ mt: 5, mb: 2 }}>
            Summary Table
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  {tableData.columns.map((col, idx) => (
                    <TableCell key={idx}><strong>{col}</strong></TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {tableData.rows.map((row, idx) => (
                  <TableRow key={idx}>
                    {row.map((cell, i) => (
                      <TableCell key={i}>{cell}</TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </>
      )}
    </Container>
  );
}

export default App;
