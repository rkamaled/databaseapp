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
    'Diet Data Totals': {
        'tables': [
            {'name': 'asa24_children_totals_2025', 'type': 'children', "gender_column": ""},
            {'name': 'asa24_parents_totals_2025', 'type': 'adults', "gender_column": ""}
        ]
    },
    'Qualtrics Data': {
        'tables': [
            {'name': 'qualtrics_children_data_2025', 'type': 'children', "gender_column": "gender"},
            # {'name': 'qualtrics_children_data_2025_coded', 'type': 'child', "gender_column": "gender"},
            {'name': 'qualtrics_parent_data_2025', 'type': 'adults', "gender_column": "gender_v2"},
            # {'name': 'qualtrics_parent_data_2025_coded', 'type': 'parent', "gender_column": "gender_v2"}
            {'name': 'children_self_report_2025', 'type': 'children', "gender_column": "gender"}
        ]
    },
    'Demographic Data': {
        'tables': [
            {'name': 'child_demographics_2025', 'type': 'children', "gender_column": "gender"},
            {'name': 'parent_demographics_2025', 'type': 'adults', "gender_column": "gender_v2"}
        ]
    },
    'Life-labs Data': {
        'tables': [
            {'name': 'life_labs_2025', 'type': 'both', "gender_column": ""},
        ]
    }
    
    # 'Genotype Data': {
    #     'tables': [
    #         {'name': 'genotype_data_2025', 'type': '*', "gender_column": ""},
    #     ]
    # }
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
        # If a table is of type 'both', expose its columns for either cohort
        tables = [
            table['name'] for table in MODALITY_MAPPING[modality]['tables']
            if table['type'] == cohort_type or (table['type'] == 'both' and cohort_type in ['children', 'adults'])
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
                            'operators': get_operators_for_type(data_type),
                            'cohort': cohort_type,
                            'tables': [table]
                        }
                    else:
                        # Merge table membership for this variable
                        if 'tables' not in variables[col_name] or not isinstance(variables[col_name]['tables'], list):
                            variables[col_name]['tables'] = []
                        if table not in variables[col_name]['tables']:
                            variables[col_name]['tables'].append(table)
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

