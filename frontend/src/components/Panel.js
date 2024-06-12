import React from 'react';

const Panel = ({ name, data }) => {
  return (
    <div>
      <h2>{name}</h2>
      {/* Add logic to render different types of panels based on the 'type' */}
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
};

export default Panel;
