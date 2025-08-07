import React, { useState, useEffect } from 'react';
import './App.css';
import FilterSection from './components/FilterSection';
import DataDisplay from './components/DataDisplay';
import logo from './logo.jpg';
import { API_BASE_URL } from './config';

function App() {
  const [filteredData, setFilteredData] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    // Check if user previously set a theme preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
      setIsDarkMode(true);
      document.body.classList.add('dark-mode');
    }
  }, []);

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('theme', !isDarkMode ? 'dark' : 'light');
  };

  const handleSearch = async (filters) => {
    setIsLoading(true);
    
    try {
      const response = await fetch(`${API_BASE_URL}/query-data`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ filters }),
      });

      const data = await response.json();
      
      if (data.status === 'success') {
        setFilteredData(data.results);
      } else {
        console.error('Error:', data.message);
        setFilteredData({});
      }
    } catch (error) {
      console.error('Error:', error);
      setFilteredData({});
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="app-header">
        <div className="header-content">
          <div className="logo-section">
            <img src={logo} alt="Database Viewer Logo" className="header-logo" />
          </div>
          <div className="header-text">
            <h1>GFHS Database Viewer</h1>
            <p>Filter and view your data with filtering system</p>
          </div>
          <button 
            className={`theme-toggle ${isDarkMode ? 'dark' : 'light'}`} 
            onClick={toggleTheme}
            aria-label="Toggle dark mode"
          >
            <span className="sun-icon">☀️</span>
            <span className="moon-icon">🌙</span>
          </button>
        </div>
      </header>
      
      <main className="app-main">
        <div className="app-container">
          <FilterSection onSearch={handleSearch} />
          <DataDisplay data={filteredData} isLoading={isLoading} />
        </div>
      </main>
    </div>
  );
}

export default App;