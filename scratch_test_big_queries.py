import time
from router.engine import route

# Create massive queries (~15,000 words each, roughly 100k characters)
massive_text_1 = "Here is a huge block of text to test the system. " * 2000
q1 = f"Please extract the hidden email address from this text block: {massive_text_1} my_hidden_email@example.com"

massive_text_2 = "This is a complex legal document about corporate mergers and liability clauses. " * 2000
q2 = f"Summarize the key findings and liability clauses in this document: {massive_text_2}"

queries = [
    ("Find Email (Tier 2/3)", q1),
    ("Legal Summary (Tier 1/2)", q2)
]

modes = ["cheap", "standard", "best"]

print("Starting big query routing test...\n")

for name, q in queries:
    print(f"--- Testing Query: {name} (Length: {len(q):,} characters) ---")
    for mode in modes:
        start = time.time()
        result = route(q, mode=mode)
        elapsed = (time.time() - start) * 1000
        
        # Determine if it hit the LLM or heuristic
        source = "Heuristic" if result.llm_used is False else "LLM"
        
        print(f"  [{mode.upper():<8}] Model: {result.model.id:<35} | Tier: {result.tier} | Source: {source:<9} | Time: {elapsed:.1f} ms")
    print()
