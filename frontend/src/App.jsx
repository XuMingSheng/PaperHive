import React, { useState, useEffect } from "react";
import {
  Container,
  Typography,
  TextField,
  Chip,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Box,
  CssBaseline
} from "@mui/material";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import {
  DragDropContext,
  Droppable,
  Draggable
} from "@hello-pangea/dnd";

const darkTheme = createTheme({
  palette: {
    mode: "dark"
  }
});

function App() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [tableData, setTableData] = useState({ columns: [], rows: [] });

  const [hashtagOr, setHashtagOr] = useState([]);
  const [hashtagAnd, setHashtagAnd] = useState([]);
  const [hashtagNot, setHashtagNot] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [autocompleteSuggestions, setAutocompleteSuggestions] = useState([]);

  const [inputOr, setInputOr] = useState("");
  const [inputAnd, setInputAnd] = useState("");
  const [inputNot, setInputNot] = useState("");

  const [pdfFile, setPdfFile] = useState(null);

  const handleSearch = async () => {
    try {
      const response = await fetch("http://localhost:8000/search/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query,
          or: hashtagOr,
          and: hashtagAnd,
          not: hashtagNot
        })
      });
      const data = await response.json();
      setResults(data.results || []);
      setTableData(data.table || { columns: [], rows: [] });
    } catch (error) {
      console.error("Error fetching search results:", error);
    }
  };

  const fetchRecommendations = async () => {
    try {
      const res = await fetch("http://localhost:8000/recommend/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          or: hashtagOr,
          and: hashtagAnd,
          not: hashtagNot
        })
      });
      const data = await res.json();
      setRecommendations(data.recommendations || []);
    } catch (err) {
      console.error("Failed to fetch recommendations:", err);
    }
  };

  const fetchAutocomplete = async (input) => {
    if (!input) return;

    try {
      const res = await fetch("http://localhost:8000/autocomplete", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ q: input })
      });

      const data = await res.json();
      setAutocompleteSuggestions(data.suggestions || []);
    } catch (err) {
      console.error("Failed to fetch autocomplete:", err);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, [hashtagOr, hashtagAnd, hashtagNot]);

  const handlePdfUpload = (event) => {
    const file = event.target.files[0];
    if (file && file.type === "application/pdf") {
      setPdfFile(file);
      const formData = new FormData();
      formData.append("file", file);
      fetch("http://localhost:8000/upload-pdf/", {
        method: "POST",
        body: formData
      })
        .then((res) => res.json())
        .then((data) => {
          console.log("PDF uploaded", data);
        });
    }
  };

  const handleDelete = (tag, list, setList) => {
    setList(list.filter((item) => item !== tag));
  };

  const handleDrop = (result) => {
    const { source, destination, draggableId } = result;
    if (!destination) return;
    if (source.droppableId === destination.droppableId && source.index === destination.index) return;

    const updateList = (list, setList) => {
      const newList = Array.from(list);
      newList.splice(source.index, 1);
      newList.splice(destination.index, 0, draggableId);
      setList(newList);
    };

    const moveItem = (fromList, toList, setFromList, setToList) => {
      const newFrom = fromList.filter((tag) => tag !== draggableId);
      const newTo = toList.includes(draggableId) ? toList : [...toList, draggableId];
      setFromList(newFrom);
      setToList(newTo);
    };

    const droppables = {
      recommend: [recommendations, setRecommendations],
      or: [hashtagOr, setHashtagOr],
      and: [hashtagAnd, setHashtagAnd],
      not: [hashtagNot, setHashtagNot]
    };

    if (source.droppableId === destination.droppableId) {
      updateList(...droppables[source.droppableId]);
    } else {
      moveItem(...droppables[source.droppableId], ...droppables[destination.droppableId]);
    }
  };

  const renderZone = (id, title, items, inputVal, setInputVal, setList) => (
    <Box mb={3}>
      <Typography variant="h6">{title}</Typography>
      <TextField
        fullWidth
        placeholder={`Add hashtag to ${title}`}
        value={inputVal}
        onChange={(e) => {
          const val = e.target.value;
          setInputVal(val);
          fetchAutocomplete(val);
        }}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && inputVal.trim()) {
            const val = inputVal.trim();
            if (!items.includes(val)) setList([...items, val]);
            setInputVal('');
          }
        }}
        InputProps={{ style: { color: 'white' } }}
        sx={{ mb: 1 }}
      />
      <Droppable droppableId={id} direction="horizontal">
        {(provided) => (
          <Box
            ref={provided.innerRef}
            {...provided.droppableProps}
            sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, border: '1px dashed #888', borderRadius: 1, p: 1 }}
          >
            {items.map((tag, index) => (
              <Draggable key={tag} draggableId={tag} index={index}>
                {(providedDraggable) => (
                  <Chip
                    ref={providedDraggable.innerRef}
                    {...providedDraggable.draggableProps}
                    {...providedDraggable.dragHandleProps}
                    label={tag}
                    onDelete={() => handleDelete(tag, items, setList)}
                    sx={{ bgcolor: 'secondary.main', color: 'white' }}
                  />
                )}
              </Draggable>
            ))}
            {provided.placeholder}
          </Box>
        )}
      </Droppable>
    </Box>
  );

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Container maxWidth="md" sx={{ pt: 4, pb: 6 }}>
        <Typography variant="h4" align="center" gutterBottom>
          Hashtag-Based Paper Search
        </Typography>

        <Box mb={3}>
          <Typography variant="h6">Query</Typography>
          <TextField
            fullWidth
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            variant="outlined"
            placeholder="Enter your query"
            InputProps={{ style: { color: 'white' } }}
          />
        </Box>

        <DragDropContext onDragEnd={handleDrop}>
          {renderZone("recommend", "Recommended Hashtags", recommendations, "", () => {}, () => {})}
          {renderZone("or", "OR", hashtagOr, inputOr, setInputOr, setHashtagOr)}
          {renderZone("and", "AND", hashtagAnd, inputAnd, setInputAnd, setHashtagAnd)}
          {renderZone("not", "NOT", hashtagNot, inputNot, setInputNot, setHashtagNot)}
        </DragDropContext>

        <Box mb={3}>
          <Typography variant="h6">Upload PDF (optional)</Typography>
          <Button variant="outlined" component="label">
            Upload PDF
            <input type="file" hidden accept="application/pdf" onChange={handlePdfUpload} />
          </Button>
          {pdfFile && (
            <Typography variant="body2" mt={1}>{pdfFile.name}</Typography>
          )}
        </Box>

        <Box textAlign="center" mb={4}>
          <Button variant="contained" color="primary" size="large" onClick={handleSearch}>
            Search
          </Button>
        </Box>

        <Typography variant="h6">Results</Typography>
        {results.map((paper, idx) => (
          <Paper key={idx} sx={{ p: 2, mb: 2 }}>
            <Typography variant="subtitle1"><strong>{paper.title}</strong></Typography>
            <Typography variant="body2">{paper.abstract}</Typography>
            <Typography variant="caption">Hashtags: {paper.hashtags.join(", ")}</Typography>
          </Paper>
        ))}

        {tableData.columns.length > 0 && (
          <>
            <Typography variant="h6" mt={4} mb={2}>Summary Table</Typography>
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
    </ThemeProvider>
  );
}

export default App;