import React from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const colors = ["#8884d8", "#82ca9d", "#ffc658", "#ff7300", "#387908", "#e8c3b9", "#d0ed57", "#8e44ad", "#3498db"];

const LinePlotPanel = ({ data, index }) => {
  const keys = Object.keys(data[0] || {}).filter(key => key !== index);

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
        {keys.map((key, idx) => (
          <Line 
            key={key} 
            type="monotone" 
            dataKey={key} 
            stroke={colors[idx % colors.length]} 
            activeDot={{ r: 8 }} 
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
};

export default LinePlotPanel;