def _build_pid_filter_conditions(table_type, selected_cohorts):
    """Build SQL conditions to filter PIDs based on table type and selected cohorts"""
    if table_type != 'both':
        return "1=1"  # No filtering for non-both tables
    
    conditions = []
    
    if 'children' in selected_cohorts:
        # Children: PID begins with 'a', 'b', or 'c' (case insensitive)
        conditions.append("(UPPER(LEFT(t.pid, 1)) IN ('A', 'B', 'C'))")
    
    if 'adults' in selected_cohorts or 'adult' in selected_cohorts:
        # Adults: PID begins with 'p' or 's' (case insensitive)
        conditions.append("(UPPER(LEFT(t.pid, 1)) IN ('P', 'S'))")
    
    if conditions:
        return " OR ".join(conditions)
    else:
        # If no specific cohorts selected for a 'both' table, include all valid PIDs
        return "(UPPER(LEFT(t.pid, 1)) IN ('A', 'B', 'C', 'P', 'S'))"

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
               (table_type == 'adults' and has_adults) or \
               (table_type == 'both' and (has_children or has_adults)):
                selected_tables.append(table_config)

    # Build a query for each selected table
    # Discover columns for each selected table to scope variables/thresholds safely
    columns_per_table = {}
    column_types_per_table = {}
    try:
        conn_cols = get_db_connection()
        if conn_cols:
            cur_cols = conn_cols.cursor()
            for table_cfg in selected_tables:
                tname = table_cfg['name']
                try:
                    cur_cols.execute(f"SELECT TOP 0 * FROM {tname}")
                    # Collect column names and coarse type categories
                    col_names = set()
                    col_types = {}
                    for col in cur_cols.description:
                        col_name = col[0]
                        col_names.add(col_name)
                        type_name = col[1].__name__.lower()
                        if type_name in ['int', 'bigint', 'smallint', 'tinyint', 'decimal', 'numeric', 'float', 'real']:
                            cat = 'number'
                        elif type_name in ['datetime', 'date', 'time', 'datetime2', 'datetimeoffset']:
                            cat = 'datetime'
                        elif type_name in ['char', 'varchar', 'text', 'nchar', 'nvarchar', 'ntext']:
                            cat = 'string'
                        else:
                            cat = 'other'
                        col_types[col_name] = cat
                    columns_per_table[tname] = col_names
                    column_types_per_table[tname] = col_types
                except Exception:
                    columns_per_table[tname] = set()
                    column_types_per_table[tname] = {}
            cur_cols.close()
            conn_cols.close()
    except Exception:
        pass
    for table_config in selected_tables:
        table_name = table_config['name']
        table_type = table_config['type']
        gender_col = table_config['gender_column']
        
        # Process the first logic parameter (or use defaults if none provided)
        logic_param = logic_parameters[0] if logic_parameters and len(logic_parameters) > 0 else {}
        timepoints = logic_param.get('timepoints') if logic_param and logic_param.get('timepoints') else []
        thresholds = logic_param.get('thresholds') if logic_param and logic_param.get('thresholds') else []
        cohorts = logic_param.get('cohorts') if logic_param and logic_param.get('cohorts') else []
        # Variables scoped to the current table's cohort and membership
        # For 'both' type tables, include variables for both 'adults' and 'children' cohorts
        if table_type == 'both':
            variables_for_table = []
            for var in (logic_param.get('variables') or []):
                if not isinstance(var, dict):
                    continue
                if var.get('cohort') not in ['adults', 'children', 'both']:
                    continue
                var_name = var.get('name')
                var_tables = var.get('tables') if isinstance(var.get('tables'), list) else None
                has_column = False
                if var_tables:
                    has_column = table_name in var_tables
                else:
                    table_cols = columns_per_table.get(table_name)
                    has_column = (var_name in table_cols) if isinstance(table_cols, set) else True
                if has_column:
                    variables_for_table.append(var)
        else:
            variables_for_table = []
            for var in (logic_param.get('variables') or []):
                if not isinstance(var, dict):
                    continue
                if var.get('cohort') != table_type:
                    continue
                var_name = var.get('name')
                var_tables = var.get('tables') if isinstance(var.get('tables'), list) else None
                has_column = False
                if var_tables:
                    has_column = table_name in var_tables
                else:
                    table_cols = columns_per_table.get(table_name)
                    has_column = (var_name in table_cols) if isinstance(table_cols, set) else True
                if has_column:
                    variables_for_table.append(var)
        thresholds_for_table = []
        for th in thresholds:
            var = th.get('variable') if isinstance(th, dict) else None
            scope = th.get('cohortScope') if isinstance(th, dict) else None
            if not var or not isinstance(var, dict):
                continue
            var_cohort = var.get('cohort')
            # Respect table membership if provided; otherwise check discovered columns
            var_tables = var.get('tables') if isinstance(var, dict) else None
            if isinstance(var_tables, list):
                if table_name not in var_tables:
                    continue
            else:
                table_cols = columns_per_table.get(table_name)
                var_name = var.get('name') if isinstance(var, dict) else None
                if isinstance(table_cols, set) and var_name not in table_cols:
                    continue
            # Apply to both tables if scope == 'both' (assumes column exists on both cohort tables)
            if scope == 'both':
                thresholds_for_table.append(th)
                continue
            # Otherwise, apply only if variable belongs to this table and scope includes this table
            if table_type == 'both':
                # For 'both' type tables, include thresholds for 'adults', 'children', and 'both' cohorts
                if var_cohort in ['adults', 'children', 'both'] and (scope in (None, '', var_cohort, 'both')):
                    thresholds_for_table.append(th)
            elif var_cohort == table_type and (scope in (None, '', table_type)):
                thresholds_for_table.append(th)
        
        # If no timepoints specified, empty list, or 'all' selected, use all timepoints
        if not timepoints or timepoints == [] or 'all' in timepoints:
            timepoints = [1, 2, 3, 4, 5, 6, 7, 8, 9]  # All timepoints must be present
        # Otherwise, use the specific timepoints selected
        
        # Make sure timepoints are integers
        timepoint_params = [int(tp) for tp in timepoints]
        

        # Build conditional HAVING clause for NOT NULL checks only if variables are provided for this table
        having_not_null_clause_single = (
            f" AND COUNT(CASE WHEN {_build_not_null_conditions(variables_for_table)} THEN 1 END) = {len(timepoints)}"
            if variables_for_table else ""
        )

        # Build PID filtering conditions for 'both' type tables
        pid_filter_condition = _build_pid_filter_conditions(table_type, selected_cohorts)

        base_cte = f"""
        WITH ParticipantGenders AS (
            SELECT 
                v.pid,
                COALESCE(p.gender, 'Unknown') as gender
            FROM (
                SELECT t.pid
                FROM {table_name} t
                WHERE t.time_point IN ({','.join(['?' for _ in timepoints])})
                  AND {pid_filter_condition}
                GROUP BY t.pid
                HAVING COUNT(DISTINCT t.time_point) = {len(timepoints)}{having_not_null_clause_single}
            ) v
            LEFT JOIN {table_name} t ON v.pid = t.pid
            LEFT JOIN {PARTICIPANTS_TABLE} p ON v.pid = p.pid
            GROUP BY v.pid, p.gender
        )
    """

        if table_type == 'both':
            final_select = """
        SELECT 
            COUNT(DISTINCT pid) as count,
            CASE 
                WHEN UPPER(LEFT(pid, 1)) IN ('A', 'B', 'C') THEN 'children'
                WHEN UPPER(LEFT(pid, 1)) IN ('P', 'S') THEN 'adults'
                ELSE 'other'
            END as source,
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
        GROUP BY 
            CASE 
                WHEN UPPER(LEFT(pid, 1)) IN ('A', 'B', 'C') THEN 'children'
                WHEN UPPER(LEFT(pid, 1)) IN ('P', 'S') THEN 'adults'
                ELSE 'other'
            END
            """
        else:
            final_select = f"""
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

        base_query = base_cte + final_select
        conditions = []
        params = timepoint_params.copy()  # These are used in the IN clause of the CTE

        # Handle thresholds
        threshold_conditions = []
        for threshold in thresholds_for_table:
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
        # If multiple tables share the same cohort (not 'both'), build a merged UNION-based CTE
        logic_param = logic_parameters[0] if logic_parameters and len(logic_parameters) > 0 else {}
        all_thresholds = logic_param.get('thresholds') or []
        all_variables = logic_param.get('variables') or []

        same_type = len({t['type'] for t in selected_tables}) == 1
        cohort_type = selected_tables[0]['type'] if same_type else None
        if same_type and cohort_type in ['children', 'adults']:
            # Build union column set
            union_columns = set()
            for tcfg in selected_tables:
                tcols = columns_per_table.get(tcfg['name']) or set()
                for c in tcols:
                    if c.lower() not in ['pid', 'time_point']:
                        union_columns.add(c)
            union_columns = sorted(union_columns)

            # Decide a target SQL type per union column based on available categories
            union_target_types = {}
            for col in union_columns:
                target_cat = None
                for tcfg in selected_tables:
                    tname_scan = tcfg['name']
                    ttypes = column_types_per_table.get(tname_scan) or {}
                    if col in ttypes:
                        cat = ttypes[col]
                        if cat == 'number':
                            target_cat = 'number'
                            break
                        if cat == 'datetime' and target_cat != 'number':
                            target_cat = 'datetime'
                        if cat == 'string' and target_cat not in ['number', 'datetime']:
                            target_cat = 'string'
                        if target_cat is None:
                            target_cat = cat
                if target_cat is None:
                    target_cat = 'string'
                union_target_types[col] = target_cat

            # Build UNION ALL CTE with aligned columns
            union_selects = []
            for tcfg in selected_tables:
                tname = tcfg['name']
                tcols = columns_per_table.get(tname) or set()
                select_cols = ["pid", "time_point"]
                for col in union_columns:
                    target_cat = union_target_types.get(col, 'string')
                    if col in tcols:
                        if target_cat == 'number':
                            select_cols.append(f"CAST({col} AS FLOAT) AS {col}")
                        elif target_cat == 'datetime':
                            select_cols.append(f"CAST({col} AS DATETIME) AS {col}")
                        else:
                            select_cols.append(f"CAST({col} AS NVARCHAR(MAX)) AS {col}")
                    else:
                        if target_cat == 'number':
                            select_cols.append(f"CAST(NULL AS FLOAT) AS {col}")
                        elif target_cat == 'datetime':
                            select_cols.append(f"CAST(NULL AS DATETIME) AS {col}")
                        else:
                            select_cols.append(f"CAST(NULL AS NVARCHAR(MAX)) AS {col}")
                union_selects.append(
                    f"SELECT {', '.join(select_cols)} FROM {tname}"
                )

            # Build CombinedData CTE aggregating per pid/time_point
            agg_cols_list = []
            for col in union_columns:
                if col.lower() == 'gender':
                    agg_cols_list.append(f"MAX(u.{col}) AS survey_gender")
                else:
                    agg_cols_list.append(f"MAX(u.{col}) AS {col}")
            agg_cols = ",\n                        ".join(agg_cols_list)
            combined_query = """
                WITH Unioned AS (
                    {union_all}
                ),
                CombinedData AS (
                    SELECT 
                        u.pid,
                        u.time_point,
                        MIN(p.gender) AS gender,
                        {agg_cols}
                    FROM Unioned u
                    LEFT JOIN {PARTICIPANTS_TABLE} p ON u.pid = p.pid
                    GROUP BY u.pid, u.time_point
                ),
                EligiblePids AS (
                    SELECT 
                        cd.pid,
                        MIN(cd.gender) AS gender
                    FROM CombinedData cd
                    WHERE cd.time_point IN ({timepoints}) {where_th}
                    GROUP BY cd.pid
                    HAVING COUNT(DISTINCT cd.time_point) = {len_timepoints}{having_not_null}
                )
                SELECT 
                    COUNT(DISTINCT pid) as count,
                    '{cohort}' as source,
                    SUM(CASE WHEN gender IN ('M', 'MALE') OR LOWER(gender) = 'male' THEN 1 ELSE 0 END) as male_count,
                    SUM(CASE WHEN gender IN ('F', 'FEMALE') OR LOWER(gender) = 'female' THEN 1 ELSE 0 END) as female_count,
                    SUM(CASE 
                        WHEN gender IS NULL THEN 0
                        WHEN gender NOT IN ('M', 'MALE', 'F', 'FEMALE') 
                            AND LOWER(gender) NOT IN ('male', 'female') 
                        THEN 1 
                        ELSE 0 
                    END) as other_count
                FROM EligiblePids
            """.format(
                union_all="\n                    UNION ALL\n                    ".join(union_selects),
                agg_cols=agg_cols if agg_cols else "",
                PARTICIPANTS_TABLE=PARTICIPANTS_TABLE,
                cohort=cohort_type,
                timepoints=','.join(['?' for _ in timepoints]),
                len_timepoints=len(timepoints),
                where_th='',  # thresholds below
                having_not_null=''  # will fill below
            )

            # Build threshold conditions against CombinedData alias
            threshold_conditions = []
            params_merged = timepoint_params.copy()
            for threshold in all_thresholds:
                variable_obj = threshold.get('variable')
                operator = threshold.get('operator')
                value = threshold.get('value')
                value2 = threshold.get('value2')
                if not variable_obj or not operator:
                    continue
                if operator not in ['IS NULL','IS NOT NULL'] and value is None:
                    continue
                var_name = variable_obj.get('name')
                if var_name not in union_columns:
                    continue
                vtype = variable_obj.get('type')
                if operator == 'between' and value2 is not None:
                    threshold_conditions.append(f"cd.{var_name} BETWEEN ? AND ?")
                    if vtype == 'number':
                        params_merged.extend([float(value), float(value2)])
                    else:
                        params_merged.extend([value, value2])
                elif operator in ['LIKE', 'NOT LIKE']:
                    threshold_conditions.append(f"cd.{var_name} {operator} ?")
                    params_merged.append(f"%{value}%")
                elif operator in ['IS NULL', 'IS NOT NULL']:
                    threshold_conditions.append(f"cd.{var_name} {operator}")
                else:
                    threshold_conditions.append(f"cd.{var_name} {operator} ?")
                    if vtype == 'number':
                        params_merged.append(float(value))
                    else:
                        params_merged.append(value)

            # Inject thresholds into WHERE
            if threshold_conditions:
                combined_query = combined_query.replace("{where_th}", " AND " + " AND ".join(threshold_conditions))
            else:
                combined_query = combined_query.replace("{where_th}", "")

            # Build NOT NULL having clause for selected variables present in union
            selected_vars = [v for v in all_variables if isinstance(v, dict) and v.get('cohort') == cohort_type and v.get('name') in union_columns]
            if selected_vars:
                not_null_conditions = " AND ".join([f"cd.{v['name']} IS NOT NULL" for v in selected_vars])
                having_clause = f" AND COUNT(CASE WHEN {not_null_conditions} THEN 1 END) = {len(timepoints)}"
                combined_query = combined_query.replace("{having_not_null}", having_clause)
            else:
                combined_query = combined_query.replace("{having_not_null}", "")

            combined_query = combined_query.replace("{where_th}", "")
            queries = [combined_query]
            all_params = params_merged
        else:
            # Fallback: keep prior per-table queries as-is
            combined_query = " UNION ALL ".join(queries)
            queries = [combined_query]
    else:
        combined_query = queries[0]

    return combined_query, all_params

def build_filter_pid_query(modality, logic_parameters):
    """Build a SQL query that returns DISTINCT pid and gender eligible for this filter."""
    modality_config = MODALITY_MAPPING.get(modality)
    if not modality_config:
        raise ValueError(f"No table mapping found for modality: {modality}")

    # Determine selected tables based on cohorts
    selected_tables = []
    selected_cohorts = []
    if logic_parameters and len(logic_parameters) > 0:
        selected_cohorts = logic_parameters[0].get('cohorts', [])
    has_children = 'children' in selected_cohorts
    has_adults = 'adults' in selected_cohorts or 'adult' in selected_cohorts
    if not selected_cohorts or (has_children and has_adults):
        selected_tables = modality_config['tables'].copy()
    else:
        for table_config in modality_config['tables']:
            table_type = table_config['type']
            if (table_type == 'children' and has_children) or \
               (table_type == 'adults' and has_adults) or \
               (table_type == 'both' and (has_children or has_adults)):
                selected_tables.append(table_config)

    # Discover columns for variable/threshold scoping
    columns_per_table = {}
    try:
        conn_cols = get_db_connection()
        if conn_cols:
            cur_cols = conn_cols.cursor()
            for table_cfg in selected_tables:
                tname = table_cfg['name']
                try:
                    cur_cols.execute(f"SELECT TOP 0 * FROM {tname}")
                    col_names = set()
                    for col in cur_cols.description:
                        col_names.add(col[0])
                    columns_per_table[tname] = col_names
                except Exception:
                    columns_per_table[tname] = set()
            cur_cols.close()
            conn_cols.close()
    except Exception:
        pass

    subselects = []
    all_params = []

    for table_config in selected_tables:
        table_name = table_config['name']
        table_type = table_config['type']

        logic_param = logic_parameters[0] if logic_parameters and len(logic_parameters) > 0 else {}
        timepoints = logic_param.get('timepoints') if logic_param and logic_param.get('timepoints') else []
        thresholds = logic_param.get('thresholds') if logic_param and logic_param.get('thresholds') else []

        # Variables present on this table for NOT NULL checks
        if table_type == 'both':
            variables_for_table = []
            for var in (logic_param.get('variables') or []):
                if not isinstance(var, dict):
                    continue
                if var.get('cohort') not in ['adults', 'children', 'both']:
                    continue
                var_name = var.get('name')
                var_tables = var.get('tables') if isinstance(var.get('tables'), list) else None
                if var_tables:
                    has_column = table_name in var_tables
                else:
                    table_cols = columns_per_table.get(table_name)
                    has_column = (var_name in table_cols) if isinstance(table_cols, set) else True
                if has_column:
                    variables_for_table.append(var)
        else:
            variables_for_table = []
            for var in (logic_param.get('variables') or []):
                if not isinstance(var, dict):
                    continue
                if var.get('cohort') != table_type:
                    continue
                var_name = var.get('name')
                var_tables = var.get('tables') if isinstance(var.get('tables'), list) else None
                if var_tables:
                    has_column = table_name in var_tables
                else:
                    table_cols = columns_per_table.get(table_name)
                    has_column = (var_name in table_cols) if isinstance(table_cols, set) else True
                if has_column:
                    variables_for_table.append(var)

        # Timepoints
        if not timepoints or timepoints == [] or 'all' in timepoints:
            timepoints = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        timepoint_params = [int(tp) for tp in timepoints]

        having_not_null_clause_single = (
            f" AND COUNT(CASE WHEN {_build_not_null_conditions(variables_for_table)} THEN 1 END) = {len(timepoints)}"
            if variables_for_table else ""
        )

        pid_filter_condition = _build_pid_filter_conditions(table_type, selected_cohorts)

        # Threshold conditions
        threshold_conditions = []
        params = timepoint_params.copy()
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
            if operator == 'between' and value2 is not None:
                threshold_conditions.append(f"t.{variable} BETWEEN ? AND ?")
                if data_type == 'number':
                    params.extend([float(value), float(value2)])
                else:
                    params.extend([value, value2])
            elif operator in ['LIKE', 'NOT LIKE']:
                threshold_conditions.append(f"t.{variable} {operator} ?")
                params.append(f"%{value}%")
            elif operator in ['IS NULL', 'IS NOT NULL']:
                threshold_conditions.append(f"t.{variable} {operator}")
            else:
                threshold_conditions.append(f"t.{variable} {operator} ?")
                if data_type == 'number':
                    params.append(float(value))
                else:
                    params.append(value)

        thresholds_sql = (" AND " + " AND ".join(threshold_conditions)) if threshold_conditions else ""

        # Build per-table subselect of eligible PIDs
        subselect = f"""
            SELECT t.pid
            FROM {table_name} t
            WHERE t.time_point IN ({','.join(['?' for _ in timepoints])})
              AND {pid_filter_condition}
              {thresholds_sql}
            GROUP BY t.pid
            HAVING COUNT(DISTINCT t.time_point) = {len(timepoints)}{having_not_null_clause_single}
        """
        subselects.append(subselect)
        all_params.extend(params)

    if not subselects:
        return "SELECT pid, gender FROM (SELECT NULL as pid, NULL as gender) x WHERE 1=0", []

    unioned = "\n            UNION ALL\n            ".join(subselects)
    full_query = f"""
        WITH UnionPids AS (
            {unioned}
        ),
        DistinctPids AS (
            SELECT DISTINCT pid FROM UnionPids
        )
        SELECT dp.pid, COALESCE(p.gender, 'Unknown') as gender
        FROM DistinctPids dp
        LEFT JOIN {PARTICIPANTS_TABLE} p ON dp.pid = p.pid
    """
    return full_query, all_params

def build_filter_pid_subselect(modality, logic_parameters):
    """Return a SQL subselect that yields DISTINCT pid for a single filter."""
    modality_config = MODALITY_MAPPING.get(modality)
    if not modality_config:
        raise ValueError(f"No table mapping found for modality: {modality}")

    # Determine tables for cohorts
    selected_tables = []
    selected_cohorts = []
    if logic_parameters and len(logic_parameters) > 0:
        selected_cohorts = logic_parameters[0].get('cohorts', [])
    has_children = 'children' in selected_cohorts
    has_adults = 'adults' in selected_cohorts or 'adult' in selected_cohorts
    if not selected_cohorts or (has_children and has_adults):
        selected_tables = modality_config['tables'].copy()
    else:
        for table_config in modality_config['tables']:
            table_type = table_config['type']
            if (table_type == 'children' and has_children) or \
               (table_type == 'adults' and has_adults) or \
               (table_type == 'both' and (has_children or has_adults)):
                selected_tables.append(table_config)

    # Discover columns for variable/threshold scoping
    columns_per_table = {}
    try:
        conn_cols = get_db_connection()
        if conn_cols:
            cur_cols = conn_cols.cursor()
            for table_cfg in selected_tables:
                tname = table_cfg['name']
                try:
                    cur_cols.execute(f"SELECT TOP 0 * FROM {tname}")
                    col_names = set(col[0] for col in cur_cols.description)
                    columns_per_table[tname] = col_names
                except Exception:
                    columns_per_table[tname] = set()
            cur_cols.close()
            conn_cols.close()
    except Exception:
        pass

    # Build union-of-tables subselects honoring thresholds and not-null variable checks
    subselects = []
    params_all = []

    logic_param = logic_parameters[0] if logic_parameters and len(logic_parameters) > 0 else {}
    timepoints = logic_param.get('timepoints') if logic_param and logic_param.get('timepoints') else []
    thresholds = logic_param.get('thresholds') if logic_param and logic_param.get('thresholds') else []

    # variables check per-table
    for table_config in selected_tables:
        table_name = table_config['name']
        table_type = table_config['type']

        # Variables present on this table for NOT NULL checks
        if table_type == 'both':
            variables_for_table = []
            for var in (logic_param.get('variables') or []):
                if not isinstance(var, dict):
                    continue
                if var.get('cohort') not in ['adults', 'children', 'both']:
                    continue
                var_name = var.get('name')
                var_tables = var.get('tables') if isinstance(var.get('tables'), list) else None
                if var_tables:
                    has_column = table_name in var_tables
                else:
                    table_cols = columns_per_table.get(table_name)
                    has_column = (var_name in table_cols) if isinstance(table_cols, set) else True
                if has_column:
                    variables_for_table.append(var)
        else:
            variables_for_table = []
            for var in (logic_param.get('variables') or []):
                if not isinstance(var, dict):
                    continue
                if var.get('cohort') != table_type:
                    continue
                var_name = var.get('name')
                var_tables = var.get('tables') if isinstance(var.get('tables'), list) else None
                if var_tables:
                    has_column = table_name in var_tables
                else:
                    table_cols = columns_per_table.get(table_name)
                    has_column = (var_name in table_cols) if isinstance(table_cols, set) else True
                if has_column:
                    variables_for_table.append(var)

        # Timepoints
        tps = timepoints
        if not tps or tps == [] or 'all' in tps:
            tps = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        tp_params = [int(tp) for tp in tps]

        having_not_null_clause_single = (
            f" AND COUNT(CASE WHEN {_build_not_null_conditions(variables_for_table)} THEN 1 END) = {len(tps)}"
            if variables_for_table else ""
        )

        pid_filter_condition = _build_pid_filter_conditions(table_type, selected_cohorts)

        # Threshold conditions and params
        th_conditions = []
        params = tp_params.copy()
        for threshold in thresholds or []:
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
            if operator == 'between' and value2 is not None:
                th_conditions.append(f"t.{variable} BETWEEN ? AND ?")
                if data_type == 'number':
                    params.extend([float(value), float(value2)])
                else:
                    params.extend([value, value2])
            elif operator in ['LIKE', 'NOT LIKE']:
                th_conditions.append(f"t.{variable} {operator} ?")
                params.append(f"%{value}%")
            elif operator in ['IS NULL', 'IS NOT NULL']:
                th_conditions.append(f"t.{variable} {operator}")
            else:
                th_conditions.append(f"t.{variable} {operator} ?")
                if data_type == 'number':
                    params.append(float(value))
                else:
                    params.append(value)

        th_sql = (" AND " + " AND ".join(th_conditions)) if th_conditions else ""

        subselects.append(
            f"""
            SELECT t.pid
            FROM {table_name} t
            WHERE t.time_point IN ({','.join(['?' for _ in tps])})
              AND {pid_filter_condition}
              {th_sql}
            GROUP BY t.pid
            HAVING COUNT(DISTINCT t.time_point) = {len(tps)}{having_not_null_clause_single}
            """
        )
        params_all.extend(params)

    if not subselects:
        return "SELECT pid FROM (SELECT NULL as pid) x WHERE 1=0", []

    unioned = "\n            UNION ALL\n            ".join(subselects)
    pid_only_query = f"""
        SELECT DISTINCT pid FROM (
            {unioned}
        ) AS U
    """
    return pid_only_query, params_all

@app.route('/query-data', methods=['POST'])
def query_data():
    """Execute queries based on filter parameters and return counts"""
    try:
        filters = request.json.get('filters', [])
        # Enforce: logicParameters are required and must specify at least one constraint
        if not isinstance(filters, list) or len(filters) == 0:
            return jsonify({'status': 'error', 'message': 'At least one filter with logicParameters is required'}), 400

        for f in filters:
            logic_parameters = f.get('logicParameters') if isinstance(f, dict) else None
            if not logic_parameters or len(logic_parameters) == 0:
                return jsonify({'status': 'error', 'message': 'logicParameters are required for each filter'}), 400
            lp0 = logic_parameters[0] if isinstance(logic_parameters[0], dict) else {}
            has_timepoints = bool(lp0.get('timepoints'))
            has_thresholds = bool(lp0.get('thresholds'))
            has_cohorts = bool(lp0.get('cohorts'))
            has_variables = bool(lp0.get('variables'))
            if not (has_timepoints or has_thresholds or has_cohorts or has_variables):
                return jsonify({'status': 'error', 'message': 'logicParameters must include timepoints, cohorts, thresholds, or variables'}), 400
        
        # Get database connection
        conn = get_db_connection()
        if not conn:
            return jsonify({'status': 'error', 'message': 'Database connection failed'}), 500

        cursor = conn.cursor()
        results = {}
        filter_counts = []  # store per-filter counts for min-based combined

        # Accumulator for a single combined table across all filters
        combined_counts = {
            'total': 0,
            'children': 0,
            'adults': 0,
            'gender': {
                'children': {'M': 0, 'F': 0, 'O': 0},
                'adults': {'M': 0, 'F': 0, 'O': 0}
            }
        }

        def add_counts(target, src):
            target['total'] += int(src.get('total', 0) or 0)
            target['children'] += int(src.get('children', 0) or 0)
            target['adults'] += int(src.get('adults', 0) or 0)
            # genders
            tga = target['gender']['adults']
            tgc = target['gender']['children']
            sga = ((src.get('gender') or {}).get('adults')) or {'M': 0, 'F': 0, 'O': 0}
            sgc = ((src.get('gender') or {}).get('children')) or {'M': 0, 'F': 0, 'O': 0}
            tga['M'] += int(sga.get('M', 0) or 0)
            tga['F'] += int(sga.get('F', 0) or 0)
            tga['O'] += int(sga.get('O', 0) or 0)
            tgc['M'] += int(sgc.get('M', 0) or 0)
            tgc['F'] += int(sgc.get('F', 0) or 0)
            tgc['O'] += int(sgc.get('O', 0) or 0)

        # Process each filter
        filter_pid_sets = []  # list of dicts pid->gender per filter
        filter_pid_queries = []
        filter_pid_params = []
        for filter_item in filters:
            modality = filter_item.get('modality')
            logic_parameters = filter_item.get('logicParameters') or []

            if not modality:
                continue

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
                    
                    # Accumulate per-modality (avoid overwriting when same modality appears multiple times)
                    if modality not in results:
                        results[modality] = {
                            'counts': {
                                'total': 0,
                                'children': 0,
                                'adults': 0,
                                'gender': {
                                    'children': {'M': 0, 'F': 0, 'O': 0},
                                    'adults': {'M': 0, 'F': 0, 'O': 0}
                                }
                            },
                            'query': query
                        }
                    # Add to modality totals
                    add_counts(results[modality]['counts'], counts)
                    # Add to combined totals
                    add_counts(combined_counts, counts)
                    # Track per-filter counts for min-based combination
                    filter_counts.append(counts)
                except pyodbc.Error as e:
                    results[modality] = {
                        'error': str(e),
                        'query': query  # Include failed query for debugging
                    }

                # Prepare PID-only subselect for SQL-level INTERSECT
                try:
                    pid_subselect_sql, pid_subselect_params = build_filter_pid_subselect(modality, logic_parameters)
                    filter_pid_queries.append(pid_subselect_sql)
                    filter_pid_params.extend(pid_subselect_params)
                except Exception:
                    pass

        # Compute true intersection via SQL INTERSECT when 2+ filters
        intersection_counts = {
            'total': 0,
            'children': 0,
            'adults': 0,
            'gender': {
                'children': {'M': 0, 'F': 0, 'O': 0},
                'adults': {'M': 0, 'F': 0, 'O': 0}
            }
        }
        if len(filter_pid_queries) >= 2:
            try:
                intersect_sql = " INTERSECT ".join([f"({q})" for q in filter_pid_queries])
                full_sql = f"""
                    WITH Intersected AS (
                        {intersect_sql}
                    )
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN UPPER(LEFT(pid, 1)) IN ('P', 'S') THEN 1 ELSE 0 END) as adults,
                        SUM(CASE WHEN UPPER(LEFT(pid, 1)) IN ('A', 'B', 'C') THEN 1 ELSE 0 END) as children,
                        SUM(CASE WHEN UPPER(LEFT(pid, 1)) IN ('P', 'S') AND (p.gender IN ('M','MALE') OR LOWER(p.gender)='male') THEN 1 ELSE 0 END) as adults_m,
                        SUM(CASE WHEN UPPER(LEFT(pid, 1)) IN ('P', 'S') AND (p.gender IN ('F','FEMALE') OR LOWER(p.gender)='female') THEN 1 ELSE 0 END) as adults_f,
                        SUM(CASE WHEN UPPER(LEFT(pid, 1)) IN ('P', 'S') AND p.gender IS NOT NULL AND p.gender NOT IN ('M','MALE','F','FEMALE') AND LOWER(p.gender) NOT IN ('male','female') THEN 1 ELSE 0 END) as adults_o,
                        SUM(CASE WHEN UPPER(LEFT(pid, 1)) IN ('A', 'B', 'C') AND (p.gender IN ('M','MALE') OR LOWER(p.gender)='male') THEN 1 ELSE 0 END) as children_m,
                        SUM(CASE WHEN UPPER(LEFT(pid, 1)) IN ('A', 'B', 'C') AND (p.gender IN ('F','FEMALE') OR LOWER(p.gender)='female') THEN 1 ELSE 0 END) as children_f,
                        SUM(CASE WHEN UPPER(LEFT(pid, 1)) IN ('A', 'B', 'C') AND p.gender IS NOT NULL AND p.gender NOT IN ('M','MALE','F','FEMALE') AND LOWER(p.gender) NOT IN ('male','female') THEN 1 ELSE 0 END) as children_o
                    FROM Intersected i
                    LEFT JOIN {PARTICIPANTS_TABLE} p ON i.pid = p.pid
                """
                cursor.execute(full_sql, filter_pid_params)
                row = cursor.fetchone()
                if row:
                    intersection_counts['total'] = int(row[0] or 0)
                    intersection_counts['adults'] = int(row[1] or 0)
                    intersection_counts['children'] = int(row[2] or 0)
                    intersection_counts['gender']['adults']['M'] = int(row[3] or 0)
                    intersection_counts['gender']['adults']['F'] = int(row[4] or 0)
                    intersection_counts['gender']['adults']['O'] = int(row[5] or 0)
                    intersection_counts['gender']['children']['M'] = int(row[6] or 0)
                    intersection_counts['gender']['children']['F'] = int(row[7] or 0)
                    intersection_counts['gender']['children']['O'] = int(row[8] or 0)
            except Exception:
                pass

        # Fallback to Python-side intersection if SQL result is zero but per-filter sets are non-empty
        try:
            if intersection_counts['total'] == 0 and len(filters) >= 2:
                pid_sets = []
                gender_map = {}
                for filter_item in filters:
                    modality = filter_item.get('modality')
                    logic_parameters = filter_item.get('logicParameters') or []
                    if not modality:
                        continue
                    pid_query_full, pid_params_full = build_filter_pid_query(modality, logic_parameters)
                    cursor.execute(pid_query_full, pid_params_full)
                    rows = cursor.fetchall()
                    s = set()
                    for r in rows:
                        if r and len(r) >= 2 and r[0] is not None:
                            pid = str(r[0])
                            s.add(pid)
                            if pid not in gender_map:
                                gender_map[pid] = r[1]
                    if s:
                        pid_sets.append(s)
                if len(pid_sets) >= 2:
                    inter = set.intersection(*pid_sets)
                else:
                    inter = set()

                def cohort_from_pid(pid_value):
                    if not pid_value:
                        return 'other'
                    ch = str(pid_value)[0].upper()
                    if ch in ['A', 'B', 'C']:
                        return 'children'
                    if ch in ['P', 'S']:
                        return 'adults'
                    return 'other'

                # Recompute counts from intersection
                intersection_counts = {
                    'total': 0,
                    'children': 0,
                    'adults': 0,
                    'gender': {
                        'children': {'M': 0, 'F': 0, 'O': 0},
                        'adults': {'M': 0, 'F': 0, 'O': 0}
                    }
                }
                for pid in inter:
                    cohort = cohort_from_pid(pid)
                    if cohort not in ['children', 'adults']:
                        continue
                    intersection_counts['total'] += 1
                    intersection_counts[cohort] += 1
                    g = (gender_map.get(pid) or 'Unknown')
                    g_upper = str(g).upper() if isinstance(g, str) else 'UNKNOWN'
                    if cohort == 'children':
                        if g_upper in ['M', 'MALE']:
                            intersection_counts['gender']['children']['M'] += 1
                        elif g_upper in ['F', 'FEMALE']:
                            intersection_counts['gender']['children']['F'] += 1
                        else:
                            intersection_counts['gender']['children']['O'] += 1
                    else:
                        if g_upper in ['M', 'MALE']:
                            intersection_counts['gender']['adults']['M'] += 1
                        elif g_upper in ['F', 'FEMALE']:
                            intersection_counts['gender']['adults']['F'] += 1
                        else:
                            intersection_counts['gender']['adults']['O'] += 1
        except Exception:
            pass

        # Attach Combined from true intersection (even if zero) for multi-filter searches
        if isinstance(filters, list) and len(filters) >= 2:
            results['Combined'] = { 'counts': intersection_counts }

        cursor.close()
        conn.close()

        return jsonify({
            'status': 'success',
            'results': results
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5001)