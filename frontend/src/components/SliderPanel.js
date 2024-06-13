import React, { useState } from 'react';
import PanelTypeSwitch from './PanelTypeSwitch';

const SliderPanel = ({ data, slider, type, index }) => {
  const [currentStep, setCurrentStep] = useState(0);

  const steps = data.map(item => item[slider]);
  const uniqueSteps = [...new Set(steps)].sort((a, b) => a - b);

  const handleSliderChange = (event) => {
    setCurrentStep(parseInt(event.target.value, 10));
  };

  const currentData = data.filter(item => item[slider] === uniqueSteps[currentStep]);

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
      <div>Step: {uniqueSteps[currentStep]}</div>
      {currentData.map((item, index) => (
        <PanelTypeSwitch
          key={index}
          data={item}
          type={type}
          index={index}
          initiallyOpen={true} // Ensure the YamlPanel opens all levels by default
        />
      ))}
    </div>
  );
};

export default SliderPanel;
