from flask import Flask, request, jsonify
from flask_cors import CORS
import pyodbc
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

# Database configuration
PARTICIPANTS_TABLE = 'participants_2025'  # Define participants table name as a constant

DB_CONFIG = {
    'SERVER': os.getenv('DB_SERVER'),
    'DATABASE': os.getenv('DB_DATABASE'),
    'USERNAME': os.getenv('DB_USERNAME'),
    'PASSWORD': os.getenv('DB_PASSWORD'),
    'DRIVER': os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
}

# Modality to table mapping 
MODALITY_MAPPING = {
    'Diet_Data_Totals': {
        'tables': [
            {'name': 'asa24_children_totals_2025', 'type': 'children', "gender_column": ""},
            {'name': 'asa24_parents_totals_2025', 'type': 'adults', "gender_column": ""}
        ]
    },
    'Qualtrics_Data': {
        'tables': [
            {'name': 'qualtrics_children_data_2025', 'type': 'children', "gender_column": "gender"},
            # {'name': 'qualtrics_children_data_2025_coded', 'type': 'child', "gender_column": "gender"},
            {'name': 'qualtrics_parent_data_2025', 'type': 'adults', "gender_column": "gender_v2"}
            # {'name': 'qualtrics_parent_data_2025_coded', 'type': 'parent', "gender_column": "gender_v2"}
        ]
    },
    'Demographic_Data': {
        'tables': [
            {'name': 'child_demographics_2025', 'type': 'children', "gender_column": "gender"},
            {'name': 'parent_demographics_2025', 'type': 'adults', "gender_column": "gender_v2"}
        ]
    }
}

def get_db_connection():
    """Create and return a database connection"""
    conn_str = (
        f"DRIVER={{{DB_CONFIG['DRIVER']}}};"
        f"SERVER={DB_CONFIG['SERVER']};"
        f"DATABASE={DB_CONFIG['DATABASE']};"
        f"UID={DB_CONFIG['USERNAME']};"
        f"PWD={DB_CONFIG['PASSWORD']};"
    )
    try:
        conn = pyodbc.connect(conn_str)
        return conn
    except pyodbc.Error as e:
        print(f"Error connecting to database: {e}")
        return None

@app.route('/')
def home():
    return {'message': 'Backend server is running'}

