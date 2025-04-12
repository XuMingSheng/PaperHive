import React, { createContext, useContext, useState } from 'react';

const SearchContext = createContext(null);

export const SearchProvider = ({ children }) => {
  const [hashtagOr, setHashtagOr] = useState([]);
  const [hashtagAnd, setHashtagAnd] = useState([]);
  const [hashtagNot, setHashtagNot] = useState([]);
  const [query, setQuery] = useState("");

  return (
    <SearchContext.Provider
      value={{
        hashtagOr, setHashtagOr,
        hashtagAnd, setHashtagAnd,
        hashtagNot, setHashtagNot,
        query, setQuery
      }}
    >
      {children}
    </SearchContext.Provider>
  );
};

export const useSearchContext = () => {
  const context = useContext(SearchContext);

  if (!context) {
    throw new Error("useSearchContext must be used within a SearchProvider");
  }
  
  return context;
};