import React from 'react';
import YamlPanel from './YamlPanel';
import ImagePanel from './ImagePanel';
import TablePanel from './TablePanel';

const Panel = ({ name, data, type, index }) => {
  console.log('Panel', name, data, type, index);
  if (type === 'data' && index) {
    return (
      <div>
        <h2>{name}</h2>
        <TablePanel data={data} index={index} />
      </div>
    );
  } else if (type === 'data') {
    if (typeof data === 'object' && !Array.isArray(data)) {
      return (
        <div>
          <h2>{name}</h2>
          <YamlPanel data={data} />
        </div>
      );
    }
  } else if (type === 'image' && data && data.path && data.filename) {
    return (
      <div>
        <h2>{name}</h2>
        <ImagePanel data={data} />
      </div>
    );
  }

  // Add more types as needed
  return (
    <div>
      <h2>{name}</h2>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
};

export default Panel;
