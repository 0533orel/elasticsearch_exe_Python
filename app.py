import os, time
from elasticsearch import Elasticsearch, exceptions


ES_HOST  = os.getenv("ES_HOST",  "http://localhost:9200")
ES_INDEX = os.getenv("ES_INDEX", "demo")

es = Elasticsearch(ES_HOST)

# def wait_for_es(timeout=120, interval=2):
#     deadline = time.time() + timeout
#     last_err = None
#     while time.time() < timeout:
#         try:
#             es.info()
#             print("[OK] Elasticsearch is up")
#             return
#         except exceptions.ConnectionError as e:
#             last_err = e
#             print("[WAIT] Elasticsearch not ready yet...")
#             time.sleep(interval)
#     raise RuntimeError(f"Elasticsearch did not become ready: {last_err}")

def ensure_index():
    mapping = {
        "settings": {},
        "mappings": {
            "properties": {
                "title": {"type": "text"},
                "body": {"type": "text"},
                "tag": {"type": "keyword"}
            }
        }
    }
    if not es.indices.exists(index=ES_INDEX):
        es.indices.create(index=ES_INDEX, **mapping)
        print(f"[CREATE] index {ES_INDEX}")
    else:
        print(f"[EXISTS] index {ES_INDEX}")

def index_samples():
    docs = [
        {
            "title": "Hubble spots new galaxy",
            "body": "NASA telescope captured a distant object in deep space.",
            "tag": "sci.space"
        },
        {
            "title": "OpenGL tips for faster rendering",
            "body": "Graphics pipeline tuning and textures handling.",
            "tag": "comp.graphics"
        },
        {
            "title": "World Series analysis",
            "body": "The baseball season stats and playoff predictions.",
            "tag": "rec.sport.baseball"
        },
    ]
    for i, doc in enumerate(docs, start=1):
        res = es.index(index=ES_INDEX, id=i, document=doc)
        assert res["result"] in ["created", "updated"]
    es.indices.refresh(index=ES_INDEX)
    print(f"[INDEXED] {len(docs)} docs + refresh")

def run_search():
    query = {"match": {"body": "space"}}
    res = es.search(index=ES_INDEX, query=query, size=5)
    total = res["hits"]["total"]["value"]
    print(f"[SEARCH] total hits: {total}")
    for hit in res["hits"]["hits"]:
        src = hit["_source"]
        print(f"  - title: {src.get('title')}  | tag: {src.get('tag')}  | _score: {hit.get('_score')}")


if __name__ == "__main__":
    # wait_for_es()
    ensure_index()
    index_samples()
    run_search()













