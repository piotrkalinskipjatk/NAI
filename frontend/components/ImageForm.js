import React, { useState } from 'react';

const ImageForm = ({ onSubmit, isFileUploaded }) => {
    const [parameters, setParameters] = useState({
        style: '',
        color: ''
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setParameters(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        onSubmit(parameters);
        setParameters({
            style: '',
            color: ''
        });
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-6">
            <div className="flex flex-col items-left">
                <label htmlFor="style" className="font-semibold" style={{color: 'var(--foreground)'}}>Image Style:</label>
                <select
                    id="style"
                    name="style"
                    value={parameters.style}
                    onChange={handleChange}
                    className="form-element p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    style={{
                        backgroundColor: 'var(--input-bg)',
                        color: 'var(--input-text)',
                        borderColor: 'var(--input-border)'
                    }}
                >
                    <option value="">Select style</option>
                    <option value="minimalist">Minimalist</option>
                    <option value="retro">Retro</option>
                    <option value="futuristic">Futuristic</option>
                    <option value="abstract">Abstract</option>
                    <option value="vintage">Vintage</option>
                    <option value="modern">Modern</option>
                    <option value="cartoon">Cartoon</option>
                    <option value="realistic">Realistic</option>
                </select>
            </div>
            <div className="flex flex-col items-left">
                <label htmlFor="color" className="font-semibold" style={{color: 'var(--foreground)'}}>Color:</label>
                <input
                    type="text"
                    id="color"
                    name="color"
                    value={parameters.color}
                    onChange={handleChange}
                    placeholder="Enter color"
                    className="form-element p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    style={{
                        backgroundColor: 'var(--input-bg)',
                        color: 'var(--input-text)',
                        borderColor: 'var(--input-border)'
                    }}
                />
            </div>
            <div className="flex justify-center">
                <button
                    type="submit"
                    className={`form-element font-semibold px-4 py-2 rounded-md border-2 ${
                        !isFileUploaded
                            ? 'border-gray-500 text-gray-500 cursor-not-allowed'
                            : 'bg-gray-800 border-blue-500 text-blue-500 hover:bg-blue-500 hover:text-white hover:border-blue-500'
                    }`}
                    disabled={!isFileUploaded}
                >
                    Generate Image
                </button>
            </div>
        </form>
    );
};

export default ImageForm;
