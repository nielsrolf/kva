import React, { useState } from 'react';
import YamlPanel from './YamlPanel';
import TablePanel from './TablePanel';
import LinePlotPanel from './LinePlotPanel';
import FilePanel from './FilePanel'; 
import SliderPanel from './SliderPanel';  // Import the new SliderPanel
import '../styles.css';

const PanelTypeSwitch = ({ data, type='data', index, slider, isOpen=true }) => {  // Add slider as a prop

  return (
        <div className={`panel-content ${isOpen ? '' : 'hidden'}`}>
          {type === 'lineplot' && index && <LinePlotPanel data={data} index={index} />}
          {type === 'data' && index && <TablePanel data={data} index={index} />}
          {type === 'data' && !index && <YamlPanel data={data} />}
          {type === 'image' && data && data.path && data.filename && <FilePanel data={data} />}
          {type === 'file' && data && data.path && data.filename && <FilePanel data={data} />}
          {type === 'data' && slider && <SliderPanel data={data} slider={slider} />}
          {/* Add more types as needed */}
          {type !== 'lineplot' && type !== 'data' && type !== 'file' && <pre>{JSON.stringify(data, null, 2)}</pre>}
        </div>
    );
};

export default PanelTypeSwitch;
