 import { useState } from "react";
import axios from "axios";

function App() {
  const [inputs, setInputs] = useState({
    age: "", gender: "", ap_hi: "", ap_lo: "", cholesterol: "", gluc: "",
    smoke: "", alco: "", bmi: ""
  });
  const [output, setOutput] = useState(null);

  const handleChange = (e) => {
    setInputs({...inputs, [e.target.name]: e.target.value});
  };

  const handleSubmit = async () => {
    try {
      const res = await axios.post("http://localhost:5000/predict_fit", inputs, {
        headers: {"Content-Type": "application/json"}
      });
      setOutput(res.data);
    } catch (err) {
      console.error(err);
      alert("Error fetching prediction. Make sure Flask backend is running and CORS is allowed.");
    }
  };

  return (
    <div style={{padding: "20px", fontFamily: "Arial"}}>
      <h1>💓 Heart Attack Risk Prediction</h1>
      <h3>Enter your details:</h3>
      <div style={{display: "flex", flexWrap: "wrap", gap: "15px", marginBottom: "15px"}}>
        {Object.keys(inputs).map((key) => (
          <div key={key}>
            <label>{key}:</label><br/>
            <input
              type="number"
              name={key}
              value={inputs[key]}
              onChange={handleChange}
              style={{width: "80px", padding: "5px"}}
            />
          </div>
        ))}
      </div>
      <button onClick={handleSubmit} style={{padding: "8px 15px", fontSize: "16px"}}>Predict</button>

      {output && (
        <div style={{marginTop: "30px", display: "flex", flexDirection: "column", gap: "20px"}}>
          
          {/* Fit Data Card */}
          <div style={{border: "1px solid #ccc", padding: "15px", borderRadius: "10px", backgroundColor: "#f9f9f9"}}>
            <h3>📊 Fit Data</h3>
            <p>Steps (avg/day): {output.fit_data.avg_steps.toFixed(1)}</p>
            <p>Calories (avg/day): {output.fit_data.avg_calories.toFixed(1)}</p>
            <p>Height: {output.fit_data.height.toFixed(2)} m</p>
            <p>Weight: {output.fit_data.weight.toFixed(1)} kg</p>
          </div>

          {/* Manual Input Card */}
          <div style={{border: "1px solid #ccc", padding: "15px", borderRadius: "10px", backgroundColor: "#eef6ff"}}>
            <h3>📝 Manual Input</h3>
            {Object.entries(output.manual_input).map(([key, value]) => (
              <p key={key}>{key}: {typeof value === "number" ? value.toFixed(2) : value}</p>
            ))}
          </div>

          {/* Prediction Result Card */}
          <div style={{border: "1px solid #ccc", padding: "15px", borderRadius: "10px", backgroundColor: "#ffe6e6"}}>
            <h3>🩺 Prediction Result</h3>
            <p>Predicted Class: {output.predicted_class} ({output.predicted_class === 1 ? "High Risk" : "Low Risk"})</p>
            <p>Probability: {(output.probability * 100).toFixed(2)}%</p>
          </div>

        </div>
      )}
    </div>
  );
}

export default App;

