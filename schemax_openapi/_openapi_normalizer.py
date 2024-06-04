from typing import Any, Dict

import jsonschema


def openapi_normalizer(value: Dict[str, Any]) -> Dict[str, Any]:
    def schema_runner(
        schema: Dict[str, Any], resolver: jsonschema.RefResolver
    ) -> Dict[str, Any]:
        if isinstance(schema, dict):
            if "$ref" in schema:
                with resolver.resolving(schema["$ref"]) as resolved:
                    return schema_runner(resolved, resolver)
            else:
                return {k: schema_runner(v, resolver) for k, v in schema.items()}
        elif isinstance(schema, list):
            return [schema_runner(item, resolver) for item in schema]  # noqa
        else:
            return schema

    ref_resolver = jsonschema.RefResolver("", value)
    return schema_runner(value, ref_resolver)
