import React from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const LinePlotPanel = ({ data, index }) => {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart
        data={data}
        margin={{
          top: 5, right: 30, left: 20, bottom: 5,
        }}
      >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey={index} />
        <YAxis />
        <Tooltip />
        <Legend />
        {Object.keys(data[0] || {}).map(key => (
          key !== index ? <Line key={key} type="monotone" dataKey={key} stroke="#8884d8" activeDot={{ r: 8 }} /> : null
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
};

export default LinePlotPanel;