@app.route('/get-modalities')
def get_modalities():
    """Get all available modalities"""
    try:
        return jsonify({
            'status': 'success',
            'modalities': list(MODALITY_MAPPING.keys())
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def get_operators_for_type(data_type):
    """Return the list of valid operators for a given data type"""
    if data_type == 'number':
        return [
            {'value': '=', 'label': 'equals'},
            {'value': '!=', 'label': 'not equals'},
            {'value': '>', 'label': 'greater than'},
            {'value': '>=', 'label': 'greater than or equal'},
            {'value': '<', 'label': 'less than'},
            {'value': '<=', 'label': 'less than or equal'},
            {'value': 'between', 'label': 'between'},
            {'value': 'IS NULL', 'label': 'is empty'},
            {'value': 'IS NOT NULL', 'label': 'is not empty'}
        ]
    elif data_type == 'datetime':
        return [
            {'value': '=', 'label': 'on'},
            {'value': '!=', 'label': 'not on'},
            {'value': '>', 'label': 'after'},
            {'value': '>=', 'label': 'on or after'},
            {'value': '<', 'label': 'before'},
            {'value': '<=', 'label': 'on or before'},
            {'value': 'between', 'label': 'between'},
            {'value': 'IS NULL', 'label': 'is empty'},
            {'value': 'IS NOT NULL', 'label': 'is not empty'}
        ]
    elif data_type == 'string':
        return [
            {'value': '=', 'label': 'equals'},
            {'value': '!=', 'label': 'not equals'},
            {'value': 'LIKE', 'label': 'contains'},
            {'value': 'NOT LIKE', 'label': 'does not contain'},
            {'value': 'IS NULL', 'label': 'is empty'},
            {'value': 'IS NOT NULL', 'label': 'is not empty'}
        ]
    else:  # type 'other' or unknown types
        return [
            {'value': '=', 'label': 'equals'},
            {'value': '!=', 'label': 'not equals'},
            {'value': 'IS NULL', 'label': 'is empty'},
            {'value': 'IS NOT NULL', 'label': 'is not empty'}
        ]

@app.route('/get-variables/<modality>/<cohort_type>')
def get_variables(modality, cohort_type):
    """Get variables for a specific modality and cohort type"""
    try:
        if modality not in MODALITY_MAPPING:
            return jsonify({'status': 'error', 'message': 'Invalid modality'}), 400

        # Get tables for the selected modality and cohort type
        tables = [
            table['name'] for table in MODALITY_MAPPING[modality]['tables']
            if table['type'] == cohort_type
        ]

        if not tables:
            return jsonify({'status': 'error', 'message': f'No tables found for {cohort_type} cohort'}), 404

        # Get database connection
        conn = get_db_connection()
        if not conn:
            return jsonify({'status': 'error', 'message': 'Database connection failed'}), 500

        cursor = conn.cursor()
        
        # Get column names and types from all relevant tables
        variables = {}
        for table in tables:
            try:
                cursor.execute(f"SELECT TOP 0 * FROM {table}")
                for column in cursor.description:
                    col_name = column[0]
                    # Map SQL Server types to our simplified types
                    type_name = column[1].__name__.lower()
                    if type_name in ['int', 'bigint', 'smallint', 'tinyint', 'decimal', 'numeric', 'float', 'real']:
                        data_type = 'number'
                    elif type_name in ['datetime', 'date', 'time', 'datetime2', 'datetimeoffset']:
                        data_type = 'datetime'
                    elif type_name in ['char', 'varchar', 'text', 'nchar', 'nvarchar', 'ntext']:
                        data_type = 'string'
                    else:
                        data_type = 'other'
                    
                    # Only update if not exists or if current type is more specific
                    if col_name not in variables or variables[col_name]['type'] == 'other':
                        variables[col_name] = {
                            'name': col_name,
                            'type': data_type,
                            'operators': get_operators_for_type(data_type)
                        }
            except pyodbc.Error as e:
                print(f"Error getting columns from {table}: {e}")

        cursor.close()
        conn.close()

        return jsonify({
            'status': 'success',
            'variables': sorted([v for v in variables.values()], key=lambda x: x['name'])
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/test-connection')
def test_connection():
    """Test the database connection"""
    try:
        conn = get_db_connection()
        if conn:
            conn.close()
            return jsonify({'status': 'success', 'message': 'Database connection successful'})
        else:
            return jsonify({'status': 'error', 'message': 'Could not connect to database'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def _build_not_null_conditions(variables):
    """Build SQL conditions to check for NOT NULL values in selected variables"""
    if not variables:
        return "1=1"  # No variables selected, always true
    conditions = [f"t.{var['name']} IS NOT NULL" for var in variables]  # Use table alias 't' for variables
    return " AND ".join(conditions)

def build_filter_queries(modality, logic_parameters):
    """Build SQL queries for a specific modality and its logic parameters"""
    # Get the actual table mappings for this modality
    modality_config = MODALITY_MAPPING.get(modality)
    if not modality_config:
        raise ValueError(f"No table mapping found for modality: {modality}")
    
    queries = []
    all_params = []
    
    # Filter tables based on selected cohorts
    selected_tables = []
    
    # Get cohorts from the first logic parameter (if any)
    selected_cohorts = []
    if logic_parameters and len(logic_parameters) > 0:
        selected_cohorts = logic_parameters[0].get('cohorts', [])
    
    # If no cohorts selected, empty cohorts list, or all cohorts selected, include all tables
    has_children = 'children' in selected_cohorts
    has_adults = 'adults' in selected_cohorts or 'adult' in selected_cohorts
    
    # If no cohorts or both cohorts selected, include all tables
    if not selected_cohorts or (has_children and has_adults):
        selected_tables = modality_config['tables'].copy()
    else:
        # Only include tables that match the selected cohorts
        for table_config in modality_config['tables']:
            table_type = table_config['type']
            if (table_type == 'children' and has_children) or \
               (table_type == 'adults' and has_adults):
                selected_tables.append(table_config)

    # Build a query for each selected table
    for table_config in selected_tables:
        table_name = table_config['name']
        table_type = table_config['type']
        gender_col = table_config['gender_column']
        
        # Process the first logic parameter (or use defaults if none provided)
        logic_param = logic_parameters[0] if logic_parameters and len(logic_parameters) > 0 else {}
        timepoints = logic_param.get('timepoints') if logic_param and logic_param.get('timepoints') else []
        thresholds = logic_param.get('thresholds') if logic_param and logic_param.get('thresholds') else []
        cohorts = logic_param.get('cohorts') if logic_param and logic_param.get('cohorts') else []
        
        # If no timepoints specified, empty list, or 'all' selected, use all timepoints
        if not timepoints or timepoints == [] or 'all' in timepoints:
            timepoints = [1, 2, 3, 4, 5, 6]  # All timepoints must be present
        
        # Make sure timepoints are integers
        timepoint_params = [int(tp) for tp in timepoints]
        

        base_query = f"""
        WITH ParticipantGenders AS (
            SELECT 
                v.pid,
                COALESCE(p.gender, 'Unknown') as gender
            FROM (
                SELECT t.pid
                FROM {table_name} t
                WHERE t.time_point IN ({','.join(['?' for _ in timepoints])})
                GROUP BY t.pid
                HAVING COUNT(DISTINCT t.time_point) = {len(timepoints)}
                AND COUNT(CASE WHEN {_build_not_null_conditions(logic_param.get('variables', []))} THEN 1 END) = {len(timepoints)}
            ) v
            LEFT JOIN {table_name} t ON v.pid = t.pid
            LEFT JOIN {PARTICIPANTS_TABLE} p ON v.pid = p.pid
            GROUP BY v.pid, p.gender
        )
        SELECT 
            COUNT(DISTINCT pid) as count,
            '{table_type}' as source,
            SUM(CASE WHEN gender IN ('M', 'MALE') OR LOWER(gender) = 'male' THEN 1 ELSE 0 END) as male_count,
            SUM(CASE WHEN gender IN ('F', 'FEMALE') OR LOWER(gender) = 'female' THEN 1 ELSE 0 END) as female_count,
            SUM(CASE 
                WHEN gender IS NULL THEN 0
                WHEN gender NOT IN ('M', 'MALE', 'F', 'FEMALE') 
                    AND LOWER(gender) NOT IN ('male', 'female') 
                THEN 1 
                ELSE 0 
            END) as other_count
        FROM ParticipantGenders
    """
        conditions = []
        params = timepoint_params.copy()  # These are used in the IN clause of the CTE

        # Handle thresholds
        threshold_conditions = []
        for threshold in thresholds:
            variable_obj = threshold.get('variable')
            operator = threshold.get('operator')
            value = threshold.get('value')
            value2 = threshold.get('value2')

            if not variable_obj or not operator:
                continue
            if operator not in ['IS NULL','IS NOT NULL'] and value is None:
                continue


            variable = variable_obj['name']  # Extract name from variable object
            data_type = variable_obj['type']  # Use type from variable object

            if operator == 'between' and value2:
                threshold_conditions.append(f"t.{variable} BETWEEN ? AND ?")  # Reference variable with table alias
                if data_type == 'number':
                    params.extend([float(value), float(value2)])
                elif data_type == 'datetime':
                    params.extend([value, value2])  # Assuming ISO format dates
                else:
                    params.extend([value, value2])
            elif operator in ['LIKE', 'NOT LIKE']:
                threshold_conditions.append(f"t.{variable} {operator} ?")  # Reference variable with table alias
                params.append(f"%{value}%")  # Add wildcards for contains/not contains
            elif operator in ['IS NULL', 'IS NOT NULL']:
                threshold_conditions.append(f"t.{variable} {operator}")  # Reference variable with table alias
            else:
                threshold_conditions.append(f"t.{variable} {operator} ?")  # Reference variable with table alias
                if data_type == 'number':
                    params.append(float(value))
                elif data_type == 'datetime':
                    params.append(value)  # Assuming ISO format dates
                else:
                    params.append(value)

        # Modify the CTE to include threshold conditions
        if threshold_conditions:
            # Find the position of the first WHERE clause in the CTE
            where_pos = base_query.find("WHERE t.time_point IN")
            if where_pos != -1:
                # Insert the threshold conditions after the existing WHERE clause
                insert_pos = base_query.find("GROUP BY t.pid", where_pos)
                if insert_pos != -1:
                    base_query = (
                        base_query[:insert_pos] +
                        f" AND {' AND '.join(threshold_conditions)} " +
                        base_query[insert_pos:]
                    )
        
        queries.append(base_query)
        all_params.extend(params)
    
    # If we have no queries, return a default query that returns no results
    if not queries:
        return "SELECT 0 as count, 'none' as source WHERE 1=0", []
    
            # If we have multiple tables, we'll need to combine their results
    if len(queries) > 1:
        # For SQL Server, we need to define all CTEs first, then do the UNION ALL
        # Process threshold conditions for each CTE
        threshold_conditions_1 = []
        threshold_conditions_2 = []
        
        # Handle thresholds for both CTEs
        for threshold in thresholds:
            variable_obj = threshold.get('variable')
            operator = threshold.get('operator')
            value = threshold.get('value')
            value2 = threshold.get('value2')

            if not variable_obj or not operator:
                continue
            if operator not in ['IS NULL','IS NOT NULL'] and value is None:
                continue


            variable = variable_obj['name']
            data_type = variable_obj['type']

            if operator == 'between' and value2:
                condition = f"t.{variable} BETWEEN ? AND ?"
            elif operator in ['LIKE', 'NOT LIKE']:
                condition = f"t.{variable} {operator} ?"
            elif operator in ['IS NULL', 'IS NOT NULL']:
                condition = f"t.{variable} {operator}"
            else:
                condition = f"t.{variable} {operator} ?"
            
            threshold_conditions_1.append(condition)
            threshold_conditions_2.append(condition)

        combined_query = """
            WITH ParticipantGenders_1 AS (
                SELECT 
                    v.pid,
                    COALESCE(p.gender, 'Unknown') as gender
                FROM (
                    SELECT t.pid
                    FROM {table_name_1} t
                    WHERE t.time_point IN ({timepoints_1})
                    GROUP BY t.pid
                    HAVING COUNT(DISTINCT t.time_point) = {len_timepoints_1}
                ) v
                LEFT JOIN {table_name_1} t ON v.pid = t.pid
                LEFT JOIN {PARTICIPANTS_TABLE} p ON v.pid = p.pid
                WHERE 1=1 {where_th_1}
                GROUP BY v.pid, p.gender
            ),
            ParticipantGenders_2 AS (
                SELECT 
                    v.pid,
                    COALESCE(p.gender, 'Unknown') as gender
                FROM (
                    SELECT t.pid
                    FROM {table_name_2} t
                    WHERE t.time_point IN ({timepoints_2})
                    GROUP BY t.pid
                    HAVING COUNT(DISTINCT t.time_point) = {len_timepoints_2}
                ) v
                LEFT JOIN {table_name_2} t ON v.pid = t.pid
                LEFT JOIN {PARTICIPANTS_TABLE} p ON v.pid = p.pid
                WHERE 1=1 {where_th_2}
                GROUP BY v.pid, p.gender
            )
            SELECT 
                COUNT(DISTINCT pid) as count,
                '{type_1}' as source,
                SUM(CASE WHEN gender IN ('M', 'MALE') OR LOWER(gender) = 'male' THEN 1 ELSE 0 END) as male_count,
                SUM(CASE WHEN gender IN ('F', 'FEMALE') OR LOWER(gender) = 'female' THEN 1 ELSE 0 END) as female_count,
                SUM(CASE 
                    WHEN gender IS NULL THEN 0
                    WHEN gender NOT IN ('M', 'MALE', 'F', 'FEMALE') 
                        AND LOWER(gender) NOT IN ('male', 'female') 
                    THEN 1 
                    ELSE 0 
                END) as other_count
            FROM ParticipantGenders_1
            UNION ALL
            SELECT 
                COUNT(DISTINCT pid) as count,
                '{type_2}' as source,
                SUM(CASE WHEN gender IN ('M', 'MALE') OR LOWER(gender) = 'male' THEN 1 ELSE 0 END) as male_count,
                SUM(CASE WHEN gender IN ('F', 'FEMALE') OR LOWER(gender) = 'female' THEN 1 ELSE 0 END) as female_count,
                SUM(CASE 
                    WHEN gender IS NULL THEN 0
                    WHEN gender NOT IN ('M', 'MALE', 'F', 'FEMALE') 
                        AND LOWER(gender) NOT IN ('male', 'female') 
                    THEN 1 
                    ELSE 0 
                END) as other_count
            FROM ParticipantGenders_2
        """.format(
            table_name_1=selected_tables[0]['name'],
            table_name_2=selected_tables[1]['name'],
            type_1=selected_tables[0]['type'],
            type_2=selected_tables[1]['type'],
            timepoints_1=','.join(['?' for _ in timepoints]),
            timepoints_2=','.join(['?' for _ in timepoints]),
            len_timepoints_1=len(timepoints),
            len_timepoints_2=len(timepoints),
            PARTICIPANTS_TABLE=PARTICIPANTS_TABLE,
            where_th_1=(' AND ' + ' AND '.join(threshold_conditions_1)) if threshold_conditions_1 else '',
            where_th_2=(' AND ' + ' AND '.join(threshold_conditions_2)) if threshold_conditions_2 else '',
        )
        # Create separate parameter lists for each CTE
        params_1 = timepoint_params.copy()
        params_2 = timepoint_params.copy()
        
        # Add threshold parameters for each CTE
        for threshold in thresholds:
            if threshold.get('variable') and threshold.get('operator') and threshold.get('value'):
                if threshold.get('operator') == 'between' and threshold.get('value2'):
                    params_1.extend([float(threshold['value']), float(threshold['value2'])])
                    params_2.extend([float(threshold['value']), float(threshold['value2'])])
                else:
                    value = float(threshold['value']) if threshold['value'].replace('.', '').isdigit() else threshold['value']
                    params_1.append(value)
                    params_2.append(value)
        
        # Combine parameters in the correct order
        all_params = params_1 + params_2
    else:
        combined_query = queries[0]

    return combined_query, all_params

@app.route('/query-data', methods=['POST'])
def query_data():
    """Execute queries based on filter parameters and return counts"""
    try:
        filters = request.json.get('filters', [])
        
        # Get database connection
        conn = get_db_connection()
        if not conn:
            return jsonify({'status': 'error', 'message': 'Database connection failed'}), 500

        cursor = conn.cursor()
        results = {}

        # Process each filter
        for filter_item in filters:
            modality = filter_item.get('modality')
            logic_parameters = filter_item.get('logicParameters') or []

            if not modality:
                continue

            # If no logic parameters or all fields in logic parameter are empty, just get basic counts
            if not logic_parameters or (
                len(logic_parameters) == 1 and
                not logic_parameters[0].get('timepoints') and
                not logic_parameters[0].get('thresholds') and
                not logic_parameters[0].get('cohorts') and
                not logic_parameters[0].get('variables')
            ):
                counts = {
                    'total': 0,
                    'children': 0,
                    'adults': 0,
                    'gender': {
                        'children': {'M': 0, 'F': 0},
                        'adults': {'M': 0, 'F': 0}
                    }
                }
                
                # Get counts for each table in this modality
                for table_config in MODALITY_MAPPING[modality]['tables']:
                    table_name = table_config['name']
                    table_type = table_config['type']
                    
                    try:
                        # Get total count and gender counts for this table
                        gender_col = table_config['gender_column']
                        base_select = """
                            SELECT 
                                COUNT(pid) as total,
                                SUM(CASE WHEN gender IN ('M', 'MALE') OR LOWER(gender) = 'male' THEN 1 ELSE 0 END) as male_count,
                                SUM(CASE WHEN gender IN ('F', 'FEMALE') OR LOWER(gender) = 'female' THEN 1 ELSE 0 END) as female_count,
                                SUM(CASE 
                                    WHEN gender IS NULL THEN 0
                                    WHEN gender NOT IN ('M', 'MALE', 'F', 'FEMALE') 
                                        AND LOWER(gender) NOT IN ('male', 'female') 
                                    THEN 1 
                                    ELSE 0 
                                END) as other_count
                            FROM TimePointCounts
                        """
                        
                        # Choose query based on whether we need to get gender from participants table
                        if gender_col == '':
                            count_query = f"""
                                WITH TimePointCounts AS (
                                    SELECT 
                                        t.pid,
                                        COUNT(DISTINCT t.time_point) as tp_count,
                                        MIN(p.gender) as gender
                                    FROM {table_name} t
                                    LEFT JOIN {PARTICIPANTS_TABLE} p ON t.pid = p.pid
                                    WHERE t.time_point IN (1,2,3,4,5,6)
                                    GROUP BY t.pid
                                    HAVING COUNT(DISTINCT t.time_point) = 6  -- All timepoints required in this case
                                )
                                {base_select}
                            """
                        else:
                            count_query = f"""
                                WITH TimePointCounts AS (
                                    SELECT 
                                        pid,
                                        COUNT(DISTINCT time_point) as tp_count,
                                        MIN({gender_col}) as gender
                                    FROM {table_name}
                                    WHERE time_point IN (1,2,3,4,5,6)
                                    GROUP BY pid
                                    HAVING COUNT(DISTINCT time_point) = 6  -- All timepoints required in this case
                                )
                                {base_select}
                            """
                        cursor.execute(count_query)
                        row = cursor.fetchone()
                        count = row[0]
                        male_count = row[1] or 0  # Use 0 if NULL
                        female_count = row[2] or 0  # Use 0 if NULL
                        other_count = row[3] or 0  # Use 0 if NULL
                        
                        # Update counts
                        counts[table_type] = count
                        counts['total'] += count
                        counts['gender'][table_type]['M'] = male_count
                        counts['gender'][table_type]['F'] = female_count
                        counts['gender'][table_type]['O'] = other_count
                        
                    except pyodbc.Error as e:
                        print(f"Error counting rows in {table_name}: {e}")
                
                results[modality] = {
                    'counts': counts
                }
            else:
                # Original logic for when there are logic parameters
                query, params = build_filter_queries(modality, logic_parameters)
                try:
                    cursor.execute(query, params)
                    rows = cursor.fetchall()
                    counts = {
                        'total': 0,
                        'children': 0,
                        'adults': 0,
                        'gender': {
                            'children': {'M': 0, 'F': 0, 'O': 0},
                            'adults': {'M': 0, 'F': 0, 'O': 0}
                        }
                    }
                    
                    for row in rows:
                        if row and len(row) >= 5:  # count, source, male_count, female_count, other_count
                            count = row[0] or 0  # Use 0 if count is None
                            source = row[1]
                            male_count = row[2] or 0
                            female_count = row[3] or 0
                            other_count = row[4] or 0
                            
                            # Normalize source type to match our expected keys
                            source_type = source.lower()  # Convert to lowercase to handle any case variations
                            if source_type in ['children', 'adults']:  # Make sure it's a valid source type
                                counts[source_type] = count
                                counts['total'] += count
                                counts['gender'][source_type]['M'] = male_count
                                counts['gender'][source_type]['F'] = female_count
                                counts['gender'][source_type]['O'] = other_count
                    
                    results[modality] = {
                        'counts': counts,
                        'query': query
                    }
                except pyodbc.Error as e:
                    results[modality] = {
                        'error': str(e),
                        'query': query  # Include failed query for debugging
                    }

        cursor.close()
        conn.close()

        return jsonify({
            'status': 'success',
            'results': results
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)