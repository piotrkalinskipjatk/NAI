import React from "react";
import { useGlobalContext } from "@/app/context/GlobalContext";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faImage } from "@fortawesome/free-solid-svg-icons";
import { BarLoader } from "react-spinners";

const ImageDisplay = () => {
    const { imageUrl, isLoaded } = useGlobalContext();

    const downloadImage = () => {
      if (imageUrl) {
          const link = document.createElement("a");
          link.href = imageUrl;
          link.download = "generated_thumbnail.jpg";
          link.click();
      }
    };

    return (
        <div className="image-container">
            {!imageUrl ? (
                <div className="flex flex-col justify-center items-center">
                    {isLoaded ? (
                        <>
                            <BarLoader color="#0070f3" />
                            <p className="text-center mt-4 text-gray-600 text-sm">
                                Generating image in progress... this may take up to few minutes.
                            </p>
                        </>
                    ) : (
                        <FontAwesomeIcon
                            icon={faImage}
                            className="text-6xl text-gray-400"
                        />
                    )}
                </div>
            ) : (
                <img
                    src={imageUrl}
                    alt="Generated"
                    className="rounded-md shadow-md cursor-pointer"
                    onClick={downloadImage}
                />
            )}
        </div>
    );
};

export default ImageDisplay;
