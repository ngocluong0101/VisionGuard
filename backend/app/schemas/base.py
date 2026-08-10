from pydantic import BaseModel, ConfigDict


class SchemaBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid", populate_by_name=True)