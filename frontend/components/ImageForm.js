import React, { useState } from 'react';

const ImageForm = ({ onSubmit }) => {
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
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="flex flex-col items-center">
        <label htmlFor="style" className="font-semibold" style={{ color: 'var(--foreground)' }}>Styl obrazka:</label>
        <select
            id="style"
            name="style"
            value={parameters.style}
            onChange={handleChange}
            className="p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 w-1/2"
            style={{ backgroundColor: 'var(--input-bg)', color: 'var(--input-text)', borderColor: 'var(--input-border)' }}
        >
            <option value="">Wybierz styl</option>
            <option value="minimalist">Minimalistyczny</option>
            <option value="retro">Retro</option>
            <option value="futuristic">Futurystyczny</option>
        </select>
      </div>
      <div className="flex flex-col items-center">
        <label htmlFor="color" className="font-semibold" style={{ color: 'var(--foreground)' }}>Kolor</label>
        <input
            type="text"
            id="color"
            name="color"
            value={parameters.color}
            onChange={handleChange}
            placeholder="Wpisz kolor"
            className="p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 w-1/2"
            style={{ backgroundColor: 'var(--input-bg)', color: 'var(--input-text)', borderColor: 'var(--input-border)' }}
        />
      </div>
      <div className="flex justify-center">
        <button type="submit" className="px-4 py-2 text-white rounded-md hover:bg-blue-700"
                style={{ backgroundColor: 'var(--button-bg)', color: 'var(--button-text)' }}>
            Generate Image
        </button>
      </div>
    </form>
  );
};

export default ImageForm;
