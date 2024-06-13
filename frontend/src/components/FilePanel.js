// frontend/src/components/FilePanel.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import TablePanel from './TablePanel';

const FilePanel = ({ data }) => {
  const [csvData, setCsvData] = useState(null);

  useEffect(() => {
    if (data.filename.endsWith('.csv')) {
      axios.get(`/${data.path}`)
        .then(response => {
          const rows = response.data.split('\n').map(row => row.split(','));
          const headers = rows[0];
          const content = rows.slice(1).map(row => {
            const rowData = {};
            headers.forEach((header, index) => {
              rowData[header] = row[index];
            });
            return rowData;
          });
          setCsvData(content);
        })
        .catch(error => {
          console.error('There was an error fetching the CSV file!', error);
        });
    }
  }, [data]);

  const renderFileContent = () => {
    if (csvData) {
      return <TablePanel data={csvData} />;
    }

    if (data.filename.endsWith('.csv')) {
      return <div>Loading CSV data...</div>;
    }

    const filePath = `/${data.path}`;
    const fileExtension = data.filename.split('.').pop().toLowerCase();

    if (['jpg', 'jpeg', 'png', 'gif'].includes(fileExtension)) {
      return <img src={filePath} alt={data.filename} style={{ maxWidth: '100%', height: 'auto' }} />;
    }
    if (['mp3', 'wav', 'ogg'].includes(fileExtension)) {
      return <audio controls>
        <source src={filePath} type={`audio/${fileExtension}`} />
        Your browser does not support the audio element.
      </audio>;
    }
    if (['mp4', 'webm', 'ogg'].includes(fileExtension)) {
      return <video controls style={{ maxWidth: '100%', height: 'auto' }}>
        <source src={filePath} type={`video/${fileExtension}`} />
        Your browser does not support the video tag.
      </video>;
    }
    if (['txt', 'log', 'md', 'py', 'html', 'css', 'js', 'ts', 'sh'].includes(fileExtension)) {
      return <iframe src={filePath} title={data.filename} style={{ width: '100%', height: '400px', border: 'none' }} />;
    }
    return <a href={filePath} download={data.filename}>Download {data.filename}</a>;
  };

  return (
    <div>
      <h3>{data.filename}</h3>
      {renderFileContent()}
    </div>
  );
};

export default FilePanel;
