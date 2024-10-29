from typing import List
from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain_community.vectorstores.neo4j_vector import remove_lucene_chars
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from src.graph.entities import Entities
import os

from pydantic import BaseModel
from typing import List, Optional

class Entities(BaseModel):
    psychotherapy_techniques: Optional[List[str]] = []
    counseling_cases: Optional[List[str]] = []
    emotional_states: Optional[List[str]] = []
    cognitive_distortions: Optional[List[str]] = []
    behavioral_patterns: Optional[List[str]] = []
    interpersonal_interactions: Optional[List[str]] = []
    self_perception: Optional[List[str]] = []
    life_events: Optional[List[str]] = []
    cultural_factors: Optional[List[str]] = []
    physical_health_entities: Optional[List[str]] = []


class GraphRAG():
    """
    这个类是用于从三元组中抽取知识图谱的关键
    Class to encapsulate all methods required to query a graph for retrieval augmented generation
    """

    def __init__(self, llm):
        self.graph = Neo4jGraph()
        self.llm = llm

    def create_entity_extract_chain(self):
        """
        从问题中抽取实体出来，使用用户所使用的语言。
        Returns a runnable chain which extracts entities from the user’s question.
        """
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                    You are an expert in psychotherapy and related fields. Your task is to extract relevant entities from the user's input. 
                    The entities should be related to the following categories:
                    
                    - **Psychotherapy techniques**: Cognitive-behavioral therapy (CBT), Dialectical behavior therapy (DBT), exposure therapy, etc.
                    - **Counseling cases**: Client issues such as trauma, addiction, relationship issues, work stress.
                    - **Emotional states**: Anxiety, depression, anger, sadness, joy, etc.
                    - **Cognitive distortions**: Overgeneralization, black-and-white thinking, catastrophizing, etc.
                    - **Behavioral patterns**: Avoidance, procrastination, risk-taking, etc.
                    - **Interpersonal interactions**: Conflicts, communication patterns, support systems.
                    - **Self-perception**: Low self-esteem, self-doubt, self-confidence, etc.
                    - **Life events**: Major life transitions like divorce, job loss, moving, etc.
                    - **Cultural factors**: Family traditions, societal expectations, community values.
                    - **Physical health entities**: Issues affecting mental health, such as chronic illness, disability, and physical health conditions.
                    
                    **Important:** Please ignore any information not related to psychotherapy or mental health. Do not include generic information that falls outside of these areas. For example, if the input includes financial advice, legal terminology, or general health issues unrelated to mental health, omit them.

                    Use the user’s native language in your responses, and ensure that the output format is structured clearly. Provide your output in JSON format, where each entity falls under the categories above. If an entity doesn't fit any category, ignore it.
                    
                    **Please return the results strictly in the following JSON format:**
                    ```json
                    {{
                        "psychotherapy_techniques": [],
                        "counseling_cases": [],
                        "emotional_states": [],
                        "cognitive_distortions": [],
                        "behavioral_patterns": [],
                        "interpersonal_interactions": [],
                        "self_perception": [],
                        "life_events": [],
                        "cultural_factors": [],
                        "physical_health_entities": []
                    }}
                    ```
                    
                    Ensure to categorize the entities under the right headings. If no entities are relevant, return an empty JSON.                    
                    """
                ),
                (
                    "human",
                    "Please extract relevant entities from the following input: {question}."
                    "Use the format provided above to structure your response.",
                ),
            ]
        )

        entity_extract_chain = prompt | self.llm.with_structured_output(Entities)
        return entity_extract_chain

    def generate_full_text_query(self, input_query: str) -> str:
        """
        根据实体长度自动调整相似度阈值，并使用LLM重写更精确的查询字符串。
        """
        # 使用LLM重写查询字符串，使其更精确
        refined_query = self.refine_query_with_llm(input_query)

        # 移除Lucene中的特殊字符，并将字符串按空格分割成单词
        words = [el for el in remove_lucene_chars(refined_query).split() if el]

        # 根据实体长度动态调整相似度阈值
        def get_similarity_threshold(word):
            if len(word) <= 4:
                return 1  # 短词，允许1个字符的差异
            elif len(word) <= 8:
                return 2  # 中等长度，允许2个字符的差异
            else:
                return 3  # 长词，允许3个字符的差异

        # 构建全文搜索查询字符串
        full_text_query = ""
        for word in words[:-1]:
            threshold = get_similarity_threshold(word)
            full_text_query += f" {word}~{threshold} AND"
        # 处理最后一个单词
        threshold = get_similarity_threshold(words[-1])
        full_text_query += f" {words[-1]}~{threshold}"

        return full_text_query.strip()

    def refine_query_with_llm(self, input_query: str) -> str:
        """
        使用LLM重写输入的查询字符串，使其更精确。
        """
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "As a knowledgeable assistant, please rewrite the following entity to be more precise and suitable for database querying."
                ),
                (
                    "human",
                    f"Entity: {input_query}\n\nRefined Query:"
                ),
            ]
        )

        # 使用 `prompt.format` 来生成格式化后的字符串
        formatted_prompt = prompt.format(question=input_query)

        # 调用 LLM 的 invoke 方法来生成查询
        refined_query = self.llm.invoke(formatted_prompt)

        # 检查LLM的返回结果，并获取其文本内容
        if hasattr(refined_query, 'content'):
            return refined_query.content.strip()  # 使用 content 属性来提取实际文本
        else:
            raise ValueError("LLM returned an unexpected response format.")

    def structured_retriever(self, question: str, result_num_limit: int, exclude_relations: list) -> List[str]:
        print(f"Structured Search query: {question}", "*" * 10)
        entity_extract_chain = self.create_entity_extract_chain()
        entities = entity_extract_chain.invoke({"question": question})
        print("实体提取", entities)

        results = []
        # 获取 Entities 对象的所有字段名称
        for category in entities.__fields__:
            entity_list = getattr(entities, category)
            if entity_list:
                for entity in entity_list:
                    # 使用生成的全文搜索查询字符串
                    query_str = self.generate_full_text_query(entity)
                    response = self.graph.query(
                        """
                        CALL db.index.fulltext.queryNodes('entity', $query, {limit: $limit})
                        YIELD node, score
                        MATCH (node)-[r]-(neighbor)
                        WHERE NOT type(r) IN $exclude_relations
                        RETURN node.id + ' - ' + type(r) + ' -> ' + neighbor.id AS output
                        LIMIT $limit
                        """,
                        {
                            "query": query_str,
                            "limit": result_num_limit,
                            "exclude_relations": exclude_relations
                        }
                    )
                    results.extend([el['output'] for el in response])

        return results
    
    def unstructured_retriever(self, question: str, embedding_model, exclude_relations: list) -> dict:
        """
        基于向量相似度的非结构化检索方法，用于文本片段的相似性搜索。
        Unstructured retrieval based on vector similarity using vector embeddings.
        """
        print(f"Unstructured Search query: {question}")
        vector_index = Neo4jVector.from_existing_graph(
            embedding_model,
            search_type="hybrid",  # 指定搜索类型为混合搜索
            node_label="Therapist strategy",  # 节点标签
            text_node_properties=["id", "text"],  # 节点中包含的文本属性
            embedding_node_property="embedding"  # 嵌入的节点属性
        )

        # 执行相似性搜索，获取与问题最相关的文档
        search_results = vector_index.similarity_search(question)

        # 将搜索结果转换为文档内容的列表
        doc_list = [str(el.page_content) for el in search_results]

        # 初始化一个列表来存储节点ID
        doc_node_id_list = []

        # 遍历每个文档片段
        for document_page in doc_list:
            for line in document_page.split("\n"):
                if "id" in line:
                    id = line.split("id: ")[-1].strip()
                    doc_node_id_list.append(id)

        # 返回结果，包括检索到的文档内容和对应的节点ID
        return {"documents": doc_list, "node_ids": doc_node_id_list}

    def mix_retriever(self, question: str, result_num_limit=5) -> str:
        """
        结合结构化和非结构化方法的混合检索器。
        Combines both structured and unstructured retrieval methods into a single function.
        """
        # 使用非结构化检索器进行向量搜索，获取文档列表和节点ID列表
        unstructured_result = self.unstructured_retriever(
            question,
            embedding_model=OpenAIEmbeddings(),
            exclude_relations=["MENTIONS"]
        )
        unstructured_data = unstructured_result["documents"]

        print("向量搜索结束")

        # 使用结构化检索器进行实体搜索
        structured_data = self.structured_retriever(
            question,
            result_num_limit,
            exclude_relations=["MENTIONS"]
        )
        print("结构化实体搜索结束")

        # 融合两种检索结果，可以采用简单的合并，也可以根据需要进行加权或去重
        combined_results = list(set(structured_data + unstructured_data))

        # 输出检索结果
        final_data = "\n".join(combined_results)
        print("检索结果", final_data)

        return final_data