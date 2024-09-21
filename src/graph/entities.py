# from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List
from pydantic import BaseModel, Field
class Entities(BaseModel):
    """
    定义的结构化输出，从而langchain 能够直接指定某一个特定类别的输出
    Identify and capture information about entities from text
    """

    names: List[str] = Field(
        description=
            "All the psychotherapy, counseling cases, emotional states, cognitive distortions, behavioral patterns, interpersonal interactions, self-perception, life events, cultural factors, and physical health entities that appear in the text",
    )