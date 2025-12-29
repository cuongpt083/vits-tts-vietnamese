import jsonschema
def validate_query_params(query_schema):
    def decorator(handler_method):
        def wrapper(self, *args, **kwargs):
            # Get only provided query parameters as a dictionary.
            # Missing optional params should be absent (not present as null),
            # so JSON schema `required` and `default` behavior works as expected.
            query_params = {}
            for key in query_schema["properties"].keys():
                value = self.get_argument(key, default=None)
                if value is not None:
                    query_params[key] = value
            
            try:
                # Validate the query parameters against the JSON schema
                jsonschema.validate(query_params, query_schema)
            except jsonschema.exceptions.ValidationError as e:
                self.set_status(400)  # Bad Request
                self.write(f"Query parameter validation failed: {str(e)}")
                return

            # All parameters are valid, proceed with the original handler method
            return handler_method(self, *args, **kwargs)
        return wrapper
    return decorator
