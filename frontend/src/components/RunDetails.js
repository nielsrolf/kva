import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom'; // Import useNavigate
import axios from 'axios';
import Panel from './Panel';

const RunDetails = () => {
  const { path } = useParams();
  const [data, setData] = useState({});
  const navigate = useNavigate(); // Initialize useNavigate

  useEffect(() => {
    axios.get(`/data/${path}`)
      .then(response => {
        setData(response.data);
      })
      .catch(error => {
        console.error('There was an error fetching the run details!', error);
      });
  }, [path]);

  return (
    <div>
      <button onClick={() => navigate('/')}>Back to Run List</button> {/* Add Back Button */}
      <h1>Run Details</h1>
      {Object.keys(data).map((panelName, index) => {
        const panel = data[panelName];
        return (
          <Panel 
            key={index} 
            name={panelName} 
            data={panel.data} 
            type={panel.type} 
            index={panel.index} 
            slider={panel.slider}  // Pass the slider property
          />
        );
      })}
    </div>
  );
};

export default RunDetails;
