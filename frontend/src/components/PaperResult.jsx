import React from 'react';
import { Paper, Typography, Box } from '@mui/material';

const PaperResult = ({ paper }) => (
  <Paper sx={{ p: 2, mb: 2 }}>
    <Typography variant="h6">{paper.title}</Typography>
    <Typography variant="body2" sx={{ mt: 1 }}>{paper.abstract}</Typography>
    <Box mt={1}>
      <Typography variant="caption">Hashtags: {paper.hashtags.join(", ")}</Typography>
    </Box>
  </Paper>
);

export default PaperResult;
