import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import { BASE_URL } from "../config";

const FileHandler = () => {
  const { uniqueId } = useParams();
  const [data, setData] = useState(null);
  const [notFound, setNotFound] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [downloadProgress, setDownloadProgress] = useState(0);

  useEffect(() => {
    // Check if the entry exists for the unique ID
    fetch(`${BASE_URL}/api/fetch_info/${uniqueId}`)
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
    return <UploadForm uniqueId={uniqueId} setUploadProgress={setUploadProgress} uploadProgress={uploadProgress} />;
  }

  if (!data) return <p style={{ textAlign: "center" }}>Loading...</p>;

  return (
    <DownloadPage
      data={data}
      setDownloadProgress={setDownloadProgress}
      downloadProgress={downloadProgress}
    />
  );
};

const DownloadPage = ({ data, setDownloadProgress, downloadProgress }) => {
  const handleDownload = () => {
    fetch(`${BASE_URL}/api/download/${data.unique_id}`, {
      method: "GET",
    })
      .then((res) => {
        if (!res.ok) {
          throw new Error("Failed to download the file");
        }
        const total = res.headers.get("Content-Length");
        const reader = res.body.getReader();
        let loaded = 0;
        const chunks = [];

        reader.read().then(function processText({ done, value }) {
          if (done) {
            const blob = new Blob(chunks);
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.style.display = "none";
            a.href = url;
            a.download = data.filename;
            a.click();
            window.URL.revokeObjectURL(url);
            return;
          }
          chunks.push(value);
          loaded += value.length;
          setDownloadProgress(Math.round((loaded / total) * 100)); // Update progress
          reader.read().then(processText);
        });
      })
      .catch((error) => {
        console.error("Error downloading the file:", error);
        alert("Failed to download the file.");
      });
  };

  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <h1>Entry Found</h1>
      <p><strong>Text:</strong> {data.text}</p>
      <p><strong>Filename:</strong> {data.filename}</p>

      {/* Display download progress bar */}
      {downloadProgress > 0 && downloadProgress < 100 && (
        <div style={{ marginTop: "20px", width: "100%", backgroundColor: "#ddd", borderRadius: "8px" }}>
          <div
            style={{
              height: "10px",
              width: `${downloadProgress}%`,
              backgroundColor: "#4caf50",
              borderRadius: "8px",
            }}
          ></div>
        </div>
      )}

      <button onClick={handleDownload} style={styles.button}>
        Download
      </button>
    </div>
  );
};

const UploadForm = ({ uniqueId, setUploadProgress, uploadProgress }) => {
  const [file, setFile] = useState(null);
  const [text, setText] = useState("");
  const [date, setDate] = useState("-1");
  const [dragging, setDragging] = useState(false);

  const handleFileSelect = (e) => {
    setFile(e.target.files[0]);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragging(true);
  };

  const handleDragLeave = () => {
    setDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!file) {
      alert("Please select a file before uploading.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("text", text);
    formData.append("ttl", date);

    axios
      .post(`${BASE_URL}/api/upload/${uniqueId}`, formData, {
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setUploadProgress(percentCompleted);
        },
      })
      .then(() => {
        alert("File uploaded successfully!");
        setUploadProgress(0); // Reset progress
      })
      .catch((error) => {
        console.error("Error uploading file:", error);
        alert("Failed to upload the file.");
        setUploadProgress(0); // Reset progress
      });
  };

  return (
    <div style={styles.container}>
      <h1>away.moe</h1>
      <p>Upload a file for ID: <strong>{uniqueId}</strong></p>
      <form onSubmit={handleSubmit} style={styles.form}>
        <div style={styles.formGroup}>
          <label>Text:</label>
          <input
            type="text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            style={styles.input}
          />
        </div>
        <div style={styles.formGroup}>
          <label>Expiration:</label>
          <select
            value={date}
            onChange={(e) => setDate(e.target.value)}
            style={styles.input}
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
        <div
          style={{
            ...styles.dropZone,
            ...(dragging ? styles.dropZoneActive : {}),
          }}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <label htmlFor="fileInput" style={{ cursor: "pointer" }}>
            Drag & Drop your file here or click to select
          </label>
          <input
            id="fileInput"
            type="file"
            onChange={handleFileSelect}
            style={styles.fileInput} // Hidden input
          />
        </div>

        {file && <p>Selected File: {file.name}</p>}

        {uploadProgress > 0 && (
          <div style={styles.progressBar}>
            <div style={{ ...styles.progress, width: `${uploadProgress}%` }}>
              {uploadProgress}%
            </div>
          </div>
        )}

        <button type="submit" style={styles.button}>
          Upload
        </button>
      </form>
    </div>
  );
};

const styles = {
  container: {
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
    textAlign: "center",
    maxWidth: "500px",
    padding: "20px",
    border: "1px solid #ddd",
    borderRadius: "8px",
    backgroundColor: "#f9f9f9",
    boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
    position: "absolute",
    top: "50%",
    left: "50%",
    transform: "translate(-50%, -50%)",
  },
  form: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
  },
  formGroup: {
    marginBottom: "15px",
    width: "100%",
  },
  input: {
    width: "100%",
    padding: "8px",
    margin: "5px 0",
    border: "1px solid #ccc",
    borderRadius: "4px",
  },
  dropZone: {
    width: "100%",
    padding: "20px",
    border: "2px dashed #ccc",
    borderRadius: "8px",
    textAlign: "center",
    backgroundColor: "#fefefe",
    cursor: "pointer",
  },
  dropZoneActive: {
    backgroundColor: "#e0f7fa",
    borderColor: "#00796b",
  },
  fileInput: {
    display: "none",
  },
  progressBar: {
    width: "100%",
    maxWidth: "400px",
    height: "20px",
    backgroundColor: "#e0e0e0",
    borderRadius: "10px",
    margin: "20px auto",
    overflow: "hidden",
    border: "1px solid #ccc",
  },
  progress: {
    height: "100%",
    backgroundColor: "#007BFF",
    color: "white",
    fontSize: "12px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    borderRadius: "10px 0 0 10px",
    transition: "width 0.3s ease",
  },
  button: {
    padding: "10px 20px",
    border: "none",
    borderRadius: "4px",
    backgroundColor: "#007BFF",
    color: "white",
    cursor: "pointer",
  },
};

export default FileHandler;
