import asyncio
import json
from typing import Any, Dict, List, Optional, Sequence, Tuple, Type, Union, cast

from langchain_community.graphs.graph_document import GraphDocument, Node, Relationship
from langchain_core.documents import Document
from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    PromptTemplate,
)
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field, create_model

examples = [
    {
        "text": (
            """The therapist isolates and elicits worrying thoughts from the client to understand her subjective experience. Clear expression of negative automatic thoughts (NATs) allows for the development of adaptive responses. NATs, when phrased telegraphically, can be challenging to examine and respond to."""
        ),
        "head": "The therapist isolates and elicits worrying thoughts from the client",
        "head_type": "Therapist Strategy",
        "relation": "Help",
        "tail": "Understand her subjective experience.",
        "tail_type": "Target",
    },
    {
        "text": (
            """The therapist isolates and elicits worrying thoughts from the client to understand her subjective experience. Clear expression of negative automatic thoughts (NATs) allows for the development of adaptive responses. NATs, when phrased telegraphically, can be challenging to examine and respond to."""
        ),
        "head": "For Therapist, clear expression of negative automatic thoughts (NATs)",
        "head_type": "Strategy",
        "relation": "Help",
        "tail": "the development of client's adaptive responses.",
        "tail_type": "Target",
    },
    {
        "text": (
            "When clients reach a cognitive block and respond with ‘I don’t know’, "
            "therapists can provide suggestions based on case conceptualization or clinical experience to address the issue."
        ),
       "head": "Clients reach a cognitive block and respond with ‘I don’t know’",
    "head_type": "Client Issue",
    "relation": "Prompt",
    "tail": "Therapists to provide suggestions based on case conceptualization or clinical experience to address the issue",
    "tail_type": "Strategy"
    },
    {
        "text": (
            """The therapist's suggestions can stimulate productive introspection in the client, but an excess of suggestions may lead to client passivity. It is important for the therapist to assess the client's response to suggestions to ensure genuine progress in therapy. Additionally, suggesting opposite thoughts can help clients explore their automatic thoughts and underlying beliefs."""
        ),
        "head": "An excess of therapist's suggestions may lead to client passivity",
        "head_type": "Client Issue",
        "relation": "Prompt",
        "tail": "Therapist can assess client's response to suggestions for genuine progress and suggest opposite thoughts to explore automatic thoughts and underlying beliefs.",
        "tail_type": "Therapist Strategy",
    },
    {
        "text": (
            """The client’s response contains 'hot thoughts' that are closely linked to emotions and drive the emotional intensity. These thoughts are crucial in CBT for modification. """
        ),
        "head": "A client with performance anxiety is prompted to consider the worst-case scenario.",
        "head_type": "Client Issue",
        "relation": "Lead to",
        "tail": "Therapist can Identify and address 'hot thoughts', encourage vivid imagination of problematic situations, ask about worst possible outcomes, help develop adaptive responses, challenge catastrophic thinking.",
        "tail_type": "Therapist Strategy",
    },
    {
        "text": (
            """The client’s response contains 'hot thoughts' that are closely linked to emotions and drive the emotional intensity. These thoughts are crucial in CBT for modification. Therapists focus on identifying and addressing these 'hot' automatic thoughts to understand the client's emotional reactions effectively. Encouraging clients to vividly imagine problematic situations can expedite the discovery of these 'hot' automatic thoughts. Asking clients about the worst possible outcomes can be an effective technique to elicit and address negative automatic thoughts, especially when they involve highly distorted future events. This approach can help clients develop adaptive responses and challenge catastrophic thinking patterns, as demonstrated in a scenario where a client with performance anxiety is prompted to consider the worst-case scenario. """
        ),
    "head": "Client with performance anxiety has response contains 'hot thoughts' that are closely linked to emotions and drive the emotional intensity. ",
    "head_type": "Client Issue",
    "relation": "Prompt",
    "tail": "Therapist to identify and address 'hot thoughts', encourage vivid imagination, ask about worst outcomes, develop adaptive responses, challenge catastrophic thinking",
    "tail_type": "Therapist Strategy"
    },
    {
        "text": (
            """The client’s response contains 'hot thoughts' that are closely linked to emotions and drive the emotional intensity. These thoughts are crucial in CBT for modification. """
        ),
    "head": "Client's response contains 'hot thoughts' that are closely linked to emotions and drive the emotional intensity. ",
    "head_type": "Client Emotion",
    "relation": "Be Crucial For",
    "tail": "Cognitive Behavioral Therapy for modification",
    "tail_type": "Psychotherapy"
    },
    {
    "text": (
        """For instance, accompanying a client afraid of eating in public to a café can activate their hot thoughts. The client’s answer is filled with ‘hot thoughts’, which are crucial for understanding and modifying emotional reactions. """
    ),
    "head": "Therapist accompanies a client afraid of eating in public to a café",
    "head_type": "Therapist Strategy",
    "relation": "Help",
    "tail": "Client to activate hot thoughts for understanding and modifying emotional reactions",
    "tail_type": "Client Response"
    }
    # {
    #     "text": "来访者: 我好想减肥，但是我总是做不到。\n治疗师: 好吧，总是不断重新开始减肥的人基本上存在一个问题，那就是他们往往会很快放弃自己的减肥计划然后看着体重回升。",
    #     "head": "来访者: 我好想减肥，但是我总是做不到。",
    #     "head_type": "Client Response",
    #     "relation": "Suggestion",
    #     "tail": "治疗师: 好吧，总是不断重新开始减肥的人基本上存在一个问题，那就是他们往往会很快放弃自己的减肥计划然后看着体重回升。",
    #     "tail_type": "Therapist Response",
    # },
    # {
    #     "text": "住院医生对病人的反应感到惊讶，并进一步探讨了病人对这种情况的内疚或良心的感觉。",
    #     "head": "病人的内疚或良心的感觉",
    #     "head_type": "Client Emotion",
    #     "relation": "Development",
    #     "tail": "住院医生进一步探讨病人的情感反应",
    #     "tail_type": "Strategy"
    # },
    # {
    #     "text": "在以解决方案为中心的简短治疗中，探索杰克被治疗师盯上和尴尬的感受是必不可少的。通过了解杰克的观点和情绪，治疗师可以帮助他探索潜在的解决方案和应对策略。",
    #     "head": "在以解决方案为中心的简短治疗中",
    #     "head_type": "Client Emotion",
    #     "relation": "Evaluation",
    #     "tail": "探索杰克被治疗师盯上和尴尬的感受是必不可少的",
    #     "tail_type": "Therapist Strategy"
    # },
    # {
    #     "text": "鼓励来访者直接与保护性服务工作者交谈，阐明他们的期望，有助于依从性和决策。通过保持工作者作为孩子监护权的决策者，治疗师可以专注于支持来访者，而不会产生角色冲突。",
    #     "head": "治疗师产生角色冲突，无法专注于支持来访者",
    #     "head_type": "Counseling Issue",
    #     "relation": "Guidance",
    #     "tail": "治疗师鼓励来访者与保护性服务工作者直接交谈，从而可以专注于支持来访者",
    #     "tail_type": "Therapist Strategy"
    # }
]

