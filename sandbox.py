import yaml

from openapi_parser import collect_schema_data

with open('schema-keys-reduced.yml') as schema_file:
    raw_schema = yaml.load(schema_file, yaml.FullLoader)

    parsed_data = collect_schema_data(raw_schema)
    for item in parsed_data:
        print(item.schema_prefix)
