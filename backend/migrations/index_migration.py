from elasticsearch import AsyncElasticsearch
from typing import Dict
from datetime import datetime


async def is_new_mappings(es: AsyncElasticsearch, alias: str, schema: Dict[str, any]): 
    mappings_by_index = await es.indices.get_mapping(index=alias)
    index: str = list(mappings_by_index.keys())[0]
    old_mappings: Dict[str, any] = mappings_by_index[index]["mappings"]
    return schema["mappings"] != old_mappings, index


async def init_index(es: AsyncElasticsearch, version: str, alias: str, schema: Dict[str, any]):
    if await es.indices.exists(index=alias):
        return False
    
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    index = f"{alias}_v{version}.{ts}"
    
    await es.indices.create(index=index, body=schema)
    await es.indices.put_alias(index=index, name=alias)

    return True
    

async def migrate_index(
    es: AsyncElasticsearch,
    version: str,
    alias: str, 
    schema: Dict[str, any],
    delete_old: bool = False
):
    is_new, old_index = await is_new_mappings(es, alias, schema)
    
    if not is_new:
        return False

    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S") 
    new_index = f"{alias}_v{version}.{ts}" 

    # Create New Index
    await es.indices.create(index=new_index, body=schema)
    
    # Reindex From Old to New
    await es.reindex(
        body={
            "source": {"index": old_index},
            "dest": {"index": new_index} 
        }, 
        wait_for_completion=True
    )
    await es.indices.refresh(index=new_index)

    # Switch Alias
    await es.indices.update_aliases(body={
        "actions": [
            {"remove": {"index": old_index, "alias": alias}},
            {"add": {"index": new_index, "alias": alias}}
        ]
    })

    # Delete Old Index (after verification)
    if delete_old:
        await es.indices.delete(index=old_index)