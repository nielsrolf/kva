import React, { useState } from 'react';
import PanelTypeSwitch from './PanelTypeSwitch';
import '../styles.css';

const Panel = ({ name, data, type, index, slider }) => {  // Add slider as a prop
  const [isOpen, setIsOpen] = useState(true);

  const togglePanel = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div className="panel">
      <div className="panel-header" onClick={togglePanel}>
        <h2>{name}</h2>
        <button>{isOpen ? 'Hide' : 'Show'}</button>
      </div>
      {isOpen && (
        <PanelTypeSwitch 
          data={data} 
          type={type} 
          index={index} 
          slider={slider} 
        />
      )}
    </div>
  );
};

export default Panel;
