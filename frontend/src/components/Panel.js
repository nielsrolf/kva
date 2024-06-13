import React, { useState } from 'react';
import YamlPanel from './YamlPanel';
import TablePanel from './TablePanel';
import LinePlotPanel from './LinePlotPanel';
import FilePanel from './FilePanel'; // Import the new FilePanel
import '../styles.css';

const Panel = ({ name, data, type, index }) => {
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
        <div className={`panel-content ${isOpen ? '' : 'hidden'}`}>
          {type === 'lineplot' && index && <LinePlotPanel data={data} index={index} />}
          {type === 'data' && index && <TablePanel data={data} index={index} />}
          {type === 'data' && !index && <YamlPanel data={data} />}
          {type === 'image' && data && data.path && data.filename && <FilePanel data={data} />}
          {type === 'file' && data && data.path && data.filename && <FilePanel data={data} />}
          {/* Add more types as needed */}
          {type !== 'lineplot' && type !== 'data' && type !== 'file' && <pre>{JSON.stringify(data, null, 2)}</pre>}
        </div>
      )}
    </div>
  );
};

export default Panel;
