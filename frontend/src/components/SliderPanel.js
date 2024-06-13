import React, { useState } from 'react';
import PanelTypeSwitch from './PanelTypeSwitch';

const SliderPanel = ({ data, slider, type, index }) => {
  const [currentStep, setCurrentStep] = useState(0);

  console.log(data);

  const steps = data.map(item => item[slider]);
  const uniqueSteps = [...new Set(steps)].sort((a, b) => a - b);
  const handleSliderChange = (event) => {
    setCurrentStep(parseInt(event.target.value, 10));
  };

  const currentData = data.find(item => item[slider] === uniqueSteps[currentStep]);

  return (
    <div>
      <input
        type="range"
        min="0"
        max={uniqueSteps.length - 1}
        value={currentStep}
        onChange={handleSliderChange}
        className="slider"
      />
      {currentData && <PanelTypeSwitch 
          data={data} 
          type={type} 
          index={index} 
        />}
    </div>
  );
};

export default SliderPanel;
