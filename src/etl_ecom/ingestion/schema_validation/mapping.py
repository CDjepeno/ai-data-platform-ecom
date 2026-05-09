TYPE_MAPPING = {
    # integers
    "integer": "int",
    "bigint": "long",
    "smallint": "int",

    # strings
    "character varying": "string",
    "text": "string",

    # timestamps
    "timestamp without time zone": "timestamp",
    "timestamp with time zone": "timestamptz",

    # numeric
    "numeric": "decimal",
    "double precision": "double",
    "real": "float",

    # booleans
    "boolean": "boolean",

    # postgres enum
    "user-defined": "string"
}