import React from 'react';
import { Box, Typography, Tooltip, Chip } from '@mui/material';
import { useHashtagInfo } from '../hooks/useHashtagInfo';

const HashtagRecommend = ({ recommendations }) => {
  const { tagInfo, fetchHashtagInfo } = useHashtagInfo();

  return (
    <Box mt={4}>
      <Typography variant="h6">Recommended Hashtags</Typography>

      {recommendations.length === 0 && (
        <Typography variant="body2" color="textSecondary">
          No recommendations yet.
        </Typography>
      )}

      <Box display="flex" flexWrap="wrap" gap={1} mt={1}>
        {recommendations.map((tag) => {
          const info = tagInfo[tag.name];
          return (
            <Tooltip
              key={info?.description || tag.name}
              title={info?.description || `#${tag.name}`}
              onOpen={() => fetchHashtagInfo(tag.name)}
            >
              <Chip
                label={`#${tag.name}`}
                sx={{ bgcolor: "grey.800", color: "primary.main", fontWeight: "bold" }}
              />
            </Tooltip>
          );
        })}
      </Box>

      {/* {recommendations.map((tag) => (
        <Paper key={tag.name} sx={{ p: 1, my: 1 }}>
          <Typography variant="subtitle2">#{tag.name}</Typography>
          <Typography variant="body2" color="textSecondary">
            {tag.description}
          </Typography>
        </Paper>
      ))} */}
    </Box>
  );
};

export default HashtagRecommend