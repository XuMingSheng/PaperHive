import React from 'react';
import { Paper, Typography, Box, Chip } from '@mui/material';

const PaperResult = ({ paper }) => (
  <Paper sx={{ p: 2, mb: 2 }}>
    <Typography variant="h6">{paper.title}</Typography>
    <Typography variant="body2" sx={{ mt: 1 }}>{paper.abstract}</Typography>


    <Box mt={1} sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
      {paper.hashtags.map((tag) => (
        <Chip
          key={tag}
          label={`#${tag}`}
          sx={{ bgcolor: 'grey.800', color: 'primary.main', fontWeight: 'bold' }}
        />
      ))}
    </Box>
  </Paper>
);

export default PaperResult;
