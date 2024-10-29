"""
Module to manage all GraphRAG functions. Mainly revolves around building up 
a retriever that can parse knowledge graphs and return related results
"""
from typing import List
from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain_community.vectorstores.neo4j_vector import remove_lucene_chars
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from src.graph.entities import Entities
import os


class GraphRAG():
    """
    这个类是用于从三元组中抽取知识图谱的关键
    Class to encapsulate all methods required to query a graph for retrieval augmented generation
    """

    def __init__(self,llm):
        self.graph = Neo4jGraph()
        self.llm = llm

    def create_entity_extract_chain(self):
        """
        从问题中抽取实体出来,允许我们从graph中抽取相关实体！使用用户所使用的语言
        Creates a chain which will extract entities from the question posed by the user. 
        This allows us to search the graph for nodes which correspond to entities more efficiently

        Returns:
            Runnable: Runnable chain which uses the LLM to extract entities from the users question
        """
        # P0 通过这里修改为特定的疗法与特定的标签，
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
        # 只有这里用到了Entities
        return entity_extract_chain

    def generate_full_text_query(self, input_query: str) -> str:
        """
        生成一个适用于全文搜索的查询字符串。全文搜索是一种在大量文本中查找特定信息的搜索技术，它能够理解文本中的语义和上下文，从而提供更准确的结果。
        输入处理：方法接收一个字符串input_query作为输入，这个字符串是从用户的问题中提取出来的实体名称。
        字符处理：使用remove_lucene_chars函数（假设这个函数已经定义）来移除Lucene查询中保留的特殊字符，然后使用split()方法将字符串分割成单词列表。
        生成查询字符串：遍历单词列表，对于每个单词，添加一个相似度阈值（这里设定为2，表示允许2个字符的变动），然后使用AND操作符将它们组合成一个查询字符串。最后一个单词后面不添加AND。
        返回结果：返回生成的查询字符串，并使用strip()方法去除首尾的空白字符。
        Generate a full-text search query for a given input string.

        This function constructs a query string suitable for a full-text search.
        It processes the input string by splitting it into words and appending a
        similarity threshold (~2 changed characters) to each word, then combines
        them using the AND operator. Useful for mapping entities from user questions
        to database values, and allows for some misspellings.

        Args:
            input_query (str): The extracted entity name pulled from the users question

        Returns:
            str: _description_
        """
        full_text_query = ""

        # split out words and remove any special characters reserved for cipher query
        words = [el for el in remove_lucene_chars(input_query).split() if el]
        for word in words[:-1]:
            full_text_query += f" {word}~2 AND"
        full_text_query += f" {words[-1]}~2"
        
        return full_text_query.strip()

    def structured_retriever(self, question: str, result_num_limit:int,exclude_relations:list) -> str:
        """
        事实上这个result_num_limit会导致
        使用2-gram做结构化搜索：这段Python代码定义了一个名为structured_retriever的方法，用于从用户的问题中提取实体，然后使用这些实体从图数据库中检索相关的上下文信息。具体来说，它通过调用Neo4j图数据库的查询语言Cypher来获取与查询相关的节点和边的信息。
        Creates a retriever which will use entities extracted from the users query to 
        request context from the Graph and return the neighboring nodes and edges related
        to that query. 
        
        Args:
            question (str): The question posed by the user for this graph RAG

        Returns:
            str: The fully formed Graph Query which will retrieve the 
                 context relevant to the users question
        """
        print(f"Structured Search query: {question}","*"*10)
        entity_extract_chain = self.create_entity_extract_chain()
        # 设置chain system prompt之类 用于检索对应内容
        result = ""
        entities = entity_extract_chain.invoke({"question": question})
        print("提炼的实体",entities)
        
        response_list=[]
        
        if entities is not None:
            for entity in entities.names:
                # 这里的实体提取就是指的是index 中的那个索引诶，需要对短标签的索引：同时对出边和入边进行处理，然后UNION
                if len(response_list)>= result_num_limit:
                    break    
                response = self.graph.query(
                    """
                    CALL db.index.fulltext.queryNodes('entity', $query, {limit: $limit})
                    YIELD node, score
                    CALL {
                        WITH node
                        MATCH (node)-[r]->(neighbor)
                        WHERE NOT type(r) IN $exclude_relations
                        RETURN node.id + ' - ' + type(r) + ' -> ' + neighbor.id AS output
                        UNION ALL
                        WITH node
                        MATCH (node)<-[r]-(neighbor)
                        WHERE NOT type(r) IN $exclude_relations
                        RETURN neighbor.id + ' - ' + type(r) + ' -> ' + node.id AS output
                    }
                    RETURN output LIMIT $limit
                    """,
                    {
                        "query": self.generate_full_text_query(entity),
                        "limit": result_num_limit,
                        "exclude_relations": exclude_relations
                    }
                )
                response_list.extend(response)
                print(len(response_list))


            """遍历提取到的实体。
            使用Cypher查询语言从图数据库中查询与实体相关的节点和边。
            CALL db.index.fulltext.queryNodes('entity', $query, {limit:5})：使用Neo4j的全文索引查询节点。
            MATCH (node)-[r]->(neighbor)和MATCH (node)<-[r]-(neighbor)：匹配节点之间的关系，包括正向和反向关系。
            RETURN node.id + ' - ' + type(r) + ' -> ' + neighbor.id：返回节点ID、关系类型和相邻节点的ID。
            result += "\n".join([el['output'] for el in response])：将查询结果拼接成一个字符串，每个结果占一行。
        """
        result += "\n".join([el['output'] for el in response_list[:result_num_limit]])
        print("检索结果",result,result.count("->"))
        return result
    def unstructured_retriever(self,question:str,embedding_model,exclude_relations:list,num_limit=2) ->dict:
        """Unstructured_retriever retrieve relevant text fragment based on vector similarity. 基于向量比对的非结构化检索，可以用于搜索文档等信息，这个玩意的主要作用是将文档进行向量化之后去检索vector_index 是一个Neo4jVector 只需要用很少的资源将其向量化 Uses the existing graph to create a vector index. This vector representation is based off the properties specified."""
        print(f"Unstructured Search query: {question}")
        vector_index = Neo4jVector.from_existing_graph(
            embedding_model,
            search_type="hybrid",
            node_label="Document",
            text_node_properties=["id","text"],
            embedding_node_property="embedding"
        )
         # 获取相似性搜索结果
        search_results = vector_index.similarity_search(question,num_limit)
        # 过滤掉指定关系类型的节点
        # 提取非结构化数据
        doc_list = [str(el.page_content) for el in search_results]
        doc_node_id_list=[]
        for document_page in doc_list:
            for line in document_page.split("\n"):
                print(line)
                if "id" in line:
                    id=line.split("id: ")[-1].strip()
                    print(id)
                    doc_node_id_list.append(id)
        return {"result":"#retrieve\n ".join(doc_list),"node_ids":doc_node_id_list}\
            
    def unstructured_retriever_type2(self,history:str,embedding_model,exclude_relations:list,num_limit=2) ->dict:
        """泽凯，你传入的question改一下，改成对话历史history，基于整个history检索对话，history是之前的对话历史的拼接，拼接方式是这样"""
        print(f"Unstructured Search query: {history}")
        vector_index = Neo4jVector.from_existing_graph(
            embedding_model,
            search_type="hybrid",
            index_name="dialog",
            node_label="dialog",
            keyword_index_name="dialog_vector",
            text_node_properties=["id", "content"],  # 添加 context 字段
            embedding_node_property="embedding"
        )
         # 获取相似性搜索结果
        search_results = vector_index.similarity_search(history,num_limit)
        # 过滤掉指定关系类型的节点
        # 提取非结构化数据
        print(search_results[0])
        doc_list = [str(el.page_content) for el in search_results]
        doc_node_id_list=[]
        for document_page in doc_list:
            for line in document_page.split("\n"):
                # print(line)
                if "id" in line:
                    id=line.split("id: ")[-1].strip()
                    print("检索到的nodeid"*10,id)
                    doc_node_id_list.append(id)
        return {"result":"#retrieve\n ".join(doc_list),"node_ids":doc_node_id_list}

    def mix_retriever(self, question: str,result_num_limit=5) -> str:
        """
        The graph RAG retriever which combines both structured and unstructured methods of retrieval 
        into a single retriever based off the users question. 
        
        Args:
            question (str): The question posed by the user for this graph RAG

        Returns:
            str: The retrieved data from the graph in both forms
        """
        
        doc_list,doc_node_id_list=self.unstructured_retriever(question,embedding_model=OpenAIEmbeddings(),exclude_relations=["MENTIONS"])
        unstructured_data=doc_list
        print("向量搜索结束")
        
        # structured_data = self.structured_retriever(question,result_num_limit,exclude_relations=["MENTIONS"])
        structured_data=""
        print("结构化实体搜索结束")
        
        final_data = f"""Structured data\n\n:
            {structured_data}
            Unstructured data\n\n:
            {"#Document ". join(unstructured_data)}
        """
        print("检索结果",final_data)
        print("检索节点id",doc_node_id_list)
        return final_data

    # def create_search_query(self, chat_history: List, question: str) -> str:
    #     """
    #     让LLM 去决定应该用什么query 去检索的prompt，最好需要给一个例子，生成检索query的
    #     Combines chat history along with the current question into a prompt that 
    #     can be executed by the LLM to answer the new question with history.

    #     Args:
    #         chat_history (List): List of messages captured during this conversation
    #         question (str): The question posed by the user for this graph RAG

    #     Returns:
    #         str: The formatted prompt that can be sent to the LLM with question & chat history
    #     """
    #     search_query = ChatPromptTemplate.from_messages([
    #         (
    #             "system",
    #             """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language.
    #             Chat History:
    #             {chat_history}
    #             Follow Up Input: {question}
    #             Standalone question:"""
    #         )
    #     ])
    #     formatted_query = search_query.format(
    #         chat_history=chat_history, question=question)
    #     return formatted_query
    
    
