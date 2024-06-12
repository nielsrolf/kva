import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const RunList = () => {
  const [runs, setRuns] = useState([]);

  useEffect(() => {
    axios.get('http://0.0.0.0:8000/runs')
      .then(response => {
        setRuns(response.data.runs);
      })
      .catch(error => {
        console.error('There was an error fetching the runs!', error);
      });
  }, []);

  return (
    <div>
      <h1>Run List</h1>
      <ul>
        {runs.map((run, index) => (
          <li key={index}>
            <Link to={`/view/${run}`}>{run}</Link>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default RunList;