class UnstructuredRelation(BaseModel):
    head: str = Field(
        description=(
            "extracted Brief description of subject property "
            "Must use human-readable unique identifier."
        )
    )
    head_type: str = Field(
        description="type of the extracted description in counseling like Client Emotion, Strategy, Client Issue etc"
    )
    relation: str = Field(description="relation between the head and the tail entities such as Help, Prevent, Be Crucial For")
    tail: str = Field(
        description=(
            "Brief description of predicate property. "
            "Must use human-readable unique identifier."
        )
    )
    tail_type: str = Field(
        description="type of the extracted description in counseling like Client Emotion, Strategy, Client Issue etc"
    )



def create_unstructured_prompt_for_psy_insight(
    node_labels: Optional[List[str]] = None, rel_types: Optional[List[str]] = None
) -> ChatPromptTemplate:
    """生成一个一个将心理咨询文档的字符串切片自动解析为知识图谱的切片的prompt"""
    node_labels_str = str(node_labels) if node_labels else ""
    rel_types_str = str(rel_types) if rel_types else ""
    base_string_parts = [
        "# Knowledge Graph Instructions for GPT-4",
        "## 1. Overview",
        "You are a top-tier algorithm designed for extracting information in structured "
        "formats to build a knowledge graph.",
        "Try to capture as much information from the text as possible without sacrificing accuracy.",
        "Do not add any information that is not explicitly provided.",
        "Your task is to identify the entities and relations requested with the user prompt from a given text.",
        "- **Nodes** represent descriptions or entities such as Visitor Emotion, Therapist Strategy, Session Stage, Psychotherapy Technique, Therapist Action, Issue Topic.",
        "The aim is to achieve simplicity and clarity in the knowledge graph, making it accessible for a vast audience.", 
        "## 2. Labeling Nodes",
        "- **Consistency**: Ensure you use available types for node labels.",
        f"Ensure you use basic or elementary types for node labels. Use one of the types from {node_labels_str}."
        if node_labels else "",
        "- For example, when you identify an entity representing a Psychotherapy, always label it as **'Psychotherapy'**. Avoid using more specific terms like 'mathematician' or 'scientist'.",
        "- **Node IDs**: Never utilize integers as node IDs. Node IDs should be names or human-readable identifiers found in the text.",
        "## 3. Relationships",
        "- **Relationships** represent connections between entities such as 'Session Stage' (is) 'Early Session' or therapist (use) xx technique.",
        f"Use one of the relationship types from {rel_types_str}."
        if rel_types else "",
        "Ensure consistency and generality in relationship types when constructing knowledge graphs.",
        "Instead of using specific and momentary types such as 'BECAME_PROFESSOR', use more general and timeless relationship types like 'PROFESSOR'.",
        "## 4. Coreference Resolution",
        "- **Maintain Entity Consistency**: When extracting entities, it's vital to ensure consistency.",
        'If an entity, such as "John Doe", is mentioned multiple times in the text but is referred to by different names or pronouns (e.g., "Joe", "he"), always use the most complete identifier for that entity throughout the knowledge graph.',
        "In this example, use 'John Doe' as the entity ID.",
        "Remember, the knowledge graph should be coherent and easily understandable, so maintaining consistency in entity references is crucial.",
        "## 5. Strict Compliance",
        "Adhere to the rules strictly. Non-compliance will result in termination.",
        "",
    ]
    # TODO 尚未确定是否需要限制标签类别 fewshot=["Therapist strategies includes follow examples："]
    
    system_prompt = "\n".join(filter(None, base_string_parts))

    system_message = SystemMessage(content=system_prompt)
    parser = JsonOutputParser(pydantic_object=UnstructuredRelation)

    human_string_parts = [
        "Based on the following example, extract entities and "
        "relations from the provided text.\n\n",
        "Use the following entity types, don't use other entity "
        "that is not defined below:"
        "# ENTITY TYPES:"
        "{node_labels}"
        if node_labels
        else "",
        "Use the following relation types, don't use other relation "
        "that is not defined below:"
        "# RELATION TYPES:"
        "{rel_types}"
        if rel_types
        else "",
        "Below are a number of examples of text and their extracted "
        "entities and relationships."
        "{examples}\n"
        "For the following text, extract entities and relations as "
        "in the provided example."
        "{format_instructions}\nText: {input}",
    ]
    # 这是关键的部分，基于这个systemprompt 去做提示工程
    human_prompt_string = "\n".join(filter(None, human_string_parts))
    human_prompt = PromptTemplate(
        template=human_prompt_string,
        input_variables=["input"],
        partial_variables={
            "format_instructions": parser.get_format_instructions(),
            "node_labels": node_labels,
            "rel_types": rel_types,
            "examples": examples,
        },
    )

    human_message_prompt = HumanMessagePromptTemplate(prompt=human_prompt)

    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message, human_message_prompt]
    )
    return chat_prompt