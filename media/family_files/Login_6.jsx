import React, { useState } from "react";
import axios from "axios";
import doctor from "../assets/doctor.jpg";

// ✅ Make sure you have these installed:
// npm install @mui/material @emotion/react @emotion/styled
// And Bootstrap CDN or: npm install bootstrap
// In your main index.js/main.jsx: import 'bootstrap/dist/css/bootstrap.min.css';

import {
  TextField,
  Button,
  InputAdornment,
  IconButton,
  CircularProgress,
  Alert,
} from "@mui/material";
import { Visibility, VisibilityOff, LocalHospital } from "@mui/icons-material";

function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const response = await axios.post("http://127.0.0.1:8000/api/login/", {
        username,
        password,
      });

      const token = response.data.access_token;
      localStorage.setItem("token", token);
      alert("Login Successful");
      console.log(response.data);
    } catch (err) {
      setError("Invalid username or password. Please try again.");
      console.log(err.response?.data);
    } finally {
      setLoading(false);
    }
  };

  return (
    // Bootstrap container for centering
    <div
      className="d-flex justify-content-center align-items-center vh-100"
      style={{
        background: "url('../assets/background.jpg') center/cover no-repeat",
        backgroundColor: "#e8f4fd", // fallback color
      }}
    >
      {/* Bootstrap card layout */}
      <div
        className="card border-0 overflow-hidden"
        style={{
          width: "900px",
          maxWidth: "95vw",
          borderRadius: "20px",
          boxShadow: "0 24px 64px rgba(0,0,0,0.15)",
        }}
      >
        <div className="row g-0">
          {/* ── LEFT: Form ── */}
          <div className="col-md-6 p-5 d-flex flex-column justify-content-center bg-white">
            {/* Logo / Brand */}
            <div className="d-flex align-items-center mb-4 gap-2">
              <LocalHospital sx={{ color: "#1e90ff", fontSize: 32 }} />
              <span
                style={{
                  fontWeight: 800,
                  fontSize: "1.2rem",
                  color: "#1e90ff",
                  letterSpacing: "-0.5px",
                }}
              >
                HealthCare
              </span>
            </div>

            <h1
              style={{
                fontWeight: 700,
                fontSize: "1.8rem",
                color: "#1a1a2e",
                marginBottom: "6px",
              }}
            >
              Welcome back 👋
            </h1>
            <p className="text-muted mb-4" style={{ fontSize: "0.9rem" }}>
              Order from drugstores all around the country
            </p>

            {/* Error alert (MUI) */}
            {error && (
              <Alert severity="error" className="mb-3" onClose={() => setError("")}>
                {error}
              </Alert>
            )}

            <form onSubmit={handleSubmit} noValidate>
              {/* MUI TextField for Username */}
              <TextField
                label="Username"
                variant="outlined"
                fullWidth
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                size="medium"
                sx={{ mb: 2.5 }}
              />

              {/* MUI TextField for Password with show/hide toggle */}
              <TextField
                label="Password"
                variant="outlined"
                fullWidth
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                size="medium"
                sx={{ mb: 3 }}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => setShowPassword((prev) => !prev)}
                        edge="end"
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />

              {/* MUI Button with Bootstrap width */}
              <Button
                type="submit"
                variant="contained"
                fullWidth
                size="large"
                disabled={loading}
                sx={{
                  borderRadius: "10px",
                  padding: "13px",
                  fontWeight: 700,
                  fontSize: "1rem",
                  textTransform: "none",
                  backgroundColor: "#1e90ff",
                  boxShadow: "0 4px 15px rgba(30,144,255,0.35)",
                  "&:hover": {
                    backgroundColor: "#0077cc",
                    boxShadow: "0 6px 20px rgba(30,144,255,0.45)",
                  },
                }}
              >
                {loading ? (
                  <CircularProgress size={22} sx={{ color: "white" }} />
                ) : (
                  "Sign In"
                )}
              </Button>
            </form>

            {/* Link to Register */}
            <p className="text-center mt-3 mb-0" style={{ fontSize: "0.875rem", color: "#666" }}>
              Don't have an account?{" "}
              <a href="/register" style={{ color: "#1e90ff", fontWeight: 600, textDecoration: "none" }}>
                Register here
              </a>
            </p>
          </div>

          {/* ── RIGHT: Image ── */}
          <div className="col-md-6 d-none d-md-block">
            <img
              src={doctor}
              alt="Doctor"
              style={{
                width: "100%",
                height: "100%",
                objectFit: "cover",
                filter: "brightness(0.9) contrast(1.05)",
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;
