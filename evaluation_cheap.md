# LLM Router Cheap Mode Evaluation Report

## Overview
- Total Queries: 102
- Tier 1 (High Complexity): 38
- Tier 2 (Medium Complexity): 36
- Tier 3 (Low Complexity): 28

## Classifier Usage
- Heuristic only (high confidence, LLM skipped): 25
- Real Groq LLM classifier used: 77
- Mock classifier used (fallback): 0

## Performance
- Average Total Time: 3124.25 ms
- Average Heuristic Time: 1.32 ms
- Average LLM Classifier Time: 3114.76 ms

## Detailed Results
| ID | Category | Query | Model | Tier | LLM Used | Source | Vision | Think | Code | Time(ms) | Pass |
|---|---|---|---|---|---|---|---|---|---|---|---| 
| 1 | Simple | Hello there! | ling-2.6-flash | 3 | No | heuristic | False | False | False | 825.2 | PASS |
| 2 | Simple | What is the capital of France? | ling-2.6-flash | 3 | No | heuristic | False | False | False | 0.5 | PASS |
| 3 | Simple | Define entropy. | ling-2.6-flash | 3 | No | heuristic | False | False | False | 0.3 | PASS |
| 4 | Simple | Is the sky blue? Yes or no. | ling-2.6-flash | 3 | No | heuristic | False | False | False | 0.4 | PASS |
| 5 | Simple | Who is the president of the US? | ling-2.6-flash | 3 | Yes | llm | False | False | False | 1059.2 | PASS |
| 6 | Simple | Tell me a joke. | ling-2.6-flash | 3 | No | heuristic | False | False | False | 0.6 | PASS |
| 7 | Simple | What's the weather like? | ling-2.6-flash | 3 | No | heuristic | False | False | False | 0.7 | PASS |
| 8 | Simple | Translate 'apple' to Spanish. | ling-2.6-flash | 3 | Yes | llm | False | False | False | 496.1 | PASS |
| 9 | Simple | Format this list of names: John, Jane, Joe. | ling-2.6-flash | 3 | No | heuristic | False | False | False | 0.6 | PASS |
| 10 | Simple | Thank you very much. | ling-2.6-flash | 3 | No | heuristic | False | False | False | 0.4 | PASS |
| 11 | Simple | What is 2+2? | ling-2.6-flash | 3 | Yes | llm | False | False | False | 498.2 | PASS |
| 12 | Simple | Synonym for happy. | ling-2.6-flash | 3 | No | heuristic | False | False | False | 0.4 | PASS |
| 13 | Simple | Where is the Eiffel Tower? | ling-2.6-flash | 3 | Yes | llm | False | False | False | 650.2 | PASS |
| 14 | Simple | Find the word 'test' in this short sentence. | ling-2.6-flash | 3 | Yes | llm | False | False | False | 659.0 | PASS |
| 15 | Simple | Extract the date from this string: 2024-05-12. | ling-2.6-flash | 3 | Yes | llm | False | False | False | 649.8 | PASS |
| 16 | Simple | True or false: Earth is flat. | ling-2.6-flash | 3 | No | heuristic | False | False | False | 0.6 | PASS |
| 17 | Simple | What time is it in Tokyo? | ling-2.6-flash | 3 | Yes | llm | False | False | False | 601.1 | PASS |
| 18 | Simple | Hey! | ling-2.6-flash | 3 | No | heuristic | False | False | False | 0.4 | PASS |
| 19 | Simple | How many days in a leap year? | ling-2.6-flash | 3 | Yes | llm | False | False | False | 612.8 | PASS |
| 20 | Simple | What is water? | ling-2.6-flash | 3 | No | heuristic | False | False | False | 0.5 | PASS |
| 21 | Medium | Write a short blog post about the benefits of AI i | qwen3-vl-8b-instruct | 2 | Yes | llm | False | False | False | 612.1 | PASS |
| 22 | Medium | Summarize this long article about global warming. | qwen3-vl-8b-instruct | 2 | Yes | llm | False | False | False | 513.9 | PASS |
| 23 | Medium | Plan a 3-day itinerary for a trip to Rome. | qwen3-vl-8b-instruct | 2 | Yes | llm | False | False | False | 695.6 | PASS |
| 24 | Medium | Explain how photosynthesis works in simple terms. | qwen3-vl-8b-instruct | 2 | Yes | llm | False | False | False | 634.8 | PASS |
| 25 | Medium | Compare apples and oranges. | qwen3-vl-8b-instruct | 2 | Yes | llm | False | False | False | 614.6 | PASS |
| 26 | Medium | Write an email to my boss asking for a raise. | qwen3-vl-8b-instruct | 2 | Yes | llm | False | False | False | 2845.9 | PASS |
| 27 | Medium | Review this feedback and give me your thoughts. | qwen3-vl-8b-instruct | 2 | Yes | llm | False | False | False | 4627.9 | PASS |
| 28 | Medium | Translate this whole paragraph into Japanese. | ling-2.6-flash | 3 | Yes | llm | False | False | False | 4813.1 | PASS |
| 29 | Medium | Describe the plot of the Matrix. | qwen3-vl-8b-instruct | 2 | Yes | llm | False | False | False | 4710.3 | PASS |
| 30 | Medium | Brainstorm 5 names for my new startup. | qwen3-vl-8b-instruct | 2 | Yes | llm | False | False | False | 4821.3 | PASS |
| 31 | Medium | Outline the history of the Roman Empire. | qwen3-vl-8b-instruct | 2 | Yes | llm | False | False | False | 3693.9 | PASS |
| 32 | Medium | Write a cover letter for a software engineer posit | qwen3-vl-8b-instruct | 2 | Yes | llm | False | False | False | 4699.2 | PASS |
| 33 | Medium | Explain the rules of basketball. | qwen3-vl-8b-instruct | 2 | Yes | llm | False | False | False | 4911.9 | PASS |
| 34 | Medium | Compare electric cars with gas cars. | qwen3-vl-8b-instruct | 2 | Yes | llm | False | False | False | 4607.3 | PASS |
| 35 | Medium | Write a short essay on the impact of social media. | qwen3-vl-8b-instruct | 2 | Yes | llm | False | False | False | 4812.1 | PASS |
| 36 | Medium | Describe how a car engine works. | qwen3-vl-8b-instruct | 2 | Yes | llm | False | False | False | 4710.2 | PASS |
| 37 | Medium | Summarize the book '1984'. | qwen3-vl-8b-instruct | 2 | Yes | llm | False | False | False | 3666.9 | PASS |
| 38 | Medium | Plan a weekly dinner menu. | qwen3-vl-8b-instruct | 2 | Yes | llm | False | False | False | 4935.1 | PASS |
| 39 | Medium | Write a creative story about a robot. | qwen3-vl-8b-instruct | 2 | Yes | llm | False | False | False | 4726.6 | PASS |
| 40 | Medium | Explain the difference between a stock and a bond. | qwen3-vl-8b-instruct | 2 | Yes | llm | False | False | False | 4795.6 | PASS |
| 41 | Complex | Design a scalable microservices architecture for a | l3-lunaris-8b | 1 | No | heuristic | False | True | False | 0.3 | PASS |
| 42 | Complex | Prove the Pythagorean theorem using geometry. | l3-lunaris-8b | 1 | No | heuristic | False | True | False | 0.2 | PASS |
| 43 | Complex | Analyze the legal implications of this contract cl | l3-lunaris-8b | 1 | Yes | llm | False | True | False | 4710.2 | PASS |
| 44 | Complex | What is the optimal business strategy for a new Sa | l3-lunaris-8b | 1 | No | heuristic | False | True | False | 0.6 | PASS |
| 45 | Complex | Explain the intricacies of the Black-Scholes model | l3-lunaris-8b | 1 | Yes | llm | False | True | False | 5019.6 | PASS |
| 46 | Complex | Derive the formula for the volume of a sphere. | l3-lunaris-8b | 1 | No | heuristic | False | True | False | 0.5 | PASS |
| 47 | Complex | Design a deep learning model for natural language  | l3-lunaris-8b | 1 | No | heuristic | False | True | False | 0.6 | PASS |
| 48 | Complex | Conduct a security audit on a standard OAuth2 impl | l3-lunaris-8b | 1 | No | heuristic | False | True | False | 0.5 | PASS |
| 49 | Complex | Discuss the ethical implications of artificial gen | l3-lunaris-8b | 1 | Yes | llm | False | True | False | 3682.1 | PASS |
| 50 | Complex | Provide a comprehensive competitive analysis of th | l3-lunaris-8b | 1 | No | heuristic | False | True | False | 0.6 | PASS |
| 51 | Complex | How would you optimize performance tuning for a hi | gpt-5-nano | 1 | No | heuristic | False | True | True | 0.6 | PASS |
| 52 | Complex | What is the difference between a philosophical zom | l3-lunaris-8b | 1 | Yes | llm | False | True | False | 4710.7 | PASS |
| 53 | Complex | Create a decision framework for whether a company  | l3-lunaris-8b | 1 | Yes | llm | False | True | False | 4708.2 | PASS |
| 54 | Complex | Solve this complex differential equation step by s | l3-lunaris-8b | 1 | Yes | llm | False | True | False | 4709.9 | PASS |
| 55 | Complex | Analyze the trade-offs between eventual consistenc | l3-lunaris-8b | 1 | Yes | llm | False | True | False | 4917.9 | PASS |
| 56 | Complex | Explain the architecture of a transformer model in | l3-lunaris-8b | 1 | No | heuristic | False | True | False | 0.5 | PASS |
| 57 | Complex | Design a Kubernetes orchestration strategy for 100 | l3-lunaris-8b | 1 | No | heuristic | False | True | False | 0.5 | PASS |
| 58 | Complex | Review the vulnerability footprint of a monolithic | l3-lunaris-8b | 1 | No | heuristic | False | True | False | 0.6 | PASS |
| 59 | Complex | Evaluate the pros and cons of different economic t | l3-lunaris-8b | 1 | Yes | llm | False | True | False | 3784.6 | PASS |
| 60 | Complex | Explain how zero-knowledge proofs work in cryptogr | l3-lunaris-8b | 1 | Yes | llm | False | True | False | 4650.6 | PASS |
| 61 | Coding | Write a Python script to scrape data from a websit | gpt-5-nano | 1 | Yes | llm | False | False | True | 4873.5 | PASS |
| 62 | Coding | Debug this React component that is not rendering p | gpt-5-nano | 1 | Yes | llm | False | False | True | 5222.8 | PASS |
| 63 | Coding | Implement a binary search tree in C++. | gpt-5-nano | 1 | Yes | llm | False | False | True | 3706.6 | PASS |
| 64 | Coding | Create a REST API using Node.js and Express. | gpt-5-nano | 1 | Yes | llm | False | False | True | 4998.6 | PASS |
| 65 | Coding | Refactor this legacy Java code to use modern strea | gpt-5-nano | 1 | No | heuristic | False | True | True | 0.4 | PASS |
| 66 | Coding | Write a SQL query to find the second highest salar | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | True | 4705.5 | PASS |
| 67 | Coding | How do I fix a segmentation fault in my C program? | gpt-5-nano | 1 | Yes | llm | False | False | True | 5021.0 | PASS |
| 68 | Coding | Build a simple to-do app in Next.js. | gpt-5-nano | 1 | Yes | llm | False | False | True | 3788.0 | PASS |
| 69 | Coding | Create a CSS animation for a bouncing ball. | gpt-5-nano | 1 | Yes | llm | True | False | True | 4915.3 | PASS |
| 70 | Coding | Write a shell script to backup a directory. | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | True | 4714.0 | PASS |
| 71 | Coding | Implement Dijkstra's algorithm in Python. | gpt-5-nano | 1 | Yes | llm | False | False | True | 4810.1 | PASS |
| 72 | Coding | Explain why this JavaScript promise is not resolvi | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | True | 4813.0 | PASS |
| 73 | Coding | Write a regex to validate an email address. | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | True | 3654.4 | PASS |
| 74 | Coding | How do I connect a Flask app to a PostgreSQL datab | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | True | 4946.5 | PASS |
| 75 | Coding | Build a responsive grid layout using Tailwind CSS. | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | True | 4918.1 | PASS |
| 76 | Coding | Implement authentication using JWT in Go. | gpt-5-nano | 1 | Yes | llm | False | False | True | 4810.1 | PASS |
| 77 | Coding | Write unit tests for a Python function using pytes | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | True | 3892.5 | PASS |
| 78 | Coding | Create a Dockerfile for a Node.js application. | gpt-5-nano | 1 | Yes | llm | False | False | True | 4882.6 | PASS |
| 79 | Coding | Explain how React's virtual DOM works. | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | True | 4733.4 | PASS |
| 80 | Coding | Write a script to automate Git commits. | gpt-5-nano | 1 | Yes | llm | False | False | True | 4718.8 | PASS |
| 81 | Image | What is the primary color in this screenshot? | llama-3.2-11b-vision-instruct | 3 | Yes | llm | True | False | False | 4709.8 | PASS |
| 82 | Image | Convert this UI design into React code. | gpt-5-nano | 1 | Yes | llm | True | True | True | 4916.9 | PASS |
| 83 | Image | Analyze the trend in this chart. | qwen3-vl-8b-instruct | 2 | Yes | llm | True | False | False | 4707.8 | PASS |
| 84 | Image | Describe the architecture shown in this diagram. | gpt-5-nano | 1 | Yes | llm | True | True | False | 3686.0 | PASS |
| 85 | Image | Extract the text from this handwritten note. | llama-3.2-11b-vision-instruct | 3 | Yes | llm | True | False | False | 4709.9 | PASS |
| 86 | Image | Is there a bug in the code shown in this image? | gpt-4o-mini-search-preview | 2 | Yes | llm | True | False | True | 4712.1 | PASS |
| 87 | Image | What objects do you see in this photo? | llama-3.2-11b-vision-instruct | 3 | Yes | llm | True | False | False | 4814.0 | PASS |
| 88 | Image | Summarize the data presented in this graph. | qwen3-vl-8b-instruct | 2 | Yes | llm | True | False | False | 4402.0 | PASS |
| 89 | Image | Translate the text in this image to French. | llama-3.2-11b-vision-instruct | 3 | Yes | llm | True | False | False | 5527.4 | PASS |
| 90 | Image | Write CSS to recreate the layout in this image. | gpt-5-nano | 1 | Yes | llm | True | False | True | 4505.9 | PASS |
| 91 | File | Summarize this PDF report. | qwen3-vl-8b-instruct | 2 | Yes | llm | False | False | False | 4401.5 | PASS |
| 92 | File | What are the key findings in this document? | qwen3-vl-8b-instruct | 2 | Yes | llm | False | False | False | 4444.6 | PASS |
| 93 | File | Review this Python code for security vulnerabiliti | gpt-5-nano | 1 | Yes | llm | False | True | True | 4420.4 | PASS |
| 94 | File | Refactor this JavaScript file to use ES6 syntax. | gpt-5-nano | 1 | No | heuristic | False | True | True | 1.1 | PASS |
| 95 | File | Extract all the dependencies from this requirement | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | True | 4342.9 | PASS |
| 96 | File | Find the section about 'API' in this document. | ling-2.6-flash | 3 | Yes | llm | False | False | False | 4472.8 | PASS |
| 97 | File | Explain what this script does. | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | True | 5455.1 | PASS |
| 98 | File | Write unit tests for the functions in this file. | gpt-5-nano | 1 | Yes | llm | False | False | True | 4612.8 | PASS |
| 99 | File | Update this requirements file to the latest versio | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | True | 4380.7 | PASS |
| 100 | File | Translate this document to Spanish. | ling-2.6-flash | 3 | Yes | llm | False | False | False | 4729.5 | PASS |
| 101 | Simple | Find the exact word 'router' from this paragraph.  | ling-2.6-flash | 3 | Yes | llm | False | False | False | 10723.0 | PASS |
| 102 | Simple | Extract the email from the following massive block | qwen3-vl-8b-instruct | 2 | Yes | llm | False | False | False | 14467.9 | PASS |

## Failure Analysis
All queries routed correctly!
