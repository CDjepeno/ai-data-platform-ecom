from etl_ecom.application.ports.secondary.semantic_layer_port import SemanticLayerPort


class FakeSemanticLayer(SemanticLayerPort):
    def __init__(self):
        self.dbt_built = False
        self.indexed = False

    def build_dbt(self) -> None:
        self.dbt_built = True

    def index(self) -> None:
        self.indexed = True
