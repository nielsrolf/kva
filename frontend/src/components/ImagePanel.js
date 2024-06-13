// src/components/ImagePanel.js

import React from 'react';

const ImagePanel = ({ data }) => {
  if (!data.path) {
    return <div>Invalid image data</div>;
  }

  const imagePath = `http://localhost:8000/${data.path}`;

  return (
    <div>
      <h3>{data.filename}</h3>
      <img src={imagePath} alt={data.filename} style={{ maxWidth: '100%', height: 'auto' }} />
    </div>
  );
};

export default ImagePanel;
