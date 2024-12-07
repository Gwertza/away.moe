import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";

const FileHandler = () => {
  const { uniqueId } = useParams();
  const [data, setData] = useState(null);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
  // Check if the entry exists for the unique ID
    fetch(`http://localhost:5000/api/fetch_info/${uniqueId}`)
      .then((res) => {
        if (!res.ok) {
          throw new Error("Network response was not ok");
        }
        return res.json();
      })
      .then((data) => {
        if (data.id_present === true) {
          setData(data);
        } else {
          throw new Error("ID not present");
        }
      })
      .catch(() => setNotFound(true));
}, [uniqueId]);


  if (notFound) {
    return <UploadForm uniqueId={uniqueId} />;
  }

  if (!data) return <p>Loading...</p>;

  return <DownloadPage data={data} />;
};

const DownloadPage = ({ data }) => {
  const handleDownload = () => {
    fetch(`http://localhost:5000/api/download/${data.unique_id}`)
      .then((res) => {
        if (!res.ok) {
          throw new Error("Failed to download the file");
        }
        return res.blob();
      })
      .then((blob) => {
        // Create a downloadable link
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = data.filename; // Use the filename from the response
        link.click();
        // Cleanup the object URL after the download
        window.URL.revokeObjectURL(url);
      })
      .catch((error) => {
        console.error("Error downloading the file:", error);
        alert("Failed to download the file.");
      });
  };

  return (
    <div>
      <h1>Entry Found</h1>
      <p>Text: {data.text}</p>
      <p>Filename: {data.filename}</p>
      <button onClick={handleDownload}>Download</button>
    </div>
  );
};

const UploadForm = ({ uniqueId }) => {
  const [file, setFile] = useState(null);
  const [text, setText] = useState("");
  const [date, setDate] = useState("-1");

  const handleSubmit = (e) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append("file", file);
    formData.append("text", text);
    formData.append("ttl", date);

    fetch(`http://localhost:5000/api/upload/${uniqueId}`, {
      method: "POST",
      body: formData,
    })
      .then((res) => {
        if (res.ok) {
          alert("File uploaded successfully!");
        } else {
          alert("Failed to upload the file.");
        }
      })
      .catch((error) => console.error("Error:", error));
  };

  return (
    <div>
      <h1>No Entry Found</h1>
      <p>Upload a file for ID: {uniqueId}</p>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Text:</label>
          <input
            type="text"
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
        </div>
        <div>
          <label>Expiration:</label>
          <select
              value={date}
              onChange={(e) => {setDate(e.target.value)
                  console.log("Selected expiration value:", e.target.value); // Debugging
}}
              required
          >
            <option value="-1">Delete Upon Viewing (1 Day for entries with files)</option>
            <option value="1m">1 Minute</option>
            <option value="10m">10 Minutes</option>
            <option value="1h">1 Hour</option>
            <option value="1d">1 Day</option>
            <option value="1w">1 Week</option>
          </select>
        </div>
        <div>
          <label>File:</label>
          <input
              type="file"
              onChange={(e) => setFile(e.target.files[0])}
          />
        </div>
        <button type="submit">Upload</button>
      </form>
    </div>
  );
};

export default FileHandler;
