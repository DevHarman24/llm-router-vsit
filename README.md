# LLM Router 🧠⚡

An intelligent, context-aware router that acts as middleware between your application and the AI model ecosystem. 

Instead of blindly sending every request to expensive frontier models (like GPT-4o or Claude Opus), the LLM Router analyzes the complexity, required context window, and capability needs of each query in **under 2 milliseconds**. It then routes the request to the most cost-effective and capable model via OpenRouter, saving up to **97%** on API costs without sacrificing quality.

## Features
- **Dual-Layer Classification:** 
  - *Layer 1 (Heuristics):* Instantaneous keyword & signal mapping for obvious simple/complex queries (<1ms).
  - *Layer 2 (LLM Meta-Router):* Low-confidence queries fallback to an ultra-fast local/cheap LLM (e.g., Llama 3 8B on Groq) to accurately gauge complexity.
- **Context-Aware Selection:** Calculates token count based on query length and file uploads, ensuring the chosen model has a large enough context window.
- **Capability Matching:** Automatically detects if a query needs Vision, Deep Thinking (Math/Logic), or Coding, and filters the model catalog accordingly.
- **Dynamic Scoring:** Models are ranked dynamically based on Price, Speed, and Tier matching.
- **Beautiful UI Playground:** A sleek chat interface to test out routing decisions in real time.

---

## 🚀 Quick Start (Windows)

The easiest way to run the project is by using the provided batch script.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/DevHarman24/LLM-Router-MAIN.git
   cd LLM-Router-MAIN
   ```

2. **Set up Environment Variables:**
   - Copy `.env.example` to `.env`.
   - Add your API keys inside `.env` (Groq for the fast meta-classifier, OpenRouter for model execution).
   ```bash
   OPENROUTER_API_KEY=your_key_here
   GROQ_API_KEY=your_key_here
   ```

3. **Run the App:**
   - Just double-click the **`start.bat`** file!
   - It will automatically install Python requirements, start the FastAPI backend, and open the frontend UI in your browser at `http://localhost:8000`.

---

## 🛠 Manual Installation

If you prefer to run it manually (or are on macOS/Linux):

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Start the Backend server:**
   ```bash
   uvicorn backend.server:app --port 8000 --reload
   ```
3. **Open the App:**
   Go to `http://localhost:8000` in your web browser.

---

## 📊 Evaluation Results
Tested against 100+ diverse queries (coding, image, simple, complex edge cases), the LLM router successfully reduced costs by **97%** compared to blindly using a Tier 1 frontier model, while maintaining a **99% accuracy rate** in correct model assignment. 

See `eval_report.html` for full evaluation details.
