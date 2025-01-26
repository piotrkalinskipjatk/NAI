"use client";

import React, { Suspense } from 'react';
import Loader from 'react-spinners/BarLoader';
const Uploader = React.lazy(() => import('../components/Uploader'));

export default function UploadPage() {
  return (
    <div className="flex justify-center items-center min-h-screen" style={{ marginTop: '-10vh' }}>
      <div className="max-w-4xl w-full px-4 py-12" style={{
          background: 'var(--container-bg)',
          borderRadius: '8px',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
          padding: '60px'
        }}>
        <h1 className="text-2xl text-blue-600 font-bold text-center mb-6">Prześlij plik</h1>
        <Suspense fallback={<div className="text-center"><Loader color="#00BFFF" /></div>}>
            <Uploader />
        </Suspense>
      </div>
    </div>
  );
}



