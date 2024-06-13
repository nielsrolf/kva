import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import '../styles.css';

const RunList = () => {
  const [runs, setRuns] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    axios.get('/runs')
      .then(response => {
        setRuns(response.data.runs);
      })
      .catch(error => {
        console.error('There was an error fetching the runs!', error);
      });
  }, []);

  const filteredRuns = runs.filter(run => run.match(new RegExp(searchTerm, 'i')));

  return (
    <div>
      <h1>Run List</h1>
      <input
        type="text"
        placeholder="Search runs..."
        value={searchTerm}
        onChange={e => setSearchTerm(e.target.value)}
      />
      <ul>
        {filteredRuns.map((run, index) => (
          <li key={index}>
            <Link to={`/view/${run}`}>{run}</Link>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default RunList;
