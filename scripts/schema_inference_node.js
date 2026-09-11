/**
 * AI Data Governor — Dynamic Schema Inference & DDL Generator (n8n Code Node)
 * 
 * Purpose:
 * Runs inside an n8n JavaScript Code Node immediately after a file upload
 * (CSV or Excel). Normalizes headers, infers PostgreSQL data types, generates
 * dynamic 'CREATE TABLE IF NOT EXISTS' DDL, and formats records for batch insertion.
 */

function sanitizeColumnName(rawCol) {
    if (!rawCol || typeof rawCol !== 'string') return 'column_unnamed';
    let col = rawCol.trim().toLowerCase();
    // Replace non-alphanumeric chars with underscore
    col = col.replace(/[^a-z0-9_]+/g, '_');
    // Strip leading/trailing underscores
    col = col.replace(/^_+|_+$/g, '');
    // Ensure doesn't start with a number
    if (/^[0-9]/.test(col)) {
        col = 'col_' + col;
    }
    // Reserved SQL keywords check
    const reserved = ['user', 'order', 'group', 'table', 'select', 'primary', 'check', 'limit'];
    if (reserved.includes(col)) {
        col = col + '_val';
    }
    return col || 'column_unnamed';
}

function inferColumnType(values) {
    // Sample non-null, non-empty values
    const nonNulls = values
        .filter(v => v !== null && v !== undefined && String(v).trim() !== '' && String(v).toUpperCase() !== 'NULL');
    
    if (nonNulls.length === 0) {
        return 'TEXT';
    }

    // Check for pure ISO dates (YYYY-MM-DD)
    const isDate = nonNulls.every(v => /^\d{4}-\d{2}-\d{2}$/.test(String(v).trim()));
    if (isDate) {
        return 'DATE';
    }

    // Check for pure integers
    const isInteger = nonNulls.every(v => /^-?\d+$/.test(String(v).trim()));
    if (isInteger) {
        return 'INTEGER';
    }

    // Check for general numbers / decimals
    const isNumeric = nonNulls.every(v => /^-?\d+(\.\d+)?$/.test(String(v).trim()));
    if (isNumeric) {
        return 'NUMERIC';
    }

    // Default to TEXT for resilience against dirty values (e.g. "9 units", "UNKNOWN", trailing spaces)
    return 'TEXT';
}

function parseCSV(csvText) {
    const lines = csvText.split(/\r?\n/).filter(line => line.trim() !== '');
    if (lines.length === 0) return { headers: [], rows: [] };

    // Basic CSV parser handling quoted strings
    const parseLine = (text) => {
        const result = [];
        let cur = '';
        let inQuotes = false;
        for (let i = 0; i < text.length; i++) {
            const char = text[i];
            if (char === '"') {
                if (inQuotes && text[i + 1] === '"') {
                    cur += '"';
                    i++;
                } else {
                    inQuotes = !inQuotes;
                }
            } else if (char === ',' && !inQuotes) {
                result.push(cur.trim());
                cur = '';
            } else {
                cur += char;
            }
        }
        result.push(cur.trim());
        return result;
    };

    const rawHeaders = parseLine(lines[0]);
    const rows = [];
    for (let i = 1; i < lines.length; i++) {
        const vals = parseLine(lines[i]);
        if (vals.length === rawHeaders.length) {
            const rowObj = {};
            for (let j = 0; j < rawHeaders.length; j++) {
                rowObj[rawHeaders[j]] = vals[j];
            }
            rows.push(rowObj);
        }
    }
    return { headers: rawHeaders, rows };
}

function processUploadedDataset(fileName, rawRowsOrCsvText) {
    // 1. Determine table name from file
    let cleanTableName = (fileName || 'imported_dataset')
        .toLowerCase()
        .replace(/\.[^/.]+$/, '') // remove extension
        .replace(/[^a-z0-9_]+/g, '_')
        .replace(/^_+|_+$/g, '');
    
    if (!cleanTableName) cleanTableName = 'imported_dataset';

    // 2. Extract rows and headers
    let rawHeaders = [];
    let rows = [];

    if (typeof rawRowsOrCsvText === 'string') {
        const parsed = parseCSV(rawRowsOrCsvText);
        rawHeaders = parsed.headers;
        rows = parsed.rows;
    } else if (Array.isArray(rawRowsOrCsvText) && rawRowsOrCsvText.length > 0) {
        rows = rawRowsOrCsvText;
        rawHeaders = Object.keys(rows[0]);
    }

    if (rawHeaders.length === 0) {
        throw new Error('No valid columns found in uploaded file.');
    }

    // 3. Map sanitized column names
    const colMap = {};
    const sanitizedCols = [];
    const usedNames = new Set();

    for (const raw of rawHeaders) {
        let clean = sanitizeColumnName(raw);
        let counter = 1;
        while (usedNames.has(clean)) {
            clean = `${sanitizeColumnName(raw)}_${counter++}`;
        }
        usedNames.add(clean);
        colMap[raw] = clean;
        sanitizedCols.push(clean);
    }

    // 4. Infer types
    const columnDefinitions = [];
    const inferredTypes = {};

    for (const raw of rawHeaders) {
        const clean = colMap[raw];
        const sampleValues = rows.slice(0, 100).map(r => r[raw]);
        const inferredType = inferColumnType(sampleValues);
        inferredTypes[clean] = inferredType;
        columnDefinitions.push(`    "${clean}" ${inferredType}`);
    }

    // 5. Generate DDL
    const ddl = `CREATE TABLE IF NOT EXISTS "${cleanTableName}" (\n${columnDefinitions.join(',\n')}\n);`;

    // 6. Map rows to sanitized headers
    const sanitizedRows = rows.map(r => {
        const cleanRow = {};
        for (const raw of rawHeaders) {
            const cleanCol = colMap[raw];
            let val = r[raw];
            if (val === undefined || val === null || String(val).trim() === '' || String(val).toUpperCase() === 'NULL') {
                cleanRow[cleanCol] = null;
            } else {
                cleanRow[cleanCol] = val;
            }
        }
        return cleanRow;
    });

    return {
        table_name: cleanTableName,
        create_table_ddl: ddl,
        columns: sanitizedCols,
        inferred_types: inferredTypes,
        total_rows: sanitizedRows.length,
        sanitized_rows: sanitizedRows
    };
}

// Export for Node.js testing & n8n execution compatibility
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        sanitizeColumnName,
        inferColumnType,
        parseCSV,
        processUploadedDataset
    };
}

// In n8n Code Node, the execution block is:
// const fileData = $input.first().binary.data;
// ... processUploadedDataset(fileName, csvText) ...
