from etl_ecom.application.ports.secondary.schema_validator_port import SchemaValidatorPort


class FakeSchemaValidator(SchemaValidatorPort):
    def __init__(self, should_raise: bool = False):
        self.called = False
        self._should_raise = should_raise

    def validate(self) -> None:
        self.called = True
        if self._should_raise:
            raise Exception("Schema drift detected")
