import React, { useState } from 'react';
import './App.css';
import FilterSection from './components/FilterSection';
import DataDisplay from './components/DataDisplay';
import logo from './logo.jpg';

function App() {
  const [filteredData, setFilteredData] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSearch = (filters) => {
    setIsLoading(true);
    
    // Simulate API call with setTimeout
    setTimeout(() => {
      // Mock data with multiple data modalities and timepoints
      const mockData = [
        {
          id: 1,
          name: 'John Doe',
          email: 'john@example.com',
          // Demographic data
          age: 35,
          gender: 'Male',
          ethnicity: 'White',
          education_level: 'Bachelor',
          income_level: 'Middle',
          marital_status: 'Married',
          // Anthropometric data (multiple timepoints)
          anthropometric: {
            1: { height: 175, weight: 70, bmi: 22.9, body_fat_percentage: 15, muscle_mass: 55, waist_circumference: 80 },
            2: { height: 175, weight: 72, bmi: 23.5, body_fat_percentage: 16, muscle_mass: 54, waist_circumference: 82 },
            3: { height: 175, weight: 71, bmi: 23.2, body_fat_percentage: 15.5, muscle_mass: 55, waist_circumference: 81 },
            4: { height: 175, weight: 73, bmi: 23.8, body_fat_percentage: 17, muscle_mass: 53, waist_circumference: 83 },
            5: { height: 175, weight: 74, bmi: 24.2, body_fat_percentage: 18, muscle_mass: 52, waist_circumference: 84 },
            6: { height: 175, weight: 75, bmi: 24.5, body_fat_percentage: 19, muscle_mass: 51, waist_circumference: 85 }
          },
          // Diet data (multiple timepoints)
          diet: {
            1: { calorie_intake: 2200, protein_intake: 150, carbohydrate_intake: 250, fat_intake: 80, fiber_intake: 25, sugar_intake: 50 },
            2: { calorie_intake: 2100, protein_intake: 140, carbohydrate_intake: 240, fat_intake: 75, fiber_intake: 23, sugar_intake: 45 },
            3: { calorie_intake: 2000, protein_intake: 130, carbohydrate_intake: 230, fat_intake: 70, fiber_intake: 22, sugar_intake: 40 },
            4: { calorie_intake: 1900, protein_intake: 125, carbohydrate_intake: 220, fat_intake: 65, fiber_intake: 20, sugar_intake: 35 },
            5: { calorie_intake: 1800, protein_intake: 120, carbohydrate_intake: 210, fat_intake: 60, fiber_intake: 18, sugar_intake: 30 },
            6: { calorie_intake: 1700, protein_intake: 115, carbohydrate_intake: 200, fat_intake: 55, fiber_intake: 16, sugar_intake: 25 }
          },
          // Genetic data
          genetic: {
            gene_variant_1: 'AA',
            gene_variant_2: 'GG',
            risk_score: 0.3,
            polygenic_score: 0.45
          }
        },
        {
          id: 2,
          name: 'Jane Smith',
          email: 'jane@example.com',
          // Demographic data
          age: 28,
          gender: 'Female',
          ethnicity: 'Black',
          education_level: 'Master',
          income_level: 'Upper',
          marital_status: 'Single',
          // Anthropometric data
          anthropometric: {
            1: { height: 165, weight: 60, bmi: 22.0, body_fat_percentage: 22, muscle_mass: 45, waist_circumference: 70 },
            2: { height: 165, weight: 58, bmi: 21.3, body_fat_percentage: 20, muscle_mass: 46, waist_circumference: 68 },
            3: { height: 165, weight: 57, bmi: 20.9, body_fat_percentage: 19, muscle_mass: 47, waist_circumference: 67 },
            4: { height: 165, weight: 56, bmi: 20.6, body_fat_percentage: 18, muscle_mass: 48, waist_circumference: 66 },
            5: { height: 165, weight: 55, bmi: 20.2, body_fat_percentage: 17, muscle_mass: 49, waist_circumference: 65 },
            6: { height: 165, weight: 54, bmi: 19.8, body_fat_percentage: 16, muscle_mass: 50, waist_circumference: 64 }
          },
          // Diet data
          diet: {
            1: { calorie_intake: 1800, protein_intake: 120, carbohydrate_intake: 200, fat_intake: 60, fiber_intake: 20, sugar_intake: 30 },
            2: { calorie_intake: 1700, protein_intake: 115, carbohydrate_intake: 190, fat_intake: 55, fiber_intake: 18, sugar_intake: 25 },
            3: { calorie_intake: 1600, protein_intake: 110, carbohydrate_intake: 180, fat_intake: 50, fiber_intake: 16, sugar_intake: 20 },
            4: { calorie_intake: 1500, protein_intake: 105, carbohydrate_intake: 170, fat_intake: 45, fiber_intake: 14, sugar_intake: 15 },
            5: { calorie_intake: 1400, protein_intake: 100, carbohydrate_intake: 160, fat_intake: 40, fiber_intake: 12, sugar_intake: 10 },
            6: { calorie_intake: 1300, protein_intake: 95, carbohydrate_intake: 150, fat_intake: 35, fiber_intake: 10, sugar_intake: 5 }
          },
          // Genetic data
          genetic: {
            gene_variant_1: 'AG',
            gene_variant_2: 'GT',
            risk_score: 0.5,
            polygenic_score: 0.62
          }
        },
        {
          id: 3,
          name: 'Bob Johnson',
          email: 'bob@example.com',
          // Demographic data
          age: 42,
          gender: 'Male',
          ethnicity: 'Hispanic',
          education_level: 'High School',
          income_level: 'Lower',
          marital_status: 'Divorced',
          // Anthropometric data
          anthropometric: {
            1: { height: 180, weight: 85, bmi: 26.2, body_fat_percentage: 25, muscle_mass: 60, waist_circumference: 95 },
            2: { height: 180, weight: 88, bmi: 27.2, body_fat_percentage: 27, muscle_mass: 58, waist_circumference: 98 },
            3: { height: 180, weight: 90, bmi: 27.8, body_fat_percentage: 29, muscle_mass: 56, waist_circumference: 100 },
            4: { height: 180, weight: 92, bmi: 28.4, body_fat_percentage: 31, muscle_mass: 54, waist_circumference: 102 },
            5: { height: 180, weight: 95, bmi: 29.3, body_fat_percentage: 33, muscle_mass: 52, waist_circumference: 105 },
            6: { height: 180, weight: 98, bmi: 30.2, body_fat_percentage: 35, muscle_mass: 50, waist_circumference: 108 }
          },
          // Diet data
          diet: {
            1: { calorie_intake: 2800, protein_intake: 180, carbohydrate_intake: 320, fat_intake: 100, fiber_intake: 15, sugar_intake: 80 },
            2: { calorie_intake: 2900, protein_intake: 185, carbohydrate_intake: 330, fat_intake: 105, fiber_intake: 14, sugar_intake: 85 },
            3: { calorie_intake: 3000, protein_intake: 190, carbohydrate_intake: 340, fat_intake: 110, fiber_intake: 13, sugar_intake: 90 },
            4: { calorie_intake: 3100, protein_intake: 195, carbohydrate_intake: 350, fat_intake: 115, fiber_intake: 12, sugar_intake: 95 },
            5: { calorie_intake: 3200, protein_intake: 200, carbohydrate_intake: 360, fat_intake: 120, fiber_intake: 11, sugar_intake: 100 },
            6: { calorie_intake: 3300, protein_intake: 205, carbohydrate_intake: 370, fat_intake: 125, fiber_intake: 10, sugar_intake: 105 }
          },
          // Genetic data
          genetic: {
            gene_variant_1: 'GG',
            gene_variant_2: 'TT',
            risk_score: 0.7,
            polygenic_score: 0.78
          }
        },
        {
          id: 4,
          name: 'Alice Brown',
          email: 'alice@example.com',
          // Demographic data
          age: 31,
          gender: 'Female',
          ethnicity: 'Asian',
          education_level: 'PhD',
          income_level: 'Upper',
          marital_status: 'Married',
          // Anthropometric data
          anthropometric: {
            1: { height: 160, weight: 55, bmi: 21.5, body_fat_percentage: 18, muscle_mass: 42, waist_circumference: 65 },
            2: { height: 160, weight: 54, bmi: 21.1, body_fat_percentage: 17, muscle_mass: 43, waist_circumference: 64 },
            3: { height: 160, weight: 53, bmi: 20.7, body_fat_percentage: 16, muscle_mass: 44, waist_circumference: 63 },
            4: { height: 160, weight: 52, bmi: 20.3, body_fat_percentage: 15, muscle_mass: 45, waist_circumference: 62 },
            5: { height: 160, weight: 51, bmi: 19.9, body_fat_percentage: 14, muscle_mass: 46, waist_circumference: 61 },
            6: { height: 160, weight: 50, bmi: 19.5, body_fat_percentage: 13, muscle_mass: 47, waist_circumference: 60 }
          },
          // Diet data
          diet: {
            1: { calorie_intake: 1600, protein_intake: 110, carbohydrate_intake: 180, fat_intake: 55, fiber_intake: 22, sugar_intake: 25 },
            2: { calorie_intake: 1550, protein_intake: 108, carbohydrate_intake: 175, fat_intake: 52, fiber_intake: 21, sugar_intake: 22 },
            3: { calorie_intake: 1500, protein_intake: 105, carbohydrate_intake: 170, fat_intake: 50, fiber_intake: 20, sugar_intake: 20 },
            4: { calorie_intake: 1450, protein_intake: 102, carbohydrate_intake: 165, fat_intake: 48, fiber_intake: 19, sugar_intake: 18 },
            5: { calorie_intake: 1400, protein_intake: 100, carbohydrate_intake: 160, fat_intake: 45, fiber_intake: 18, sugar_intake: 15 },
            6: { calorie_intake: 1350, protein_intake: 98, carbohydrate_intake: 155, fat_intake: 42, fiber_intake: 17, sugar_intake: 12 }
          },
          // Genetic data
          genetic: {
            gene_variant_1: 'AA',
            gene_variant_2: 'CC',
            risk_score: 0.2,
            polygenic_score: 0.35
          }
        },
        {
          id: 5,
          name: 'Charlie Wilson',
          email: 'charlie@example.com',
          // Demographic data
          age: 45,
          gender: 'Male',
          ethnicity: 'White',
          education_level: 'Bachelor',
          income_level: 'Middle',
          marital_status: 'Married',
          // Anthropometric data
          anthropometric: {
            1: { height: 178, weight: 82, bmi: 25.9, body_fat_percentage: 20, muscle_mass: 62, waist_circumference: 88 },
            2: { height: 178, weight: 84, bmi: 26.5, body_fat_percentage: 22, muscle_mass: 60, waist_circumference: 90 },
            3: { height: 178, weight: 86, bmi: 27.1, body_fat_percentage: 24, muscle_mass: 58, waist_circumference: 92 },
            4: { height: 178, weight: 88, bmi: 27.8, body_fat_percentage: 26, muscle_mass: 56, waist_circumference: 94 },
            5: { height: 178, weight: 90, bmi: 28.4, body_fat_percentage: 28, muscle_mass: 54, waist_circumference: 96 },
            6: { height: 178, weight: 92, bmi: 29.0, body_fat_percentage: 30, muscle_mass: 52, waist_circumference: 98 }
          },
          // Diet data
          diet: {
            1: { calorie_intake: 2400, protein_intake: 160, carbohydrate_intake: 280, fat_intake: 85, fiber_intake: 28, sugar_intake: 60 },
            2: { calorie_intake: 2350, protein_intake: 158, carbohydrate_intake: 275, fat_intake: 83, fiber_intake: 27, sugar_intake: 58 },
            3: { calorie_intake: 2300, protein_intake: 155, carbohydrate_intake: 270, fat_intake: 80, fiber_intake: 26, sugar_intake: 55 },
            4: { calorie_intake: 2250, protein_intake: 152, carbohydrate_intake: 265, fat_intake: 78, fiber_intake: 25, sugar_intake: 52 },
            5: { calorie_intake: 2200, protein_intake: 150, carbohydrate_intake: 260, fat_intake: 75, fiber_intake: 24, sugar_intake: 50 },
            6: { calorie_intake: 2150, protein_intake: 148, carbohydrate_intake: 255, fat_intake: 73, fiber_intake: 23, sugar_intake: 48 }
          },
          // Genetic data
          genetic: {
            gene_variant_1: 'AG',
            gene_variant_2: 'CT',
            risk_score: 0.4,
            polygenic_score: 0.52
          }
        }
      ];

      // Apply hierarchical filters
      let filtered = mockData;
      
      filters.forEach(filter => {
        const { modality, logicParameters } = filter;
        
        filtered = filtered.filter(item => {
          // Check if item has the required modality data
          if (!item[modality]) {
            return false;
          }
          
          // Apply logic parameters
          return logicParameters.every(logicParam => {
            const { variables, timepoints, thresholds, cohorts } = logicParam;
            
            // Apply cohort filter
            if (cohorts && cohorts.length > 0) {
              const isAdult = item.age >= 18;
              const matchesCohort = cohorts.some(cohort => 
                (cohort === 'adult' && isAdult) || 
                (cohort === 'children' && !isAdult)
              );
              if (!matchesCohort) return false;
            }
            
            // Check if item has all required variables
            if (variables.length === 0) return true;
            
            // Apply timepoint logic
            const timepointValues = timepoints.map(tp => {
              const timepointData = item[modality][tp];
              if (!timepointData) return null;
              
              // Check if all thresholds are met for this timepoint
              return thresholds.every(threshold => {
                const { variable, operator, value, value2 } = threshold;
                if (!variable || !operator || !value) return true;
                
                const variableValue = timepointData[variable];
                if (variableValue === undefined) return false;
          
          switch (operator) {
            case '=':
                    return variableValue == value;
            case '!=':
                    return variableValue != value;
            case '>':
                    return parseFloat(variableValue) > parseFloat(value);
            case '<':
                    return parseFloat(variableValue) < parseFloat(value);
            case '>=':
                    return parseFloat(variableValue) >= parseFloat(value);
            case '<=':
                    return parseFloat(variableValue) <= parseFloat(value);
                  case 'between':
                    return parseFloat(variableValue) >= parseFloat(value) && 
                           parseFloat(variableValue) <= parseFloat(value2);
            default:
              return true;
          }
              });
            }).filter(val => val !== null);
            
            // Apply timepoint logic - if any timepoint meets criteria, return true
            return timepointValues.some(val => val);
          });
        });
      });

      setFilteredData(filtered);
      setIsLoading(false);
    }, 1000);
  };

  return (
    <div className="App">
      <header className="app-header">
        <div className="header-content">
          <div className="logo-section">
            <img src={logo} alt="Database Viewer Logo" className="header-logo" />
          </div>
          <div className="header-text">
            <h1>Database Viewer</h1>
            <p>Filter and view your data with filtering system</p>
          </div>
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
