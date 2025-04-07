from pinecone import Pinecone, ServerlessSpec
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
        self.index, created = self.getIndex()

        # If the index was just created, populate it with data
        if created:
            self.addData()


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


    # Add data to the index
    def addData(self):
        print("Adding data to the index...")
        
        # Define your data
        # data = [
        #     {"id": "vec1", "text": "Apple is a popular fruit known for its sweetness and crisp texture."},
        #     {"id": "vec2", "text": "The tech company Apple is known for its innovative products like the iPhone."},
        #     {"id": "vec3", "text": "Many people enjoy eating apples as a healthy snack."},
        #     {"id": "vec4", "text": "Apple Inc. has revolutionized the tech industry with its sleek designs and user-friendly interfaces."},
        #     {"id": "vec5", "text": "An apple a day keeps the doctor away, as the saying goes."},
        # ]
        
        
        paper_files = [f for f in os.listdir("papers/") if f.endswith('.txt')]
        # Prepare data from all the text files
        data = []
        for paper_file in paper_files:
            file_path = os.path.join("papers/", paper_file)
            
            # Read the content of each text file
            with open(file_path, 'r', encoding='utf-8') as file:
                paper_content = file.read()

            # Use the file name (without extension) as the ID
            entry_id = os.path.splitext(paper_file)[0]

            # Add the entry to the data list
            data.append({
                "id": entry_id,
                "text": paper_content,
                "hierarchy": random.randint(1, 2)
            })

        # Embed data
        embeddings = self.pc.inference.embed(
            model="llama-text-embed-v2",
            inputs=[d['text'] for d in data],
            parameters={"input_type": "passage"}
        )

        # Format vectors
        vectors = []
        for d, e in zip(data, embeddings):
            vectors.append({
                "id": d['id'],
                "values": e['values'],
                "metadata": {
                    'text': d['text'],
                    'hierarchy': d['hierarchy']
                }
            })

        # Upsert vectors
        self.index.upsert(vectors=vectors, namespace=self.namespace)
        print("Data upserted successfully.")


    # Query the index
    def query(self, queryText, topK=3, threshold=0.4, maxHierarchyLevel=3):
        
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
            responseBuilder += f"Paper: {match['id']}\n"
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
    # To query:
    pinecone_handler.query("Quantas horas devo dormir por dia?")
