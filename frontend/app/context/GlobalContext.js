"use client"

import React, { createContext, useState, useContext } from 'react';

const LoadingContext = createContext();

export const useLoading = () => useContext(LoadingContext);

export const GlobalProvider = ({ children }) => {
  const [isLoaded, setIsLoaded] = useState(false);

  const setLoading = (loaded) => {
    setIsLoaded(loaded);
  };

  return (
    <LoadingContext.Provider value={{ isLoaded, setLoading }}>
      {children}
    </LoadingContext.Provider>
  );
};
