from pydantic import BaseModel, ConfigDict


class SafeModel(BaseModel):
    model_config = ConfigDict(
        str_max_length=10000,  # Disallow large strings
        extra="forbid",  # Disallow unexpected input fields to validate everything
        frozen=True,  # Make all the models immutable
        allow_inf_nan=False,  # Disallow float infinity
    )
