import pytest
from migrations.index_migration import is_new_mappings, init_index, migrate_index


@pytest.mark.asyncio
async def test_is_new_mappings(es_client):
    es = es_client

    old_schema = {
        "mappings": {
            "properties": {
                "title": {"type": "text"}
            }
        },
    }
    new_schema = {
        "mappings": {
            "properties": {
                "title2": {"type": "text"}
            }
        } 
    } 
    alias = "fake_index"
    index = "fake_index_v1"

    await es.indices.create(index=index, body=old_schema)
    await es.indices.put_alias(index=index, name=alias)
    
    result, old_index = await is_new_mappings(es, alias, old_schema)
    assert result == False
    assert old_index == index

    result, index = await is_new_mappings(es, alias, new_schema)
    assert result == True
    assert old_index == index


@pytest.mark.asyncio
async def test_init_index(es_client):
    es = es_client

    schema = {
        "mappings": {
            "properties": {
                "title": {"type": "text"}
            }
        }
    }
    alias = "fake_index"
    version = "1"
    
    result = await init_index(es, version=version, alias=alias, schema=schema)
    assert result == True

    mappings_by_index = await es.indices.get_mapping(index=alias)
    assert len(mappings_by_index) == 1
    index = list(mappings_by_index.keys())[0]
    assert index.startswith(f"{alias}_v{version}")

    new_version = "2"
    result = await init_index(es, version=new_version, alias=alias, schema=schema)
    assert result == False

    mappings_by_index = await es.indices.get_mapping(index=alias)
    assert len(mappings_by_index) == 1
    index = list(mappings_by_index.keys())[0]
    assert index.startswith(f"{alias}_v{version}") 
    

@pytest.mark.asyncio
async def test_migrate_index(es_client):
    es = es_client
    
    # Sample input
    alias = "fake_index"
    old_index = "fake_index_v1.00000000"
    new_version = "2"
    old_schema = {
        "mappings": {
            "properties": {
                "title": {"type": "text"}
            }
        }
    }
    new_schema = {
        "mappings": {
            "properties": {
                "title": {"type": "text"},
                "new_prop": {"type": "keyword"}
            }
        } 
    }

    # Create old index + mock document
    await es.indices.create(index=old_index, body=old_schema)
    await es.index(index=old_index, document={"title": "Migrating ES index works!"})
    await es.indices.refresh(index=old_index)

    # Create alias pointing to old_index
    await es.indices.put_alias(index=old_index, name=alias)

    # Call migration
    result = await migrate_index(es, version=new_version, alias=alias, schema=old_schema, delete_old=True)

    # Verify no migration
    mappings_by_index = await es.indices.get_mapping(index=alias)
    assert result == False
    index = list(mappings_by_index.keys())[0]
    assert index == old_index

    # Call migration
    result = await migrate_index(es, version=new_version, alias=alias, schema=new_schema, delete_old=True) 

    # Verify alias now points to new_index
    mappings_by_index = await es.indices.get_mapping(index=alias)
    assert len(mappings_by_index) == 1
    index = list(mappings_by_index.keys())[0]
    assert index.startswith(f"{alias}_v{new_version}") 
    props = mappings_by_index[index]["mappings"]["properties"]
    assert "new_prop" in props
    assert props["new_prop"]["type"] == "keyword"

    # Verify document was copied
    docs = await es.search(index=index, query={"match_all": {}}, size=10)
    assert docs["hits"]["total"]["value"] == 1
    assert docs["hits"]["hits"][0]["_source"]["title"] == "Migrating ES index works!"

    

    