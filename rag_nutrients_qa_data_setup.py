import re
from typing import Dict, List

import chromadb
import pandas as pd
from tqdm import tqdm #progress bar library that can show progress


def parse_qa_pairs(
    file_path: str, sample_percentage: float = 0.05
) -> List[Dict[str, str]]:
    """
    Parse Q&A pairs from the questions_output.txt file.
    Each Q&A pair becomes a separate document.
    Only processes a sample percentage of the data for faster execution.
    """
    import random

    qa_pairs = []

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Split by double newlines to separate Q&A pairs
    pairs = content.split("\n\n")

    # Calculate how many pairs to sample
    total_pairs = len([p for p in pairs if p.strip()])
    sample_size = max(1, int(total_pairs * sample_percentage))

    print(f"Total Q&A pairs found: {total_pairs}")
    print(f"Sampling {sample_size} pairs ({sample_percentage*100:.1f}%)")

    # Filter out empty pairs first
    valid_pairs = [p for p in pairs if p.strip()]

    # Randomly sample pairs
    sampled_pairs = random.sample(valid_pairs, min(sample_size, len(valid_pairs)))

    # Process pairs with progress bar
    for i, pair in enumerate(tqdm(sampled_pairs, desc="Parsing Q&A pairs")):
        lines = pair.strip().split("\n")

        question = ""
        answer = ""

        for line in lines:
            if line.startswith("Question:"):
                question = line.replace("Question:", "").strip()
            elif line.startswith("Answer:"):
                answer = line.replace("Answer:", "").strip()

        if question and answer:
            qa_pairs.append({"question": question, "answer": answer, "id": f"qa_{i}"})

    return qa_pairs


def prepare_nutrition_qa_documents(
        file_path: str, sample_percentage: float = 0.05
) -> Dict:
    """
    Convert Q&A pairs into ChromaDB-ready documents.
    Each Q&A pair becomes a searchable document.
    """
    qa_pairs = parse_qa_pairs(file_path, sample_percentage)

    documents = []
    metadatas = []
    ids = []

    # Process Q&A pairs with progress bar
    for qa in tqdm(qa_pairs, desc="Preparing documents"):
        # Create rich document text for semantic search
        document_text = f"""
        Question: {qa['question']}
        Answer: {qa['answer']}

        This Q&A pair provides information about nutrition and health topics.
        """.strip()

        # Extract keywords from question for better searchability
        question_words = re.findall(r"\b\w+\b", qa["question"].lower())
        answer_words = re.findall(r"\b\w+\b", qa["answer"].lower())
        all_words = question_words + answer_words

        # Create metadata for filtering and exact lookups
        metadata = {
            "question": qa["question"],
            "answer": qa["answer"],
            "question_length": len(qa["question"]),
            "answer_length": len(qa["answer"]),
            "keywords": " ".join(set(all_words)),
            "has_question_mark": "?" in qa["question"],
            "topic": "nutrition_qa",
        }

        documents.append(document_text)
        metadatas.append(metadata)
        ids.append(qa["id"])

    return {"documents": documents, "metadatas": metadatas, "ids": ids}

def setup_nutrition_qa_chromadb(
    file_path: str,
    collection_name: str = "nutrition_qna",
    sample_percentage: float = 0.05,
):
    """
    Create and populate ChromaDB collection with nutrition Q&A data.
    """
    # Initialize ChromaDB
    client = chromadb.PersistentClient(path="chroma")

    # Create collection (delete if exists)
    try:
        client.delete_collection(collection_name)
    except:
        pass

    collection = client.create_collection(
        name=collection_name,
        metadata={
            "description": "Nutrition Q&A database with questions and answers about nutrition and health"
        },
    )

    # Prepare documents
    data = prepare_nutrition_qa_documents(file_path, sample_percentage)

    # Add to ChromaDB with progress bar
    print("Adding documents to ChromaDB...")
    collection.add(
        documents=data["documents"], metadatas=data["metadatas"], ids=data["ids"]
    )

    print(
        f"Added {len(data['documents'])} Q&A pairs to ChromaDB collection '{collection_name}'"
    )
    return collection

if __name__ == "__main__":

    # setup_nutrition_qa_chromadb("data/questions_output.txt")

    chroma_client = chromadb.PersistentClient(path="chroma")
    nutrition_qna = chroma_client.get_collection(name="nutrition_qna")
    print("qna count=", nutrition_qna.count())

    # Test query : Search for malnutrition symptoms
    print("=== Query: pregnancy ===")
    results = nutrition_qna.query(query_texts=["pregnancy"], n_results=3)
    documents = results["documents"][0]
    for i, doc in enumerate(documents):
        print(f"Result {i+1}:")
        print(f"Document: {documents[i]}")
        print("\n")

    print("\n" + "=" * 50 + "\n")