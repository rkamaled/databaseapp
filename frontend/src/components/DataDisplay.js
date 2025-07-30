import React from 'react';
import './DataDisplay.css';

const DataDisplay = ({ data, isLoading }) => {
  // Calculate counts
  const calculateCounts = (data) => {
    const counts = {
      adult: {
        total: 0,
        male: 0,
        female: 0
      },
      children: {
        total: 0,
        male: 0,
        female: 0
      },
      total: {
        total: 0,
        male: 0,
        female: 0
      }
    };

    data.forEach(item => {
      const isAdult = item.age >= 18;
      const category = isAdult ? 'adult' : 'children';
      
      // Increment category counts
      counts[category].total++;
      counts[category][item.gender.toLowerCase()]++;
      
      // Increment total counts
      counts.total.total++;
      counts.total[item.gender.toLowerCase()]++;
    });

    return counts;
  };
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
        <div className="results-info">
          {data.length > 0 ? (
            <span>{data.length} record{data.length !== 1 ? 's' : ''} found</span>
          ) : (
            <span>No records found</span>
          )}
        </div>
      </div>

      {data.length > 0 ? (
        <div className="table-container">
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
              {(() => {
                const counts = calculateCounts(data);
                return (
                  <>
                    <tr>
                      <td><strong>N</strong></td>
                      <td>{counts.adult.total}</td>
                      <td>{counts.children.total}</td>
                      <td>{counts.total.total}</td>
                    </tr>
                    <tr>
                      <td><strong>Male</strong></td>
                      <td>{counts.adult.male}</td>
                      <td>{counts.children.male}</td>
                      <td>{counts.total.male}</td>
                    </tr>
                    <tr>
                      <td><strong>Female</strong></td>
                      <td>{counts.adult.female}</td>
                      <td>{counts.children.female}</td>
                      <td>{counts.total.female}</td>
                    </tr>
                  </>
                );
              })()}
            </tbody>
          </table>
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