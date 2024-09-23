# OpenAPI Parser

Useful for d42 universe and schemax lib.


### Installation
```sh
python3 -m pip install schemax-openapi
```

### Usage

```python3
import yaml
import schemax_openapi
from schemax_openapi import SchemaData

from typing import List

# Also could be JSON OpenAPI file
with open('my_openapi.yaml') as schema_file:
    raw_schema = yaml.load(schema_file, yaml.FullLoader)
    
    parsed_data: List[SchemaData] = schemax_openapi.collect_schema_data(raw_schema)
    for item in parsed_data:
        print(item.path)
        print(item.response_schema_d42)
        ...
```

All the data is stored in `SchemaData` object, which has the following fields:
* http_method: HTTP method of the request.
* path: URL path of the request. 
* converted_path: URL path converted to the camel-case for usage in schemax generation. 
* args: Arguments of the request.
* queries: Query parameters of the request. Currently unsupported and always empty list: `[]`. 
* interface_method: Interface name for usage in schemax generation. 
* interface_method_humanized: Interface 'humanized' name for usage in schemax generation. 
* schema_prefix: Schema prefix name for usage in schemax generation. 
* schema_prefix_humanized: Schema prefix 'humanized' name for user in schemax generation. 
* response_schema: Normalized response schema (without $ref). 
* response_schema_d42: Converted to d42 response_schema. 
* request_schema: Normalized request schema (without $ref). 
* request_schema_d42: Converted to d42 request_schema. 
* tags: Tags of the request from OpenAPI schema.
