import React, { useState, useEffect } from 'react';
import FilePanel from './FilePanel';
import '../styles.css';

const isImageData = (data) => {
  return data && typeof data === 'object' && 'path' in data && 'filename' in data;
};

const YamlPanel = ({ data, level = 0, initiallyOpen = false }) => {
  const [openState, setOpenState] = useState({});

  useEffect(() => {
    if (initiallyOpen) {
      const initialOpenState = {};
      const setOpenRecursive = (data, currentLevel) => {
        Object.keys(data).forEach((key) => {
          if (typeof data[key] === 'object' && data[key] !== null) {
            initialOpenState[key] = true;
            setOpenRecursive(data[key], currentLevel + 1);
          }
        });
      };
      setOpenRecursive(data, level);
      setOpenState(initialOpenState);
    }
  }, [data, level, initiallyOpen]);

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
              {isOpen && <FilePanel data={value} />}
            </div>
          );
        } else if (typeof value === 'object' && value !== null) {
          return (
            <div key={key}>
              <div onClick={() => toggleOpen(key)} style={{ cursor: 'pointer', fontWeight: 'bold' }}>
                {isOpen ? '▼' : '▶'} {key}
              </div>
              {isOpen && <YamlPanel data={value} level={level + 1} initiallyOpen={initiallyOpen} />}
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
