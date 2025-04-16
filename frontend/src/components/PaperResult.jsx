import React from 'react';
import { Paper, Typography, Box, Chip, Link } from '@mui/material';

const PaperResult = ({ paper }) => (
  <Paper sx={{ p: 2, mb: 2 }}>
    <Typography variant="h6">{paper.title}</Typography>

    <Box mt={1}>
      <Typography variant="caption">
        {paper.year} · {paper.authors?.[0] || "Unknown Author"}
        {paper.arxiv_id && (
          <>
            {' · '}
            <Link
              href={`https://arxiv.org/abs/${paper.arxiv_id}`}
              target="_blank"
              rel="noopener noreferrer"
              underline="hover"
            >
              arXiv:{paper.arxiv_id}
            </Link>
          </>
        )}
      </Typography>
    </Box>
    
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
