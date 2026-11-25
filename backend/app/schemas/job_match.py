from pydantic import BaseModel, ConfigDict, Field


class JobMatchRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    job_description: str = Field(
        min_length=1,
        max_length=50000,
    )