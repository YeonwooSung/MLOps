# Build ChatGPT with Priavet data on MongoDB

## Workflow

1. Connect private knowledge sources using LlamaIndex connectors

2. Load in the Documents. A Document represents a lightweight container around the data source.

3. Parse the Documents objects into Node objects. Nodes represent “chunks” of source Documents (ex. a text chunk). These node objects can be persisted to a MongoDB collection or kept in memory.

4. Construct Index from Nodes. There are various kinds of indexes in LlamaIndex like “List Index” (this stores nodes as Sequential chain), “Vector Store Index” (this stores each node and a corresponding embedding in a vector store). Depending on the type of Index, these indexes can be persisted into a MongoDB collection or a Vector Database.

5. Finally query the index. This is where the the query is parsed, relevant Nodes retrieved through the use of indexes, and provided as an input to a “Large Language Model” (LLM). Different types of queries can use different indexes.
