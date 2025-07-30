import React, { useState } from 'react';
import './FilterSection.css';

const FilterSection = ({ onSearch }) => {
  // State for the 3-level filtering system
  const [filters, setFilters] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [variableSearch, setVariableSearch] = useState('');
  const [selectedCohorts, setSelectedCohorts] = useState([]);

  // Data modalities (Level 1)
  const dataModalities = {
    diet: {
      label: 'Diet Data',
      description: 'Nutritional intake and dietary patterns',
      variables: ['calorie_intake', 'protein_intake', 'carbohydrate_intake', 'fat_intake', 'fiber_intake', 'sugar_intake'],
      variableLabels: {
        calorie_intake: 'Calorie Intake',
        protein_intake: 'Protein Intake',
        carbohydrate_intake: 'Carbohydrate Intake',
        fat_intake: 'Fat Intake',
        fiber_intake: 'Fiber Intake',
        sugar_intake: 'Sugar Intake'
      }
    },
    genetic: {
      label: 'Genetic Data',
      description: 'Genetic markers and variants',
      variables: ['gene_variant_1', 'gene_variant_2', 'risk_score', 'polygenic_score'],
      variableLabels: {
        gene_variant_1: 'Gene Variant 1',
        gene_variant_2: 'Gene Variant 2',
        risk_score: 'Risk Score',
        polygenic_score: 'Polygenic Score'
      }
    },
    anthropometric: {
      label: 'Anthropometric Data',
      description: 'Physical measurements and body composition',
      variables: ['height', 'weight', 'bmi', 'body_fat_percentage', 'muscle_mass', 'waist_circumference'],
      variableLabels: {
        height: 'Height',
        weight: 'Weight',
        bmi: 'BMI',
        body_fat_percentage: 'Body Fat Percentage',
        muscle_mass: 'Muscle Mass',
        waist_circumference: 'Waist Circumference'
      }
    },
    demographic: {
      label: 'Demographic Data',
      description: 'Personal and demographic information',
      variables: ['age', 'gender', 'ethnicity', 'education_level', 'income_level', 'marital_status'],
      variableLabels: {
        age: 'Age',
        gender: 'Gender',
        ethnicity: 'Ethnicity',
        education_level: 'Education Level',
        income_level: 'Income Level',
        marital_status: 'Marital Status'
      }
    }
  };

  // Timepoints (1-6 or all)
  const timepoints = [
    { value: 'all', label: 'All Timepoints' },
    { value: 1, label: 'Timepoint 1' },
    { value: 2, label: 'Timepoint 2' },
    { value: 3, label: 'Timepoint 3' },
    { value: 4, label: 'Timepoint 4' },
    { value: 5, label: 'Timepoint 5' },
    { value: 6, label: 'Timepoint 6' }
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
    { value: 'adult', label: 'Adult' },
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

  // Update logic parameter cohorts
  const updateLogicParameterCohorts = (filterId, logicParamId, cohorts) => {
    setFilters(prev => prev.map(f => 
      f.id === filterId 
        ? { 
            ...f, 
            logicParameters: f.logicParameters.map(lp => 
              lp.id === logicParamId 
                ? { ...lp, cohorts }
                : lp
            )
          }
        : f
    ));
  };

  // Add threshold to logic parameter (Level 3)
  const addThreshold = (filterId, logicParamId) => {
    const newThreshold = {
      id: Date.now(),
      variable: '',
      operator: '',
      value: '',
      value2: '' // For 'between' operator
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

  // Function to filter variables based on search
  const getFilteredVariables = (modality, searchTerm) => {
    if (!searchTerm) return [];
    const variables = dataModalities[modality].variables;
    return variables.filter(variable => 
      dataModalities[modality].variableLabels[variable]
        .toLowerCase()
        .includes(searchTerm.toLowerCase())
    );
  };

  // Handle search submission
  const handleSubmit = (e) => {
    e.preventDefault();
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

    // Simulate API call
    setTimeout(() => {
      onSearch(processedFilters);
      setIsLoading(false);
    }, 1000);
  };

  // Clear all filters
  const handleClear = () => {
    setFilters([]);
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
                  {Object.entries(dataModalities).map(([key, modality]) => (
                    <option key={key} value={key}>
                      {modality.label}
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
                        <label>Cohort:</label>
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
                      </div>

                      {/* Variables Selection */}
                      <div className="param-group">
                        <label>Variables:</label>
                        <div className="variable-search-container">
                          <input
                            type="text"
                            value={variableSearch}
                            onChange={(e) => setVariableSearch(e.target.value)}
                            placeholder="Search variables..."
                            className="variable-search-input"
                          />
                          <div className="variable-search-results">
                            {variableSearch && getFilteredVariables(filter.modality, variableSearch).map(variable => (
                              <div 
                                key={variable} 
                                className="variable-search-item"
                                onClick={() => {
                                  if (!logicParam.variables.includes(variable)) {
                                    updateLogicParameterVariables(
                                      filter.id, 
                                      logicParam.id, 
                                      [...logicParam.variables, variable]
                                    );
                                  }
                                  setVariableSearch('');
                                }}
                              >
                                {dataModalities[filter.modality].variableLabels[variable]}
                              </div>
                            ))}
                          </div>
                        </div>
                        <div className="selected-variables">
                          {logicParam.variables.map(variable => (
                            <div key={variable} className="selected-variable-tag">
                              {dataModalities[filter.modality].variableLabels[variable]}
                              <button
                                type="button"
                                onClick={() => {
                                  updateLogicParameterVariables(
                                    filter.id,
                                    logicParam.id,
                                    logicParam.variables.filter(v => v !== variable)
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
                        <label>Timepoints:</label>
                        <div className="checkbox-group">
                          {timepoints.map(timepoint => (
                            <label key={timepoint.value} className="checkbox-label">
                              <input
                                type="checkbox"
                                checked={logicParam.timepoints.includes(timepoint.value)}
                                onChange={(e) => {
                                  const newTimepoints = e.target.checked
                                    ? [...logicParam.timepoints, timepoint.value]
                                    : logicParam.timepoints.filter(t => t !== timepoint.value);
                                  updateLogicParameterTimepoints(filter.id, logicParam.id, newTimepoints);
                                }}
                              />
                              {timepoint.label}
                            </label>
                          ))}
                        </div>
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
                                value={threshold.variable}
                                onChange={(e) => updateThreshold(filter.id, logicParam.id, threshold.id, 'variable', e.target.value)}
                                className="variable-select"
                              >
                                <option value="">Select Variable...</option>
                                {logicParam.variables.map(variable => (
                                  <option key={variable} value={variable}>
                                    {dataModalities[filter.modality].variableLabels[variable]}
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
                              >
                                <option value="">Operator...</option>
                                {thresholdOperators.map(op => (
                                  <option key={op.value} value={op.value}>
                                    {op.label}
                                  </option>
                                ))}
                              </select>

                              <input
                                type="number"
                                value={threshold.value}
                                onChange={(e) => updateThreshold(filter.id, logicParam.id, threshold.id, 'value', e.target.value)}
                                placeholder="Value"
                                className="threshold-input"
                              />

                              {threshold.operator === 'between' && (
                                <input
                                  type="number"
                                  value={threshold.value2}
                                  onChange={(e) => updateThreshold(filter.id, logicParam.id, threshold.id, 'value2', e.target.value)}
                                  placeholder="Second value"
                                  className="threshold-input"
                                />
                              )}
                            </div>
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
            disabled={isLoading || filters.length === 0}
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