import React, { useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUpload } from '@fortawesome/free-solid-svg-icons';
import { BarLoader } from 'react-spinners';
import {useLoading} from "@/app/context/GlobalContext";
import ImageForm from "@/components/ImageForm";


const Uploader = ({ onFileUpload }) => {
  const { isLoaded, setLoading } = useLoading();

useEffect(() => {
  const timer = setTimeout(() => {
    setLoading(true);
  }, 200);

  return () => clearTimeout(timer);
}, [setLoading]);


  const { getRootProps, getInputProps } = useDropzone({
    accept: 'video/mp4',
    onDrop: acceptedFiles => {
      onFileUpload(acceptedFiles[0]);
    }
  });

  return (
      <div>
          <div {...getRootProps({
              className: `cursor-pointer rounded-lg p-10 text-center relative mt-4 mb-4 ${isLoaded ? 'border-4 border-dashed border-blue-500 hover:border-blue-700' : 'border-none'}`
          })}>

              <input {...getInputProps()} />
              {!isLoaded && (
                  <div className="absolute top-0 left-0 w-full h-full flex justify-center items-center">
                      <BarLoader color="#0070f3"/>
                  </div>
              )}

              {isLoaded && (
                  <>
                      <FontAwesomeIcon icon={faUpload} className="text-2xl text-blue-500 mr-2"/>
                      <p className="text-lg" style={{color: 'var(--text-color)'}}>Przeciągnij i upuść plik tutaj, lub
                          kliknij aby wybrać plik.</p>
                  </>
              )}
          </div>

          <ImageForm/>
      </div>
  );
};

export default Uploader;
