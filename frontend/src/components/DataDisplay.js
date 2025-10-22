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

  const hasData = Object.keys(data || {}).length > 0;

  // Prefer backend-provided Combined (intersection) if present
  const combined = data && data.Combined && data.Combined.counts ? data.Combined.counts : null;

  // Fallback: Aggregate counts across all modalities/filters into a single table (sum)
  const aggregated = Object.values(data || {}).reduce(
    (acc, entry) => {
      const counts = entry && entry.counts ? entry.counts : {};
      const adults = Number(counts.adults || 0);
      const children = Number(counts.children || 0);
      const total = Number(counts.total || adults + children);

      const gAdults = (counts.gender && counts.gender.adults) || { M: 0, F: 0, O: 0 };
      const gChildren = (counts.gender && counts.gender.children) || { M: 0, F: 0, O: 0 };

      acc.adults += adults;
      acc.children += children;
      acc.total += total;
      acc.gender.adults.M += Number(gAdults.M || 0);
      acc.gender.adults.F += Number(gAdults.F || 0);
      acc.gender.adults.O += Number(gAdults.O || 0);
      acc.gender.children.M += Number(gChildren.M || 0);
      acc.gender.children.F += Number(gChildren.F || 0);
      acc.gender.children.O += Number(gChildren.O || 0);
      return acc;
    },
    {
      adults: 0,
      children: 0,
      total: 0,
      gender: {
        adults: { M: 0, F: 0, O: 0 },
        children: { M: 0, F: 0, O: 0 }
      }
    }
  );

  return (
    <div className="data-display">
      <div className="data-header">
        <h2>Results</h2>
      </div>

      {hasData ? (
        <div className="table-container">
          <div className="modality-results">
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
                  <td>{(combined ? combined.adults : aggregated.adults)}</td>
                  <td>{(combined ? combined.children : aggregated.children)}</td>
                  <td>{(combined ? combined.total : aggregated.total)}</td>
                </tr>
                <tr>
                  <td><strong>Male</strong></td>
                  <td>{(combined ? combined.gender.adults.M : aggregated.gender.adults.M)}</td>
                  <td>{(combined ? combined.gender.children.M : aggregated.gender.children.M)}</td>
                  <td>{(combined ? (combined.gender.adults.M + combined.gender.children.M) : (aggregated.gender.adults.M + aggregated.gender.children.M))}</td>
                </tr>
                <tr>
                  <td><strong>Female</strong></td>
                  <td>{(combined ? combined.gender.adults.F : aggregated.gender.adults.F)}</td>
                  <td>{(combined ? combined.gender.children.F : aggregated.gender.children.F)}</td>
                  <td>{(combined ? (combined.gender.adults.F + combined.gender.children.F) : (aggregated.gender.adults.F + aggregated.gender.children.F))}</td>
                </tr>
                <tr>
                  <td><strong>Other</strong></td>
                  <td>{(combined ? combined.gender.adults.O : aggregated.gender.adults.O)}</td>
                  <td>{(combined ? combined.gender.children.O : aggregated.gender.children.O)}</td>
                  <td>{(combined ? (combined.gender.adults.O + combined.gender.children.O) : (aggregated.gender.adults.O + aggregated.gender.children.O))}</td>
                </tr>
              </tbody>
            </table>
          </div>
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