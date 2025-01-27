import React, { useState } from "react";
import { useDropzone } from "react-dropzone";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faUpload, faCheckCircle } from "@fortawesome/free-solid-svg-icons";
import { useGlobalContext } from "@/app/context/GlobalContext";
import ImageForm from "@/components/ImageForm";
import ImageDisplay from "@/components/ImageDisplay";

const Uploader = () => {
    const { uploadAndFetchImage, setUploadError } = useGlobalContext();
    const [file, setFile] = useState(null);

    const { getRootProps, getInputProps } = useDropzone({
        accept: "video/mp4",
        onDrop: (acceptedFiles) => {
            setFile(acceptedFiles[0]);
        },
    });

    const handleFormSubmit = async (formParameters) => {
        setUploadError(null);

        if (!file) {
            setUploadError("Please add a file before submitting.");
            return;
        }

        try {
            await uploadAndFetchImage(file, formParameters);
            setFile(null);
        } catch (error) {
            console.error("Error during submission:", error);
        }
    };

    return (
        <div className="flex flex-row gap-8">
            <div className="left-column flex flex-col space-y-6">
                <div
                    {...getRootProps({
                        className: `cursor-pointer rounded-lg p-10 text-center border-4 border-dashed ${
                            file ? "border-green-500" : "border-blue-500 hover:border-blue-700"
                        }`,
                    })}
                >
                    <input {...getInputProps()} />
                    {file ? (
                        <div className="text-center">
                            <FontAwesomeIcon
                                icon={faCheckCircle}
                                className="text-2xl text-green-500 mr-2"
                            />
                            <p className="text-lg text-green-600">
                                File uploaded: {file.name}
                            </p>
                        </div>
                    ) : (
                        <>
                            <FontAwesomeIcon
                                icon={faUpload}
                                className="text-2xl text-blue-500 mr-2"
                            />
                            <p className="text-lg" style={{ color: "var(--text-color)" }}>
                                Drag and drop a file here, or click to select a file.
                            </p>
                        </>
                    )}
                </div>
                <ImageForm onSubmit={handleFormSubmit} isFileUploaded={!!file} />
            </div>

            <div className="right-column pl-4">
                <ImageDisplay />
            </div>
        </div>
    );
};

export default Uploader;
