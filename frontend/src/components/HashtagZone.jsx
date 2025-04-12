import React from 'react';
import { Box, Typography } from '@mui/material';
import HashtagInput from './HashtagInput';

const HashtagZone = ({ title, items, setItems }) => (
  <Box mb={3}>
    <Typography variant="h6">{title}</Typography>
    <HashtagInput
      label={`Add hashtag to ${title}`}
      items={items}
      setItems={setItems}
    />
  </Box>
);

export default HashtagZone;
