// src/components/FileHandler.js

import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { BASE_URL } from "../config";
import UploadForm from "./UploadForm";
import DownloadPage from "./DownloadPage";

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

export default FileHandler;
