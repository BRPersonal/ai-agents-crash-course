from typing import Dict, List

import chromadb
import pandas as pd


def prepare_nutrition_documents(csv_path: str) -> Dict:
    """
    Convert nutrition CSV into ChromaDB-ready documents.
    Each food item becomes a searchable document.
    """
    print("preparing nutrition documents")

    df = pd.read_csv(csv_path)

    documents = []
    metadatas = []
    ids = []

    for index, row in df.iterrows():
        # Create rich document text for semantic search
        row["Cals_per100grams"] = row["Cals_per100grams"].replace(" cal", "")
        row["KJ_per100grams"] = row["KJ_per100grams"].replace(" kJ", "")
        document_text = f"""
        Food: {row['FoodItem']}
        Category: {row['FoodCategory']}
        Nutritional Information:
        - Calories: {row['Cals_per100grams']} per 100g
        - Energy: {row['KJ_per100grams']} kJ per 100g
        - Serving size reference: {row['per100grams']}

        This is a {row['FoodCategory'].lower()} food item that provides {row['Cals_per100grams']} calories per 100 grams.
        """.strip()

        # Rich metadata for filtering and exact lookups
        metadata = {
            "food_item": row["FoodItem"].lower(),
            "food_category": row["FoodCategory"].lower(),
            "calories_per_100g": (
                float(row["Cals_per100grams"])
                if pd.notna(row["Cals_per100grams"])
                else 0
            ),
            "kj_per_100g": (
                float(row["KJ_per100grams"]) if pd.notna(row["KJ_per100grams"]) else 0
            ),
            "serving_info": row["per100grams"],
            # Add searchable keywords
            "keywords": f"{row['FoodItem'].lower()} {row['FoodCategory'].lower()}".replace(
                " ", "_"
            ),
        }

        documents.append(document_text)
        metadatas.append(metadata)
        ids.append(f"food_{index}")

    return {"documents": documents, "metadatas": metadatas, "ids": ids}


def setup_nutrition_chromadb(csv_path: str, collection_name: str = "nutrition_db"):
    """
    Create and populate ChromaDB collection with nutrition data.
    """
    print("Initialize chroma db...")

    # Initialize ChromaDB
    client = chromadb.PersistentClient(path="chroma")

    # Create collection (delete if exists)
    try:
        print(" deleting existing collection")
        client.delete_collection(collection_name)
    except BaseException:
        pass

    collection = client.create_collection(
        name=collection_name,
        metadata={
            "description": "Nutrition database with calorie and food information"
        }
    )

    # Prepare documents
    data = prepare_nutrition_documents(csv_path)

    # Add to ChromaDB
    collection.add(
        documents=data["documents"], metadatas=data["metadatas"], ids=data["ids"]
    )

    print(
        f"Added {len(data['documents'])} food items to ChromaDB collection '{collection_name}'"
    )
    return collection

if __name__ == "__main__":
    setup_nutrition_chromadb("data/calories.csv")

    chroma_client = chromadb.PersistentClient(path="chroma")
    nutrition_db = chroma_client.get_collection(name="nutrition_db")

    results = nutrition_db.query(query_texts=["banana"], n_results=3)
    for i, doc in enumerate(results["documents"][0]):
        print(results["metadatas"][0][i])
        print(doc)
        print("\n")