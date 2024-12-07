import React, { useState } from "react";

const UploadForm = () => {
  const [uniqueId, setUniqueId] = useState("");
  const [file, setFile] = useState(null);
  const [text, setText] = useState("");
  const [date, setDate] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append("file", file);
    formData.append("text", text);
    formData.append("date", date);

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
    <form onSubmit={handleSubmit}>
      <div>
        <label>Unique ID:</label>
        <input
          type="text"
          value={uniqueId}
          onChange={(e) => setUniqueId(e.target.value)}
          required
        />
      </div>
      <div>
        <label>Text:</label>
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          required
        />
      </div>
      <div>
        <label>Date:</label>
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          required
        />
      </div>
      <div>
        <label>File:</label>
        <input
          type="file"
          onChange={(e) => setFile(e.target.files[0])}
          required
        />
      </div>
      <button type="submit">Upload</button>
    </form>
  );
};

export default UploadForm;
