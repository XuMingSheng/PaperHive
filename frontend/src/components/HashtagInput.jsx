import React, { useState, useEffect } from "react";
import { TextField, Autocomplete, Chip, CircularProgress } from "@mui/material";
import { fetchAutocomplete } from "../api/hashtagApi";

const HashtagInput = ({label, items, setItems}) => {
  const [inputValue, setInputValue] = useState("");
  const [options, setOptions] = useState([]);
  const [loading, setLoading] = useState(false);

  // React's useEffect: Runs every time value changes (i.e., user typing).
  useEffect(
    () => {
      if (!inputValue) return;
      
      setLoading(true);
      fetchAutocomplete(inputValue)
        .then(setOptions)
        .catch(console.error)
        .finally(() => setLoading(false));
    }, 
    [inputValue]
  )
  
  return (
    <Autocomplete
      // freeSolo
      multiple
      options={options}
      loading={loading}
      
      value={items}
      onChange={(e, newValue) => setItems(newValue)}
      
      inputValue={inputValue}
      onInputChange={(e, newInput) => setInputValue(newInput)}

      renderValue={(tagValue, getTagProps) =>
        tagValue.map((option, index) => (
          <Chip
            key={option}
            label={option}
            {...getTagProps({ index })}
            sx={{ bgcolor: 'grey.800', color: 'primary.main', fontWeight: 'bold' }}
          />
        ))
      }
      
      renderInput={(params) => (
        <TextField
          {...params}
          label={label}
          variant="outlined"
          placeholder="Type to search..."
          InputProps={{
            ...params.InputProps,
            endAdornment: (
              <>
                {loading ? <CircularProgress size={20} /> : null}
                {params.InputProps.endAdornment}
              </>
            ),
          }}
        />
      )}
    />
  ); 
};

export default HashtagInput;