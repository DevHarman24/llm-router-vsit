import os
import json
import time
from typing import Dict, Any, List

# Load .env so GROQ_API_KEY is available in this terminal session
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

from router.engine import route
from router.models import get_catalog

# Verify API key loaded
groq_key = os.getenv("GROQ_API_KEY", "")
if groq_key:
    print(f"[Setup] GROQ_API_KEY loaded ({groq_key[:8]}...). LLM classifier will run.")
else:
    print("[Setup] WARNING: No GROQ_API_KEY found. Mock classifier will be used.")

# Generate 100 diverse test queries
QUERIES = [
    # ── Simple / Low Complexity (20) ──
    {"query": "Hello there!", "category": "Simple"},
    {"query": "What is the capital of France?", "category": "Simple"},
    {"query": "Define entropy.", "category": "Simple"},
    {"query": "Is the sky blue? Yes or no.", "category": "Simple"},
    {"query": "Who is the president of the US?", "category": "Simple"},
    {"query": "Tell me a joke.", "category": "Simple"},
    {"query": "What's the weather like?", "category": "Simple"},
    {"query": "Translate 'apple' to Spanish.", "category": "Simple"},
    {"query": "Format this list of names: John, Jane, Joe.", "category": "Simple"},
    {"query": "Thank you very much.", "category": "Simple"},
    {"query": "What is 2+2?", "category": "Simple"},
    {"query": "Synonym for happy.", "category": "Simple"},
    {"query": "Where is the Eiffel Tower?", "category": "Simple"},
    {"query": "Find the word 'test' in this short sentence.", "category": "Simple"},
    {"query": "Extract the date from this string: 2024-05-12.", "category": "Simple"},
    {"query": "True or false: Earth is flat.", "category": "Simple"},
    {"query": "What time is it in Tokyo?", "category": "Simple"},
    {"query": "Hey!", "category": "Simple"},
    {"query": "How many days in a leap year?", "category": "Simple"},
    {"query": "What is water?", "category": "Simple"},

    # ── Medium Complexity (20) ──
    {"query": "Write a short blog post about the benefits of AI in education.", "category": "Medium"},
    {"query": "Summarize this long article about global warming.", "category": "Medium"},
    {"query": "Plan a 3-day itinerary for a trip to Rome.", "category": "Medium"},
    {"query": "Explain how photosynthesis works in simple terms.", "category": "Medium"},
    {"query": "Compare apples and oranges.", "category": "Medium"},
    {"query": "Write an email to my boss asking for a raise.", "category": "Medium"},
    {"query": "Review this feedback and give me your thoughts.", "category": "Medium"},
    {"query": "Translate this whole paragraph into Japanese.", "category": "Medium"},
    {"query": "Describe the plot of the Matrix.", "category": "Medium"},
    {"query": "Brainstorm 5 names for my new startup.", "category": "Medium"},
    {"query": "Outline the history of the Roman Empire.", "category": "Medium"},
    {"query": "Write a cover letter for a software engineer position.", "category": "Medium"},
    {"query": "Explain the rules of basketball.", "category": "Medium"},
    {"query": "Compare electric cars with gas cars.", "category": "Medium"},
    {"query": "Write a short essay on the impact of social media.", "category": "Medium"},
    {"query": "Describe how a car engine works.", "category": "Medium"},
    {"query": "Summarize the book '1984'.", "category": "Medium"},
    {"query": "Plan a weekly dinner menu.", "category": "Medium"},
    {"query": "Write a creative story about a robot.", "category": "Medium"},
    {"query": "Explain the difference between a stock and a bond.", "category": "Medium"},

    # ── Complex / Reasoning (20) ──
    {"query": "Design a scalable microservices architecture for an e-commerce platform.", "category": "Complex"},
    {"query": "Prove the Pythagorean theorem using geometry.", "category": "Complex"},
    {"query": "Analyze the legal implications of this contract clause.", "category": "Complex"},
    {"query": "What is the optimal business strategy for a new SaaS entering a crowded market?", "category": "Complex"},
    {"query": "Explain the intricacies of the Black-Scholes model for options pricing.", "category": "Complex"},
    {"query": "Derive the formula for the volume of a sphere.", "category": "Complex"},
    {"query": "Design a deep learning model for natural language processing from scratch.", "category": "Complex"},
    {"query": "Conduct a security audit on a standard OAuth2 implementation.", "category": "Complex"},
    {"query": "Discuss the ethical implications of artificial general intelligence.", "category": "Complex"},
    {"query": "Provide a comprehensive competitive analysis of the current cloud computing market.", "category": "Complex"},
    {"query": "How would you optimize performance tuning for a high-frequency trading database?", "category": "Complex"},
    {"query": "What is the difference between a philosophical zombie and a conscious being?", "category": "Complex"},
    {"query": "Create a decision framework for whether a company should go public.", "category": "Complex"},
    {"query": "Solve this complex differential equation step by step.", "category": "Complex"},
    {"query": "Analyze the trade-offs between eventual consistency and strong consistency in distributed systems.", "category": "Complex"},
    {"query": "Explain the architecture of a transformer model in deep learning.", "category": "Complex"},
    {"query": "Design a Kubernetes orchestration strategy for 1000 nodes.", "category": "Complex"},
    {"query": "Review the vulnerability footprint of a monolithic vs microservices application.", "category": "Complex"},
    {"query": "Evaluate the pros and cons of different economic theories on inflation.", "category": "Complex"},
    {"query": "Explain how zero-knowledge proofs work in cryptography.", "category": "Complex"},

    # ── Coding (20) ──
    {"query": "Write a Python script to scrape data from a website.", "category": "Coding"},
    {"query": "Debug this React component that is not rendering properly.", "category": "Coding"},
    {"query": "Implement a binary search tree in C++.", "category": "Coding"},
    {"query": "Create a REST API using Node.js and Express.", "category": "Coding"},
    {"query": "Refactor this legacy Java code to use modern streams.", "category": "Coding"},
    {"query": "Write a SQL query to find the second highest salary.", "category": "Coding"},
    {"query": "How do I fix a segmentation fault in my C program?", "category": "Coding"},
    {"query": "Build a simple to-do app in Next.js.", "category": "Coding"},
    {"query": "Create a CSS animation for a bouncing ball.", "category": "Coding"},
    {"query": "Write a shell script to backup a directory.", "category": "Coding"},
    {"query": "Implement Dijkstra's algorithm in Python.", "category": "Coding"},
    {"query": "Explain why this JavaScript promise is not resolving.", "category": "Coding"},
    {"query": "Write a regex to validate an email address.", "category": "Coding"},
    {"query": "How do I connect a Flask app to a PostgreSQL database?", "category": "Coding"},
    {"query": "Build a responsive grid layout using Tailwind CSS.", "category": "Coding"},
    {"query": "Implement authentication using JWT in Go.", "category": "Coding"},
    {"query": "Write unit tests for a Python function using pytest.", "category": "Coding"},
    {"query": "Create a Dockerfile for a Node.js application.", "category": "Coding"},
    {"query": "Explain how React's virtual DOM works.", "category": "Coding"},
    {"query": "Write a script to automate Git commits.", "category": "Coding"},

    # ── With Image (10) ──
    {"query": "What is the primary color in this screenshot?", "category": "Image", "has_image": True, "file_path": "Screenshot 2023-11-08 123622.png"},
    {"query": "Convert this UI design into React code.", "category": "Image", "has_image": True, "file_path": "Screenshot 2024-01-01 195615.png"},
    {"query": "Analyze the trend in this chart.", "category": "Image", "has_image": True, "file_path": "Screenshot 2024-07-25 175140.png"},
    {"query": "Describe the architecture shown in this diagram.", "category": "Image", "has_image": True, "file_path": "Screenshot 2024-07-26 193238.png"},
    {"query": "Extract the text from this handwritten note.", "category": "Image", "has_image": True, "file_path": "Screenshot 2025-08-24 214806.png"},
    {"query": "Is there a bug in the code shown in this image?", "category": "Image", "has_image": True, "file_path": "Screenshot 2026-06-19 140417.png"},
    {"query": "What objects do you see in this photo?", "category": "Image", "has_image": True, "file_path": "Screenshot 2023-11-08 123622.png"},
    {"query": "Summarize the data presented in this graph.", "category": "Image", "has_image": True, "file_path": "Screenshot 2024-01-01 195615.png"},
    {"query": "Translate the text in this image to French.", "category": "Image", "has_image": True, "file_path": "Screenshot 2024-07-25 175140.png"},
    {"query": "Write CSS to recreate the layout in this image.", "category": "Image", "has_image": True, "file_path": "Screenshot 2024-07-26 193238.png"},

    # ── With File (10) ──
    {"query": "Summarize this PDF report.", "category": "File", "has_file": True, "file_path": "SkillBits (1).pdf"},
    {"query": "What are the key findings in this document?", "category": "File", "has_file": True, "file_path": "SkillBits (1).pdf"},
    {"query": "Review this Python code for security vulnerabilities.", "category": "File", "has_file": True, "file_path": "router/models.py"},
    {"query": "Refactor this JavaScript file to use ES6 syntax.", "category": "File", "has_file": True, "file_path": "frontend/app.js"},
    {"query": "Extract all the dependencies from this requirements file.", "category": "File", "has_file": True, "file_path": "requirements.txt"},
    {"query": "Find the section about 'API' in this document.", "category": "File", "has_file": True, "file_path": "SkillBits (1).pdf"},
    {"query": "Explain what this script does.", "category": "File", "has_file": True, "file_path": "router/models.py"},
    {"query": "Write unit tests for the functions in this file.", "category": "File", "has_file": True, "file_path": "frontend/app.js"},
    {"query": "Update this requirements file to the latest versions.", "category": "File", "has_file": True, "file_path": "requirements.txt"},
    {"query": "Translate this document to Spanish.", "category": "File", "has_file": True, "file_path": "SkillBits (1).pdf"},
    
    # ── Edge Cases (Big Paragraph Simple Task) ──
    {"query": "Find the exact word 'router' from this paragraph. " + ("Here is a very long paragraph. " * 50) + " router " + ("Here is some more text. " * 50), "category": "Simple"},
    {"query": "Extract the email from the following massive block of text: " + ("lorem ipsum " * 200) + "test@example.com " + ("dolor sit amet " * 200), "category": "Simple"}
]

