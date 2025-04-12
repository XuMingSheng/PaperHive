import React from 'react';
import { Box, Button, Typography } from '@mui/material';

const PdfUploader = ({ pdfFile, handlePdfUpload }) => (
  <Box mb={3}>
    <Typography variant="h6">Upload PDF (optional)</Typography>
    <Button variant="outlined" component="label">
      Upload PDF
      <input type="file" hidden accept="application/pdf" onChange={handlePdfUpload} />
    </Button>
    {pdfFile && <Typography variant="body2" mt={1}>{pdfFile.name}</Typography>}
  </Box>
);

export default PdfUploader;
