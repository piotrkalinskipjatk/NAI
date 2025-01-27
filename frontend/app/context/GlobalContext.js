"use client";

import React, { createContext, useState, useContext } from "react";

const GlobalContext = createContext();

export const useGlobalContext = () => useContext(GlobalContext);

export const GlobalProvider = ({ children }) => {
    const [isLoaded, setIsLoaded] = useState(false);
    const [imageUrl, setImageUrl] = useState(null);
    const [uploadError, setUploadError] = useState(null);

    const setLoading = (loaded) => {
        setIsLoaded(loaded);
    };

    const uploadAndFetchImage = async (file, parameters) => {
        try {
            setIsLoaded(true);
            const formData = new FormData();
            formData.append("file", file);
            formData.append("style", parameters.style);
            formData.append("color", parameters.color);

            const response = await fetch("http://127.0.0.1:8000/generate/", {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                throw new Error(`Error: ${response.statusText}`);
            }

            const blob = await response.blob();
            const imageUrl = URL.createObjectURL(blob);
            setImageUrl(imageUrl);
        } catch (error) {
            console.error("Error uploading file:", error);
            setUploadError("Failed to upload the file. Please try again.");
        } finally {
            setIsLoaded(false);
        }
    };

    return (
        <GlobalContext.Provider
            value={{
                isLoaded,
                setLoading,
                uploadAndFetchImage,
                imageUrl,
                uploadError,
                setUploadError,
            }}
        >
            {children}
        </GlobalContext.Provider>
    );
};