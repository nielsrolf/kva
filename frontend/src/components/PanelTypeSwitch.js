import React from 'react';
import YamlPanel from './YamlPanel';
import TablePanel from './TablePanel';
import LinePlotPanel from './LinePlotPanel';
import FilePanel from './FilePanel';
import SliderPanel from './SliderPanel';  // Import the new SliderPanel
import '../styles.css';

const PanelTypeSwitch = ({ data, type = 'data', index, slider, initiallyOpen = false }) => {  // Add slider as a prop

  if (slider) {
    return <SliderPanel data={data} slider={slider} type={type} index={index} />;
  }

  console.log('data:', data)
  console.log('index:', index)
  console.log('type:', type)
  return (
    <div className={`panel-content`}>
      {type === 'lineplot' && index && <LinePlotPanel data={data} index={index} />}
      {type === 'data' && index && <TablePanel data={data} index={index} />}
      {type === 'data' && !index && <YamlPanel data={data} initiallyOpen={initiallyOpen} />}
      {type === 'image' && data && data.path && data.filename && <FilePanel data={data} />}
      {type === 'file' && data && data.path && data.filename && <FilePanel data={data} />}
      {/* Add more types as needed */}
      {type !== 'lineplot' && type !== 'data' && type !== 'file' && <pre>{JSON.stringify(data, null, 2)}</pre>}
    </div>
  );
};

export default PanelTypeSwitch;
