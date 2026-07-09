import chromadb

client = chromadb.Client()
col = client.get_or_create_collection('smoke_test_quick')
print('collection ready')
col.upsert(ids=['a1'], documents=['hello'], embeddings=[[0.1]*384], metadatas=[{'x':1}])
print('upsert done')
res = col.query(query_embeddings=[[0.1]*384], n_results=1, include=['documents','metadatas','distances'])
print('query done, ids:', res['ids'])
