
import base64
import hashlib
from datetime import datetime
from functools import cached_property
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
)
from elasticsearch import Elasticsearch, exceptions, helpers
# from elasticsearch.helpers import BulkIndexError
from langchain_core.caches import RETURN_VAL_TYPE, BaseCache
from langchain_core.load import dumps, loads
# from langchain_core.stores import ByteStore

from langchain_elasticsearch.client import create_elasticsearch_client



def _manage_cache_index(es_client: Elasticsearch, index_name: str, mapping: Dict[str, Any]) -> bool:
    """Write or update an index or alias according to the default mapping"""
    if es_client.indices.exists_alias(name=index_name):
        es_client.indices.put_mapping(index=index_name, body=mapping["mappings"])
        return True

    elif not es_client.indices.exists(index=index_name):
        es_client.indices.create(index=index_name, body=mapping)
        return False

    return False



class ElasticsearchCache(BaseCache):
    """An Elasticsearch cache integration for LLMs."""
    def __init__(
        self,
        index_name: str,
        store_input: bool = True,
        store_input_params: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
        *,
        es_url: Optional[str] = None,
        es_cloud_id: Optional[str] = None,
        es_user: Optional[str] = None,
        es_api_key: Optional[str] = None,
        es_password: Optional[str] = None,
        es_params: Optional[Dict[str, Any]] = None,
    ):

        self._index_name = index_name
        self._store_input = store_input
        self._store_input_params = store_input_params
        self._metadata = metadata
        self._es_client = create_elasticsearch_client(
            url=es_url,
            cloud_id=es_cloud_id,
            api_key=es_api_key,
            username=es_user,
            password=es_password,
            params=es_params,
        )
        self._is_alias = _manage_cache_index(
            self._es_client,
            self._index_name,
            self.mapping,
        )

    @cached_property
    def mapping(self):
        """Get the default mapping for the index."""
        return {
            "mappings": {
                "properties": {
                    "llm_conf_name": {"type": "keyword", "index": True},
                    "llm_input_conf": {
                        "type": "nested",
                        "properties": {
                            "role": {
                                "type": "keyword",
                                "index": True
                            },
                            "content": {
                                "type": "text",
                                "index": True
                            }
                        }
                    },
                    "llm_output": {"type": "text", "index": True},
                    "metadata": {"type": "object"},
                    "timestamp": {"type": "date"},
                }
            }
        }

    def create_query(self, llm_conf_name: str, llm_input_conf: list):
        query = {
            "query":{
                "bool":{
                    "must":[
                        {
                            "nested":{
                                "path":"llm_input_conf",
                                "query": {
                                    "bool": {
                                        "must": [
                                            {"term": {"llm_input_conf.role": message["role"]}},
                                            {"match": {"llm_input_conf.content": message["content"]}}
                                        ]
                                    }
                                }
                            }
                            for message in llm_input_conf
                        }
                    ],
                    "filter": [
                        {"term": {"llm_conf_name": llm_conf_name}}
                    ]
                }
            },
            "sort": {"timestamp": {"order": "asc"}}
        }
        return query

    def build_document(self, llm_conf_name: str, llm_input_conf: list, llm_output: str, metadata: dict) -> dict:
        body = {
            "llm_conf_name": llm_conf_name,
            "llm_input_conf": llm_input_conf,
            "llm_output": llm_output,
            "metadata": metadata,
            "timestamp":  datetime.now().isoformat()
        }
        return body

    @staticmethod
    def _key(llm_conf_name: str, llm_input_conf: list) -> str:
        """Generate a key for the cache store."""
        return hashlib.md5((llm_conf_name + "\n" + "\n".join([message["role"] + ":" + message["content"] for message in llm_input_conf])).encode()).hexdigest()

    def lookup(self, llm_conf_name: str, llm_input_conf: list) -> list:
        cache_key = self._key(llm_conf_name, llm_input_conf)
        if self._is_alias:
            query = self.create_query(llm_conf_name, llm_input_conf)
            result = self._es_client.search(
                index=self._index_name,
                body=query,
                source_includes=["llm_output"],
            )
            if result["hits"]["total"]["value"] > 0:
                record = result["hits"]["hits"][0]
            else:
                return None
        else:
            try:
                record = self._es_client.get(
                    index=self._index_name, id=cache_key, source_includes=["llm_output"]
                )
            except exceptions.NotFoundError:
                return None
        return [item for item in record["_source"]["llm_output"]]

    def index(self, llm_conf_name: str, llm_input_conf: list, llm_output: str, metadata = {}) -> None:
        body = self.build_document(llm_conf_name, llm_input_conf, llm_output, metadata)
        self._es_client.index(
            index=self._index_name,
            id=self._key(llm_conf_name, llm_input_conf),
            body=body,
            require_alias=self._is_alias,
            refresh=True,
        )

    def clear(self, **kwargs: Any) -> None:
        self._es_client.delete_by_query(
            index=self._index_name,
            body={"query": {"match_all": {}}},
            refresh=True,
            wait_for_completion=True,
        )


