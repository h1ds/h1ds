MODULE_DOC_NAME = "Summary"
SUMMARY_TABLE_NAME = "summary"
MINIMUM_SUMMARY_TABLE_SHOT = 58000

# Map mdsplus datatypes to MySQL datatypes
# TODO: This should not depend on the database type, check that we don't
# restrict ourselves to MySQL over postgres, etc
# The single-character SQL type codes are mapped to the actual types in h1ds_summary.models.sql_type_codes
MDS_SQL_MAP = {
    'DTYPE_FLOAT':'F',
    }