def run_evaluation():
    print("Starting LLM Router Evaluation (100+ queries)...")
    results = []
    
    # Track stats
    tier_counts = {1: 0, 2: 0, 3: 0}
    avg_times = {"total": 0, "heuristic": 0, "llm": 0}
    
    for i, q in enumerate(QUERIES):
        print(f"Processing query {i+1}/{len(QUERIES)} [{q['category']}]...")
        
        has_image = q.get("has_image", False)
        has_file = q.get("has_file", False)
        file_path = q.get("file_path", "")
        
        file_size_kb = 0
        if file_path and os.path.exists(file_path):
            file_size_kb = os.path.getsize(file_path) / 1024
        
        decision = route(
            query=q["query"],
            has_image=has_image,
            has_file=has_file,
            file_size_kb=file_size_kb, mode='best',
            groq_api_key=groq_key or None
        )
        
        # Analyze if decision makes sense
        is_correct = True
        notes = []
        if q["category"] == "Simple" and decision.tier == 1:
            is_correct = False
            notes.append("Simple query routed to Tier 1")
        if q["category"] == "Complex" and decision.tier == 3:
            is_correct = False
            notes.append("Complex query routed to Tier 3")
        if q["category"] == "Coding" and not decision.model.supports_coding:
            is_correct = False
            notes.append("Coding query assigned to model without coding support")
        if has_image and not decision.model.supports_vision:
            is_correct = False
            notes.append("Image query assigned to model without vision support")
            
        result = {
            "id": i + 1,
            "category": q["category"],
            "query_preview": q["query"][:80] + "..." if len(q["query"]) > 80 else q["query"],
            "model": decision.model.id,
            "tier": decision.tier,
            "total_time_ms": decision.total_time_ms,
            "heuristic_time_ms": decision.heuristic_time_ms,
            "llm_time_ms": decision.llm_time_ms,
            "llm_used": decision.llm_used,
            "classifier_source": decision.classifier.source if decision.classifier else "heuristic",
            "needs_vision": decision.needs_vision,
            "needs_thinking": decision.needs_thinking,
            "needs_coding": decision.needs_coding,
            "context_window": decision.model.context_window,
            "price": decision.model.price_per_million_tokens,
            "reasoning": decision.reasoning,
            "is_correct": is_correct,
            "notes": notes
        }
        results.append(result)
        
        # Stats
        tier_counts[decision.tier] = tier_counts.get(decision.tier, 0) + 1
        avg_times["total"] += decision.total_time_ms
        avg_times["heuristic"] += decision.heuristic_time_ms
        avg_times["llm"] += decision.llm_time_ms

    # Finalize stats
    num_queries = len(QUERIES)
    avg_times = {k: v / num_queries for k, v in avg_times.items()}
    llm_used_count = sum(1 for r in results if r.get("llm_used", False))
    heuristic_only_count = num_queries - llm_used_count
    real_llm_count = sum(1 for r in results if r.get("classifier_source") == "llm")
    mock_count = sum(1 for r in results if r.get("classifier_source") == "mock")
    
    # Save JSON
    with open("evaluation_best_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
        
    # Generate Markdown Report
    with open("evaluation_best.md", "w", encoding="utf-8") as f:
        f.write("# LLM Router Best Mode Evaluation Report\n\n")
        
        f.write("## Overview\n")
        f.write(f"- Total Queries: {num_queries}\n")
        f.write(f"- Tier 1 (High Complexity): {tier_counts.get(1, 0)}\n")
        f.write(f"- Tier 2 (Medium Complexity): {tier_counts.get(2, 0)}\n")
        f.write(f"- Tier 3 (Low Complexity): {tier_counts.get(3, 0)}\n\n")
        
        f.write("## Classifier Usage\n")
        f.write(f"- Heuristic only (high confidence, LLM skipped): {heuristic_only_count}\n")
        f.write(f"- Real Groq LLM classifier used: {real_llm_count}\n")
        f.write(f"- Mock classifier used (fallback): {mock_count}\n\n")
        
        f.write("## Performance\n")
        f.write(f"- Average Total Time: {avg_times['total']:.2f} ms\n")
        f.write(f"- Average Heuristic Time: {avg_times['heuristic']:.2f} ms\n")
        f.write(f"- Average LLM Classifier Time: {avg_times['llm']:.2f} ms\n\n")
        
        f.write("## Detailed Results\n")
        f.write("| ID | Category | Query | Model | Tier | LLM Used | Source | Vision | Think | Code | Time(ms) | Pass |\n")
        f.write("|---|---|---|---|---|---|---|---|---|---|---|---| \n")
        for r in results:
            pass_mark = "PASS" if r["is_correct"] else "FAIL"
            llm_flag = "Yes" if r.get("llm_used") else "No"
            source = r.get("classifier_source", "heuristic")
            f.write(f"| {r['id']} | {r['category']} | {r['query_preview'][:50]} | {r['model'].split('/')[-1]} | {r['tier']} | {llm_flag} | {source} | {r['needs_vision']} | {r['needs_thinking']} | {r['needs_coding']} | {r['total_time_ms']:.1f} | {pass_mark} |\n")
            
        f.write("\n## Failure Analysis\n")
        failures = [r for r in results if not r["is_correct"]]
        if not failures:
            f.write("All queries routed correctly!\n")
        else:
            f.write(f"Total failures: {len(failures)} / {num_queries}\n\n")
            for f_res in failures:
                f.write(f"- **Query {f_res['id']}** ({f_res['category']}): {f_res['query_preview'][:80]}\n")
                f.write(f"  - Model: {f_res['model']} (Tier {f_res['tier']})\n")
                f.write(f"  - Classifier: {f_res.get('classifier_source', 'heuristic')} | LLM Used: {f_res.get('llm_used', False)}\n")
                f.write(f"  - Notes: {', '.join(f_res['notes'])}\n")
                f.write(f"  - Reasoning: {f_res['reasoning']}\n\n")

    print("\nEvaluation complete! Results saved to evaluation_best.md and evaluation_best_results.json.")

if __name__ == "__main__":
    run_evaluation()
