import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const HashtagRecommend = ({ recommendations }) => (
  <Box mt={4}>
    <Typography variant="h6">Recommended Hashtags</Typography>

    {recommendations.length === 0 && (
      <Typography variant="body2" color="textSecondary">
        No recommendations yet.
      </Typography>
    )}

    {recommendations.map((tag) => (
      <Paper key={tag.name} sx={{ p: 1, my: 1 }}>
        <Typography variant="subtitle2">#{tag.name}</Typography>
        <Typography variant="body2" color="textSecondary">
          {tag.description}
        </Typography>
      </Paper>
    ))}
  </Box>
);

export default HashtagRecommend