from core.config import settings

from elasticsearch import AsyncElasticsearch
from itertools import combinations
from typing import List, Tuple


def build_tag_pairs(tags: List[str]) -> List[Tuple[str, str]]:
    return [tuple(sorted(pair)) for pair in combinations(tags, 2)]


async def update_hashtag_relations(
    es: AsyncElasticsearch, 
    pairs: list[tuple[str, str]], 
    delta: int,
    year: int
):
    for src, dst in pairs:
        doc_id = f"{src}__{dst}"

        create_new_or_increase = {
            "script": {
                "source": """
                    ctx._source.paper_cnt_total += params.delta;
                    if (ctx._source.paper_cnt_by_year.containsKey(params.year)) {
                        ctx._source.paper_cnt_by_year[params.year] += params.count;
                    } else {
                        ctx._source.paper_cnt_by_year[params.year] = params.count;
                    }
                """,
                "params": {"delta": delta, "year": str(year)},
                "lang": "painless"
            },
            "upsert": {
                "src": src,
                "dst": dst,
                "paper_cnt_total": delta,
                "paper_cnt_by_year": {str(year): delta}
            }
        }
        
        decrease_or_delete = {
            "script": {
                "source": """
                    ctx._source.paper_cnt_total += params.delta;
                    if (ctx._source.paper_cnt_by_year.containsKey(params.year)) {
                        ctx._source.paper_cnt_by_year[params.year] += params.delta;
                        if (ctx._source.paper_cnt_by_year[params.year] <= 0) {
                            ctx._source.paper_cnt_by_year.remove(params.year);
                        }
                    }
                    if (ctx._source.paper_cnt_total <= 0) {
                        ctx.op = 'delete';
                    }
                """,
                "params": {"delta": delta, "year": str(year)},
                "lang": "painless"
            }
        }
        
        es_body = create_new_or_increase if delta > 0 else decrease_or_delete
        
        try:
            await es.update(
                index=settings.es_hashtag_relations_index,
                id=doc_id,
                body=es_body
            )
        except Exception as e:
            print(f"Failed to update relation {src}-{dst}: {e}")
            
            
        