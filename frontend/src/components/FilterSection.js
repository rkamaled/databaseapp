import React, { useState, useEffect } from 'react';
import './FilterSection.css';
import { API_BASE_URL } from '../config';

const FilterSection = ({ onSearch }) => {
  // State for the 3-level filtering system
  const [filters, setFilters] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [variableSearch, setVariableSearch] = useState('');
  const [selectedCohorts, setSelectedCohorts] = useState([]);

  // State for available modalities and variables
  const [availableModalities, setAvailableModalities] = useState([]);
  const [availableVariables, setAvailableVariables] = useState({});  // Store variables by modality and cohort

  // Fetch modalities from backend
  useEffect(() => {
    fetch(`${API_BASE_URL}/get-modalities`)
      .then(response => response.json())
      .then(data => {
        if (data.status === 'success') {
          setAvailableModalities(data.modalities);
        }
      })
      .catch(error => console.error('Error fetching modalities:', error));
  }, []);

  // Timepoints (1-9 or all)
  const timepoints = [
    { value: 'all', label: 'All Timepoints' },
    { value: 1, label: 'Timepoint 1' },
    { value: 2, label: 'Timepoint 2' },
    { value: 3, label: 'Timepoint 3' },
    { value: 4, label: 'Timepoint 4' },
    { value: 5, label: 'Timepoint 5' },
    { value: 6, label: 'Timepoint 6' },
    { value: 7, label: 'Timepoint 7' },
    { value: 8, label: 'Timepoint 8' },
    { value: 9, label: 'Timepoint 9' }
  ];

  // Threshold operators
  const thresholdOperators = [
    { value: '=', label: 'Equals' },
    { value: '>', label: 'Greater than' },
    { value: '<', label: 'Less than' },
    { value: '>=', label: 'Greater than or equal' },
    { value: '<=', label: 'Less than or equal' },
    { value: '!=', label: 'Not equal' },
    { value: 'between', label: 'Between' }
  ];

  // Add a new filter (Level 1)
  const addFilter = () => {
    const newFilter = {
      id: Date.now(),
      modality: '',
      logicParameters: []
    };
    setFilters(prev => [...prev, newFilter]);
  };

  // Remove a filter
  const removeFilter = (filterId) => {
    setFilters(prev => prev.filter(f => f.id !== filterId));
  };

  // Update filter modality
  const updateFilterModality = (filterId, modality) => {
    setFilters(prev => prev.map(f => 
      f.id === filterId 
        ? { ...f, modality, logicParameters: [] } // Reset logic parameters when modality changes
        : f
    ));
  };

  // Add logic parameter to a filter (Level 2)
  // Cohort options
  const cohortOptions = [
    { value: 'adults', label: 'Adults' },
    { value: 'children', label: 'Children' }
  ];

  const addLogicParameter = (filterId) => {
    const newLogicParameter = {
      id: Date.now(),
      variables: [],
      timepoints: [],
      thresholds: [],
      cohorts: []
    };
    
    setFilters(prev => prev.map(f => 
      f.id === filterId 
        ? { ...f, logicParameters: [newLogicParameter] } // Only allow one logic parameter
        : f
    ));
  };

  // Remove logic parameter
  const removeLogicParameter = (filterId, logicParamId) => {
    setFilters(prev => prev.map(f => 
      f.id === filterId 
        ? { ...f, logicParameters: [] } // Remove the logic parameter completely
        : f
    ));
  };

  // Update logic parameter variables
  const updateLogicParameterVariables = (filterId, logicParamId, variables) => {
    setFilters(prev => prev.map(f => 
      f.id === filterId 
        ? { 
            ...f, 
            logicParameters: f.logicParameters.map(lp => 
              lp.id === logicParamId 
                ? { ...lp, variables }
                : lp
            )
          }
        : f
    ));
  };

  // Update logic parameter timepoints
  const updateLogicParameterTimepoints = (filterId, logicParamId, timepoints) => {
    setFilters(prev => prev.map(f => 
      f.id === filterId 
        ? { 
            ...f, 
            logicParameters: f.logicParameters.map(lp => 
              lp.id === logicParamId 
                ? { ...lp, timepoints }
                : lp
            )
          }
        : f
    ));
  };

  // Handle timepoint selection with "All Timepoints" logic
  const handleTimepointChange = (filterId, logicParamId, currentTimepoints, timepointValue, isChecked) => {
    let newTimepoints;
    
    if (timepointValue === 'all') {
      // If "All Timepoints" is being selected, clear other selections
      if (isChecked) {
        newTimepoints = ['all'];
      } else {
        newTimepoints = [];
      }
    } else {
      // If individual timepoint is being selected
      if (isChecked) {
        // Remove 'all' if it was selected and add the individual timepoint
        newTimepoints = currentTimepoints.filter(t => t !== 'all');
        if (!newTimepoints.includes(timepointValue)) {
          newTimepoints.push(timepointValue);
        }
      } else {
        // Remove the individual timepoint
        newTimepoints = currentTimepoints.filter(t => t !== timepointValue);
      }
    }
    
    updateLogicParameterTimepoints(filterId, logicParamId, newTimepoints);
  };

  // Update logic parameter cohorts
  const updateLogicParameterCohorts = (filterId, logicParamId, cohorts) => {
    setFilters(prev => prev.map(f => {
      if (f.id === filterId) {
        // Get the modality for this filter
        const modality = f.modality;
        
        // For each selected cohort, fetch variables if we haven't already
        cohorts.forEach(cohort => {
          const key = `${modality}-${cohort}`;
          if (!availableVariables[key]) {
            fetchVariables(modality, cohort);
          }
        });

        return { 
          ...f, 
          logicParameters: f.logicParameters.map(lp => 
            lp.id === logicParamId 
              ? { ...lp, cohorts, variables: [] }  // Reset variables when cohorts change
              : lp
          )
        };
      }
      return f;
    }));
  };

  // Add threshold to logic parameter (Level 3)
  const addThreshold = (filterId, logicParamId) => {
    const newThreshold = {
      id: Date.now(),
      variable: '',
      operator: '',
      value: '',
      value2: '', // For 'between' operator
      cohortScope: '' // 'adults' | 'children' | 'both' (optional)
    };
    
    setFilters(prev => prev.map(f => 
      f.id === filterId 
        ? { 
            ...f, 
            logicParameters: f.logicParameters.map(lp => 
              lp.id === logicParamId 
                ? { ...lp, thresholds: [...lp.thresholds, newThreshold] }
                : lp
            )
          }
        : f
    ));
  };

  // Remove threshold
  const removeThreshold = (filterId, logicParamId, thresholdId) => {
    setFilters(prev => prev.map(f => 
      f.id === filterId 
        ? { 
            ...f, 
            logicParameters: f.logicParameters.map(lp => 
              lp.id === logicParamId 
                ? { ...lp, thresholds: lp.thresholds.filter(t => t.id !== thresholdId) }
                : lp
            )
          }
        : f
    ));
  };

  // Update threshold
  const updateThreshold = (filterId, logicParamId, thresholdId, field, value) => {
    setFilters(prev => prev.map(f => 
      f.id === filterId 
        ? { 
            ...f, 
            logicParameters: f.logicParameters.map(lp => 
              lp.id === logicParamId 
                ? { 
                    ...lp, 
                    thresholds: lp.thresholds.map(t => 
                      t.id === thresholdId 
                        ? { ...t, [field]: value }
                        : t
                    )
                  }
                : lp
            )
          }
        : f
    ));
  };

  // Function to get variables from backend based on modality and cohort
  const fetchVariables = async (modality, cohortType) => {
    try {
      const response = await fetch(`${API_BASE_URL}/get-variables/${modality}/${cohortType}`);
      const data = await response.json();
      if (data.status === 'success') {
        setAvailableVariables(prev => ({
          ...prev,
          [`${modality}-${cohortType}`]: data.variables
        }));
      }
    } catch (error) {
      console.error('Error fetching variables:', error);
    }
  };

  // Function to filter variables based on search
  const getFilteredVariables = (modality, cohortType, searchTerm) => {
    if (!searchTerm || !cohortType) return [];
    const variables = availableVariables[`${modality}-${cohortType}`] || [];
    return variables.filter(variable => 
      variable.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
  };

  // Handle search submission
  const handleSubmit = (e) => {
    e.preventDefault();
    if (isSearchDisabled()) {
      return;
    }
    setIsLoading(true);
    
    // Convert the hierarchical filters to a format that can be processed
    const processedFilters = filters.map(filter => ({
      modality: filter.modality,
      logicParameters: filter.logicParameters.map(lp => ({
        variables: lp.variables,
        timepoints: lp.timepoints,
        thresholds: lp.thresholds,
        cohorts: lp.cohorts
      }))
    }));

    // Send the search request immediately
    onSearch(processedFilters);
    setIsLoading(false);
  };

  // Clear all filters
  const handleClear = () => {
    setFilters([]);
  };

  // Check if search should be disabled
  const isSearchDisabled = () => {
    if (filters.length === 0) return true;
    // Require at least one logic parameter to be added for every filter
    return filters.some(filter => !filter.logicParameters || filter.logicParameters.length === 0);
  };

  return (
    <div className="filter-section">
      <div className="filter-header">
        <h2>Advanced Filter Builder</h2>
      </div>
      
      <form onSubmit={handleSubmit} className="filter-form">
        {/* Level 1: Add Filters */}
        <div className="filter-level">
          
          <button 
            type="button" 
            onClick={addFilter} 
            className="btn btn-primary add-filter-btn"
          >
            + Add Filter
          </button>

          {filters.map((filter) => (
            <div key={filter.id} className="filter-card">
              <button
                type="button"
                onClick={() => removeFilter(filter.id)}
                className="remove-btn filter-close-btn"
              >
                ×
              </button>
              
              <div className="filter-card-header">
                <select
                  value={filter.modality}
                  onChange={(e) => updateFilterModality(filter.id, e.target.value)}
                  className="modality-select"
                >
                  <option value="">Select Data Modality...</option>
                  {availableModalities.map(modality => (
                    <option key={modality} value={modality}>
                      {modality}
                    </option>
                  ))}
                </select>
              </div>

              {/* Level 2: Logic Parameters */}
              {filter.modality && (
                <div className="logic-parameters-section">
                  
                  {filter.logicParameters.length === 0 && (
                    <button 
                      type="button" 
                      onClick={() => addLogicParameter(filter.id)} 
                      className="btn btn-secondary add-logic-param-btn"
                    >
                      + Add Logic Parameter
                    </button>
                  )}

                  {filter.logicParameters.map((logicParam) => (
                    <div key={logicParam.id} className="logic-parameter-card">
                      <div className="logic-param-header">
                        <h5>Logic Parameter</h5>
                        <button
                          type="button"
                          onClick={() => removeLogicParameter(filter.id, logicParam.id)}
                          className="remove-btn small"
                        >
                          ×
                        </button>
                      </div>
                      {/* Cohort Selection */}
                      <div className="param-group">
                        <label>Cohort: <span className="required-field">*</span></label>
                        <div className="checkbox-group">
                          {cohortOptions.map(cohort => (
                            <label key={cohort.value} className="checkbox-label">
                              <input
                                type="checkbox"
                                checked={logicParam.cohorts.includes(cohort.value)}
                                onChange={(e) => {
                                  const newCohorts = e.target.checked
                                    ? [...logicParam.cohorts, cohort.value]
                                    : logicParam.cohorts.filter(c => c !== cohort.value);
                                  updateLogicParameterCohorts(filter.id, logicParam.id, newCohorts);
                                }}
                              />
                              {cohort.label}
                            </label>
                          ))}
                        </div>
                        {logicParam.cohorts.length === 0 && (
                          <div className="validation-message">Please select at least one cohort</div>
                        )}
                      </div>

                      {/* Variables Selection */}
                      <div className="param-group">

                      {/* Zach - Include UI elements specific for genetic modality when modality === genetics, as it is unique compared to the rest of the modalities and requires the text input drop down.
                      
                      - use "snp_input" as the logic param for this, as I've named it this in the query_data function in main app.py
                      
                      */}





                        <label>Variables:</label>
                        <div className="variable-search-container">
                          <input
                            type="text"
                            value={variableSearch}
                            onChange={(e) => setVariableSearch(e.target.value)}
                            placeholder={logicParam.cohorts.length === 0 ? "Select cohort first..." : "Search variables..."}
                            className="variable-search-input"
                            disabled={logicParam.cohorts.length === 0}
                          />
                          <div className="variable-search-results">
                            {variableSearch && logicParam.cohorts.map(cohort => (
                              <div key={cohort} className="cohort-variables-group">
                                <h6>{cohort === 'children' ? 'Child Variables' : 'Adults Variables'}</h6>
                                <div className="variable-list">
                                      {getFilteredVariables(filter.modality, cohort, variableSearch).map(variable => (
                                    <div 
                                      key={variable.name} 
                                      className="variable-search-item"
                                      onClick={() => {
                                        if (!logicParam.variables.find(v => v.name === variable.name && v.cohort === variable.cohort)) {
                                          updateLogicParameterVariables(
                                            filter.id, 
                                            logicParam.id, 
                                            [...logicParam.variables, variable]
                                          );
                                        }
                                        setVariableSearch('');
                                      }}
                                    >
                                      {variable.name}
                                    </div>
                                  ))}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                        <div className="selected-variables">
                          {logicParam.variables.map(variable => (
                            <div key={`${variable.cohort}:${variable.name}`} className="selected-variable-tag">
                              {variable.name}
                              <span className="cohort-badge">{variable.cohort === 'children' ? 'Child' : 'Adult'}</span>
                              <button
                                type="button"
                                onClick={() => {
                                  updateLogicParameterVariables(
                                    filter.id,
                                    logicParam.id,
                                        logicParam.variables.filter(v => !(v.name === variable.name && v.cohort === variable.cohort))
                                  );
                                }}
                                className="remove-variable-btn"
                              >
                                ×
                              </button>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Timepoints Selection */}
                      <div className="param-group">
                        <label>Timepoints: <span className="required-field">*</span></label>
                        <div className="checkbox-group">
                          {timepoints.map(timepoint => (
                            <label key={timepoint.value} className="checkbox-label">
                              <input
                                type="checkbox"
                                checked={logicParam.timepoints.includes(timepoint.value)}
                                onChange={(e) => {
                                  handleTimepointChange(
                                    filter.id, 
                                    logicParam.id, 
                                    logicParam.timepoints, 
                                    timepoint.value, 
                                    e.target.checked
                                  );
                                }}
                              />
                              {timepoint.label}
                            </label>
                          ))}
                        </div>
                        {logicParam.timepoints.length === 0 && (
                          <div className="validation-message">Please select at least one timepoint</div>
                        )}
                      </div>

                      {/* Level 3: Thresholds */}
                      <div className="thresholds-section">
                        <div className="level-header">
                          <h6>Thresholds</h6>
                          <p>Set conditions for variables</p>
                        </div>
                        
                        <button 
                          type="button" 
                          onClick={() => addThreshold(filter.id, logicParam.id)} 
                          className="btn btn-tertiary add-threshold-btn"
                        >
                          + Add Threshold
                        </button>

                        {logicParam.thresholds.map((threshold) => (
                          <div key={threshold.id} className="threshold-card">
                            <div className="threshold-header">
                              <select
                                value={threshold.variable ? threshold.variable.name : ''}
                                onChange={(e) => {
                                  const selectedName = e.target.value;
                                  const candidates = logicParam.variables.filter(v => v.name === selectedName);
                                  const preferred = candidates.find(v => v.cohort === 'adults') || candidates[0];
                                  updateThreshold(filter.id, logicParam.id, threshold.id, 'variable', preferred);
                                  // Reset operator when variable changes
                                  updateThreshold(filter.id, logicParam.id, threshold.id, 'operator', '');
                                  // Set cohort scope based on availability
                                  const hasAdults = candidates.some(v => v.cohort === 'adults');
                                  const hasChildren = candidates.some(v => v.cohort === 'children');
                                  const scope = hasAdults && hasChildren ? 'both' : (preferred.cohort || '');
                                  updateThreshold(filter.id, logicParam.id, threshold.id, 'cohortScope', scope);
                                }}
                                className="variable-select"
                              >
                                <option value="">Select Variable...</option>
                                {Array.from(new Set(logicParam.variables.map(v => v.name))).map(name => (
                                  <option key={name} value={name}>
                                    {name}
                                  </option>
                                ))}
                              </select>
                              <button
                                type="button"
                                onClick={() => removeThreshold(filter.id, logicParam.id, threshold.id)}
                                className="remove-btn small"
                              >
                                ×
                              </button>
                            </div>

                            <div className="threshold-controls">
                              <select
                                value={threshold.operator}
                                onChange={(e) => updateThreshold(filter.id, logicParam.id, threshold.id, 'operator', e.target.value)}
                                className="operator-select"
                                disabled={!threshold.variable}
                              >
                                <option value="">Operator...</option>
                                {threshold.variable && threshold.variable.operators.map(op => (
                                  <option key={op.value} value={op.value}>
                                    {op.label}
                                  </option>
                                ))}
                              </select>

                              {threshold.variable && threshold.operator && threshold.operator !== 'IS NULL' && threshold.operator !== 'IS NOT NULL' && (
                                <input
                                  type={threshold.variable.type === 'number' ? 'number' : threshold.variable.type === 'datetime' ? 'datetime-local' : 'text'}
                                  value={threshold.value}
                                  onChange={(e) => updateThreshold(filter.id, logicParam.id, threshold.id, 'value', e.target.value)}
                                  placeholder="Value"
                                  className="threshold-input"
                                />
                              )}

                              {threshold.variable && threshold.operator === 'between' && (
                                <input
                                  type={threshold.variable.type === 'number' ? 'number' : threshold.variable.type === 'datetime' ? 'datetime-local' : 'text'}
                                  value={threshold.value2}
                                  onChange={(e) => updateThreshold(filter.id, logicParam.id, threshold.id, 'value2', e.target.value)}
                                  placeholder="Second value"
                                  className="threshold-input"
                                />
                              )}
                            </div>

                            {/* Cohort scope selector when the same variable exists in both cohorts */}
                            {(() => {
                              const selectedName = threshold.variable ? threshold.variable.name : null;
                              const candidates = selectedName ? logicParam.variables.filter(v => v.name === selectedName) : [];
                              const hasAdults = candidates.some(v => v.cohort === 'adults');
                              const hasChildren = candidates.some(v => v.cohort === 'children');
                              if (selectedName && hasAdults && hasChildren) {
                                const scope = threshold.cohortScope || 'both';
                                return (
                                  <div className="cohort-scope-selector">
                                    <label className="label-text">Apply to cohort:</label>
                                    <label className="radio-label">
                                      <input
                                        type="radio"
                                        checked={scope === 'adults'}
                                        onChange={() => {
                                          const adultsVar = candidates.find(v => v.cohort === 'adults');
                                          if (adultsVar) {
                                            updateThreshold(filter.id, logicParam.id, threshold.id, 'variable', adultsVar);
                                          }
                                          updateThreshold(filter.id, logicParam.id, threshold.id, 'cohortScope', 'adults');
                                        }}
                                      />
                                      <span>Adults</span>
                                    </label>
                                    <label className="radio-label">
                                      <input
                                        type="radio"
                                        checked={scope === 'children'}
                                        onChange={() => {
                                          const childVar = candidates.find(v => v.cohort === 'children');
                                          if (childVar) {
                                            updateThreshold(filter.id, logicParam.id, threshold.id, 'variable', childVar);
                                          }
                                          updateThreshold(filter.id, logicParam.id, threshold.id, 'cohortScope', 'children');
                                        }}
                                      />
                                      <span>Children</span>
                                    </label>
                                    <label className="radio-label">
                                      <input
                                        type="radio"
                                        checked={scope === 'both'}
                                        onChange={() => {
                                          updateThreshold(filter.id, logicParam.id, threshold.id, 'cohortScope', 'both');
                                        }}
                                      />
                                      <span>Both</span>
                                    </label>
                                  </div>
                                );
                              }
                              return null;
                            })()}
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="filter-actions">
          <button 
            type="submit" 
            className="btn btn-primary"
            disabled={isLoading || isSearchDisabled()}
          >
            {isLoading ? 'Searching...' : 'Search'}
          </button>
          <button type="button" onClick={handleClear} className="btn btn-secondary">
            Clear All
          </button>
        </div>
      </form>
    </div>
  );
};

export default FilterSection; 