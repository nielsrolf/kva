import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import Panel from './Panel';

const RunDetails = () => {
  const { path } = useParams();
  const [data, setData] = useState({});

  useEffect(() => {
    axios.get(`http://localhost:8000/view/${path}`)
      .then(response => {
        setData(response.data);
      })
      .catch(error => {
        console.error('There was an error fetching the run details!', error);
      });
  }, [path]);

  return (
    <div>
      <h1>Run Details</h1>
      {Object.keys(data).map((panelName, index) => {
        const panel = data[panelName];
        return <Panel key={index} name={panelName} data={panel.data} type={panel.type} index={panel.index} />;
      })}
    </div>
  );
};

export default RunDetails;
