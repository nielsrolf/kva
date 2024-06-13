import React from 'react';

const FilePanel = ({ data }) => {
  if (!data.path) {
    return <div>Invalid file data</div>;
  }

  const filePath = `http://localhost:8000/${data.path}`;
  const fileExtension = data.filename.split('.').pop().toLowerCase();

  const renderFileContent = () => {
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
    if (['txt', 'csv', 'log'].includes(fileExtension)) {
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
