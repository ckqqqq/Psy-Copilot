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
            """All the objective description that appear in the text. Such as client_emotion or therapist_strategy or client_action or target or psychotherapy or client_response or therapist_response or client_issue or      client_background or dialog_topic, please use descriptions with right names. 
            Please focus on describing the therapist's therapist_strategy. Strategies refer to the techniques or actions used by the therapist, such as listening, support, goal setting, cognitive restructuring, etc., to help clients resolve psychological and behavioral issues. 
            """
    )