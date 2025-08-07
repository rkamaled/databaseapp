import React from 'react';
import './DataDisplay.css';

const DataDisplay = ({ data, isLoading }) => {
  if (isLoading) {
    return (
      <div className="data-display">
        <div className="data-header">
          <h2>Results</h2>
          <div className="results-info">
            <span className="loading-spinner"></span>
            <span>Loading...</span>
          </div>
        </div>
        <div className="loading-container">
          <div className="loading-content">
            <div className="loading-spinner large"></div>
            <p>Searching database...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="data-display">
      <div className="data-header">
        <h2>Results</h2>
      </div>

      {Object.keys(data).length > 0 ? (
        <div className="table-container">
          {Object.entries(data).map(([modality, result]) => (
            <div key={modality} className="modality-results">
              <table className="data-table counts-table">
                <thead>
                  <tr>
                    <th>Category</th>
                    <th>Adults</th>
                    <th>Children</th>
                    <th>Total</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><strong>N</strong></td>
                    <td>{result.counts?.adults || 0}</td>
                    <td>{result.counts?.children || 0}</td>
                    <td>{result.counts?.total || 0}</td>
                  </tr>
                  <tr>
                    <td><strong>Male</strong></td>
                    <td>{result.counts?.gender?.adults?.M || 0}</td>
                    <td>{result.counts?.gender?.children?.M || 0}</td>
                    <td>{(result.counts?.gender?.adults?.M || 0) + (result.counts?.gender?.children?.M || 0)}</td>
                  </tr>
                  <tr>
                    <td><strong>Female</strong></td>
                    <td>{result.counts?.gender?.adults?.F || 0}</td>
                    <td>{result.counts?.gender?.children?.F || 0}</td>
                    <td>{(result.counts?.gender?.adults?.F || 0) + (result.counts?.gender?.children?.F || 0)}</td>
                  </tr>
                  <tr>
                    <td><strong>Other</strong></td>
                    <td>{result.counts?.gender?.adults?.O || 0}</td>
                    <td>{result.counts?.gender?.children?.O || 0}</td>
                    <td>{(result.counts?.gender?.adults?.O || 0) + (result.counts?.gender?.children?.O || 0)}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          ))}
        </div>
      ) : (
        <div className="empty-state">
          <div className="empty-icon">📊</div>
          <h3>No data to display</h3>
          <p>Try adjusting your filters or search criteria</p>
        </div>
      )}
    </div>
  );
};

export default DataDisplay; 