// src/components/YamlPanel.js

import React, { useState } from 'react';
import ImagePanel from './ImagePanel';

const isImageData = (data) => {
  return data && typeof data === 'object' && 'path' in data && 'filename' in data;
};

const YamlPanel = ({ data, level = 0 }) => {
  const [openState, setOpenState] = useState({});
  const paddingLeft = level * 20;

  const toggleOpen = (key) => {
    setOpenState((prevState) => ({
      ...prevState,
      [key]: !prevState[key],
    }));
  };

  return (
    <div style={{ paddingLeft }}>
      {Object.keys(data).map((key) => {
        const value = data[key];
        const isOpen = openState[key];

        if (isImageData(value)) {
          return (
            <div key={key}>
              <div onClick={() => toggleOpen(key)} style={{ cursor: 'pointer', fontWeight: 'bold' }}>
                {isOpen ? '▼' : '▶'} {key}
              </div>
              {isOpen && <ImagePanel data={value} />}
            </div>
          );
        } else if (typeof value === 'object' && value !== null) {
          return (
            <div key={key}>
              <div onClick={() => toggleOpen(key)} style={{ cursor: 'pointer', fontWeight: 'bold' }}>
                {isOpen ? '▼' : '▶'} {key}
              </div>
              {isOpen && <YamlPanel data={value} level={level + 1} />}
            </div>
          );
        } else {
          return (
            <div key={key}>
              <span style={{ fontWeight: 'bold' }}>{key}:</span> {String(value)}
            </div>
          );
        }
      })}
    </div>
  );
};

export default YamlPanel;
