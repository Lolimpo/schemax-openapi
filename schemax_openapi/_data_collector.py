import re
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Union

from district42 import GenericSchema
from schemax import from_json_schema

from ._openapi_normalizer import openapi_normalizer


@dataclass
class SchemaData:
    """Data collector class.

    Attributes:
        http_method: HTTP method of the request.
        path: URL path of the request.
        converted_path: URL path converted to the camel-case for usage in schemax generation.
        args: Arguments of the request.
        queries: Query parameters of the request. Currently unsupported and always '[]'.
        interface_method: Interface name for usage in schemax generation.
        schema_prefix: Schema prefix name for usage in schemax generation.
        response_schema: Normalized response schema (without $ref).
        response_schema_d42: Converted to d42 response_schema.
        request_schema: Normalized request schema (without $ref).
        request_schema_d42: Converted to d42 request_schema.
        tags: Tags of the request from OpenAPI schema.
    """
    http_method: str
    path: str
    converted_path: str
    args: List[str]
    queries: List[str]
    interface_method: str
    status: Union[str, int]
    schema_prefix: str
    response_schema: Dict[str, Any]
    response_schema_d42: GenericSchema
    request_schema: Dict[str, Any]
    request_schema_d42: GenericSchema
    tags: List[str]


def collect_schema_data(value: Dict[str, Any]) -> List[SchemaData]:
    normalized_schema = openapi_normalizer(value)
    paths_data = normalized_schema.get("paths", {})

    return [
        schema_data
        for path, path_data in paths_data.items()
        for schema_data in process_paths(path, path_data)
    ]


def process_paths(path: str, path_data: Dict[str, Any]) -> List[SchemaData]:
    paths = get_enum_paths(path, path_data)
    if not paths:
        paths = [path]

    return [
        process_method_data(enum_path, http_method, method_data)
        for enum_path in paths
        for http_method, method_data in path_data.items()
        if http_method.lower() in ["get", "post", "put", "patch", "delete"]
    ]


def get_enum_paths(path: str, path_data: Dict[str, Any]) -> List[str]:
    paths = []
    parameters = path_data.get("parameters", [])
    for parameter in parameters:
        if parameter["in"] == "path" and "enum" in parameter["schema"]:
            for enum_item in parameter["schema"]["enum"]:
                paths.append(path.replace(f"{{{parameter['name']}}}", enum_item))
    return paths


def process_method_data(path: str, http_method: str, method_data: Dict[str, Any]) -> SchemaData:
    request_schema, response_schema = get_request_response_schemas(method_data)

    args = get_path_arguments(path)
    if request_schema:
        args.append("body")

    return SchemaData(
        http_method=http_method,
        path=path,
        converted_path=convert_to_snake_case(path),
        args=args,
        queries=get_queries(method_data),
        interface_method=get_interface_method_name(http_method, path),
        status=get_success_status(method_data),
        schema_prefix=get_schema_prefix(http_method, path),
        response_schema=response_schema,
        response_schema_d42=from_json_schema(response_schema),
        request_schema=request_schema,
        request_schema_d42=from_json_schema(request_schema),
        tags=method_data.get("tags", [])
    )


def get_request_response_schemas(
    method_data: Dict[str, Any]
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    request_schema: Dict[str, Any] = {}
    response_schema: Dict[str, Any] = {}

    if "requestBody" in method_data:
        request_schema = get_request_schema(method_data["requestBody"])
    elif "parameters" in method_data:
        request_schema = get_request_schema_from_parameters(method_data["parameters"])

    if "responses" in method_data:
        response_schema = get_response_schema(method_data["responses"])

    return request_schema, response_schema


def get_request_schema(request_body: Dict[str, Any]) -> Dict[str, Any]:
    content = request_body.get("content", {})
    json_content = content.get("application/json", {}).get("schema", {})
    return json_content  # type: ignore


def get_request_schema_from_parameters(parameters: List[Dict[str, Any]]) -> Dict[str, Any]:
    for param in parameters:
        if param["in"] == "body":
            return param["schema"]  # type: ignore
    return {}


def get_response_schema(responses: Dict[str, Any]) -> Dict[str, Any]:
    for status, status_data in responses.items():
        if str(status) == "200":
            content = status_data.get("content", {})
            content_schema: Dict[str, Any] = content.get(next(iter(content)), {}).get("schema", {})
            return content_schema
    return {}


def get_path_arguments(path: str) -> List[str]:
    return [convert_to_snake_case(arg) for arg in re.findall(r"{([^}]+)}", path)]


def get_queries(method_data: Dict[str, Any]) -> List[str]:
    queries = []
    for source in [method_data.get("parameters", [])]:
        for parameter in source:
            if parameter["in"] == "query" and parameter["name"] not in queries:
                queries.append(parameter["name"])
    return queries


def get_interface_method_name(http_method: str, path: str) -> str:
    return (
        http_method.lower() +
        "_".join(
            convert_to_snake_case(word)
            .replace("{", "")
            .replace("}", "")
            .replace("-", "_")
            .replace(".", "_")
            .lower()
            for word in path.split("/")
        )
    )


def get_success_status(method_data: Dict[str, Any]) -> Union[str, int]:
    success_statuses = ["200", 200]
    for status in success_statuses:
        if status in method_data.get("responses", {}):
            return status  # type: ignore
    return ""


def get_schema_prefix(http_method: str, path: str) -> str:
    return (
        http_method.capitalize() +
        "".join(
            word
            .replace("{", "")
            .replace("}", "")
            .replace("-", "")
            .capitalize()
            for word in path.split("/")
        )
    )


def convert_to_snake_case(input_string: str) -> str:
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', input_string).lower()
