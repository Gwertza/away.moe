// src/components/DownloadPage.js

import React, { useState } from "react";
import { BASE_URL } from "../config";

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

  const isImage = data.filename.match(/\.(jpeg|jpg|gif|png|bmp)$/i);

  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <h1>Entry Found</h1>
      <p><strong>Text:</strong> {data.text}</p>
      <p><strong>Filename:</strong> {data.filename}</p>

      {isImage ? (
        <div>
          <h3>Image:</h3>
          <img
            src={`${BASE_URL}/api/download/${data.unique_id}`}
            alt="Preview"
            style={{ maxWidth: "100%", maxHeight: "500px", marginTop: "20px" }}
          />
        </div>
      ) : (
        <div>
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
      )}
    </div>
  );
};

const styles = {
  button: {
    padding: "10px 20px",
    border: "none",
    borderRadius: "4px",
    backgroundColor: "#007BFF",
    color: "white",
    cursor: "pointer",
  },
};

export default DownloadPage;
