import json
from textwrap import wrap
from pinecone import Pinecone, ServerlessSpec, PineconeApiException
import os
from dotenv import load_dotenv
import random

class PineconeHandler:
    def __init__(self):
        
        load_dotenv()
        self.apiKey = os.getenv("PINECONE_API_KEY")
        if not self.apiKey:
            raise ValueError("PINECONE_API_KEY environment variable not set.")
        
        # Pinecone config
        self.pc = Pinecone(api_key=self.apiKey)
        self.indexName = "project"
        self.dimension = 1024
        self.namespace = "ns1"

        # Ensure index exists or create it
        self.index, hasJustBeenCreated = self.getIndex()

        # If the index was just created, populate it with data
        if hasJustBeenCreated:
            self.insertDataInBatches()


    # Get or create the index
    def getIndex(self):
        existingIndexes = [index["name"] for index in self.pc.list_indexes()]
        created = False

        if self.indexName not in existingIndexes:
            print("Index not found. Creating it...")
            self.pc.create_index(
                name=self.indexName,
                dimension=self.dimension,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
            created = True
        else:
            print("Index already exists.")

        return self.pc.Index(self.indexName), created

       
    def dataEmbedding(self, data):
        print("Adding data to the index...")
        data = [d for d in data]

        # Create embeddings for filtered data
        textsToEmbed = [d['chunk_text'] for d in data]
        embeddings = self.pc.inference.embed(
            model="llama-text-embed-v2",
            inputs=textsToEmbed,
            parameters={"input_type": "passage"}
        )

        # Build Pinecone vector format
        vectors = []
        for d, e in zip(data, embeddings):
            vectors.append({
                "id": d['chunk_id'],
                "values": e['values'],
                "metadata": {
                    'chunk_id': d['chunk_id'],
                    'text': d['chunk_text'],
                    'title': d['title'],
                    'link': d['link'],
                    'year': d['year'],
                    'topic': d['topic'],
                    'hierarchy': d['hierarchical_level']
                }
            })

        return vectors


    def insertDataInBatches(self):
        CHUNK_SIZE = 50
        # Load the pre-chunked JSON file (already split by text elsewhere)
        with open("../Data/ChunkedData/ChunkedData.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        # Helper: Chunk a list into smaller batches of 10
        def batch(iterable, size):
            for i in range(0, len(iterable), size):
                yield iterable[i:i + size]

        # Process data in batches
        for i, batch_data in enumerate(batch(data, CHUNK_SIZE)):  # Process in batches of 10
            print(f"Processing batch {i+1} / {len(data) // CHUNK_SIZE + 1}...")

            # Call addData to process the batch
            vectors = self.dataEmbedding(batch_data)

            if not vectors:
                print(f"Skipping batch {i+1} due to error in adding data.")
                continue  # Skip this batch if addData returns no vectors

            # Upsert vectors for the batch
            try:
                self.index.upsert(vectors=vectors, namespace=self.namespace)
                print(f"Successfully upserted batch {i+1}")
            except Exception as e:
                print(f"Error upserting batch {i+1}: {e}")
                continue  # Skip this batch and continue with the next one

        print("Data upserted successfully.")


    # Query the index
    def query(self, queryText, topK=3, threshold=0.6, maxHierarchyLevel=3):
        
        # Embed the query once
        query_embedding = self.pc.inference.embed(
            model="llama-text-embed-v2",
            inputs=[queryText],
            parameters={"input_type": "query"}
        )[0]["values"]

        finalResults = []

        for currentHierachyLevel in range(1, maxHierarchyLevel + 1):
            print(f"Searching hierarchy level {currentHierachyLevel}...")

            results = self.index.query(
                namespace=self.namespace,
                vector=query_embedding,
                top_k=topK,
                include_values=False,
                include_metadata=True,
                filter={"hierarchy": currentHierachyLevel}
            )

            matches = results.get("matches", [])
            if not matches:
                print(f"No results at level {currentHierachyLevel}, stopping.")
                break


            # Evaluate each match
            matches.sort(key=lambda x: x["score"], reverse=True)
            for match in matches:
                
                # If we already have topK results above threshold, ignore this
                if len(finalResults) < topK:
                    finalResults.append(match)
                    
                else:
                    # If we already have topK results, check lowest score of current finalResults list
                    lowest = min(finalResults, key=lambda x: x["score"])

                    # Only replace the lowest scoring match if the new match is better and out of threshold scope
                    if match["score"] > lowest["score"] and lowest["score"] < threshold:
                        finalResults.remove(lowest)
                        finalResults.append(match)

            # Stop if all finalResults are above threshold and we have enough
            if len(finalResults) == topK and all(r["score"] >= threshold for r in finalResults):
                print("All required results found. Stopping.")
                break
            else:
                print("Not good enough results yet, checking deeper hierarchy...")

        # Sort results by score descending
        finalResults.sort(key=lambda x: x["score"], reverse=True)

        # Build response
        responseBuilder = ""
        for match in finalResults:
            responseBuilder += f"Paper: {match['metadata'].get('title')}\n"
            responseBuilder += f"Hierarchy: {match['metadata'].get('hierarchy')}\n"
            responseBuilder += f"Score: {match['score']:.4f}\n"
            responseBuilder += f"Text: {match['metadata'].get('text')}\n\n"

        # Print final results
        print("\nFinal Top Matches:")
        for match in finalResults:
            print(f"Score: {match['score']:.4f}")
            print(f"Hierarchy: {match['metadata']['hierarchy']}")
            print(f"Text: {match['metadata']['text']}")
            print("-" * 50)

        return responseBuilder
        


# Debugging only
if __name__ == "__main__":
    pinecone_handler = PineconeHandler()
    pinecone_handler.insertDataInBatches()
    # To query:
    # pinecone_handler.query("Quantas horas devo dormir por dia?")
