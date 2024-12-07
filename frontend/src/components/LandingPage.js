import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const LandingPage = () => {
  const [uniqueId, setUniqueId] = useState("");
  const navigate = useNavigate();

  const handleCheck = (e) => {
    e.preventDefault();
    if (uniqueId.trim()) {
      navigate(`/${uniqueId}`);
    }
  };

  return (
    <div>
      <h1>Welcome</h1>
      <p>Enter a unique ID to check its status:</p>
      <form onSubmit={handleCheck}>
        <input
          type="text"
          value={uniqueId}
          onChange={(e) => setUniqueId(e.target.value)}
          placeholder="Enter unique ID"
          required
        />
        <button type="submit">Check</button>
      </form>
    </div>
  );
};

export default LandingPage;
