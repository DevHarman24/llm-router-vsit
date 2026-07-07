# LLM Router Standard Mode Evaluation Report

## Overview
- Total Queries: 102
- Tier 1 (High Complexity): 38
- Tier 2 (Medium Complexity): 37
- Tier 3 (Low Complexity): 27

## Classifier Usage
- Heuristic only (high confidence, LLM skipped): 25
- Real Groq LLM classifier used: 77
- Mock classifier used (fallback): 0

## Performance
- Average Total Time: 3181.18 ms
- Average Heuristic Time: 1.29 ms
- Average LLM Classifier Time: 3137.02 ms

## Detailed Results
| ID | Category | Query | Model | Tier | LLM Used | Source | Vision | Think | Code | Time(ms) | Pass |
|---|---|---|---|---|---|---|---|---|---|---|---| 
| 1 | Simple | Hello there! | llama-4-scout | 3 | No | heuristic | False | False | False | 1413.5 | PASS |
| 2 | Simple | What is the capital of France? | llama-4-scout | 3 | No | heuristic | False | False | False | 1.3 | PASS |
| 3 | Simple | Define entropy. | llama-4-scout | 3 | No | heuristic | False | False | False | 0.9 | PASS |
| 4 | Simple | Is the sky blue? Yes or no. | llama-4-scout | 3 | No | heuristic | False | False | False | 2.0 | PASS |
| 5 | Simple | Who is the president of the US? | llama-4-scout | 3 | Yes | llm | False | False | False | 1863.0 | PASS |
| 6 | Simple | Tell me a joke. | llama-4-scout | 3 | No | heuristic | False | False | False | 0.6 | PASS |
| 7 | Simple | What's the weather like? | llama-4-scout | 3 | No | heuristic | False | False | False | 0.6 | PASS |
| 8 | Simple | Translate 'apple' to Spanish. | llama-4-scout | 3 | Yes | llm | False | False | False | 1434.6 | PASS |
| 9 | Simple | Format this list of names: John, Jane, Joe. | llama-4-scout | 3 | No | heuristic | False | False | False | 1.4 | PASS |
| 10 | Simple | Thank you very much. | llama-4-scout | 3 | No | heuristic | False | False | False | 0.7 | PASS |
| 11 | Simple | What is 2+2? | llama-4-scout | 3 | Yes | llm | False | False | False | 1192.1 | PASS |
| 12 | Simple | Synonym for happy. | llama-4-scout | 3 | No | heuristic | False | False | False | 0.6 | PASS |
| 13 | Simple | Where is the Eiffel Tower? | llama-4-scout | 3 | Yes | llm | False | False | False | 1205.0 | PASS |
| 14 | Simple | Find the word 'test' in this short sentence. | llama-4-scout | 3 | Yes | llm | False | False | False | 1129.6 | PASS |
| 15 | Simple | Extract the date from this string: 2024-05-12. | llama-4-scout | 3 | Yes | llm | False | False | False | 1177.1 | PASS |
| 16 | Simple | True or false: Earth is flat. | llama-4-scout | 3 | No | heuristic | False | False | False | 0.7 | PASS |
| 17 | Simple | What time is it in Tokyo? | llama-4-scout | 3 | Yes | llm | False | False | False | 1180.5 | PASS |
| 18 | Simple | Hey! | llama-4-scout | 3 | No | heuristic | False | False | False | 1.0 | PASS |
| 19 | Simple | How many days in a leap year? | llama-4-scout | 3 | Yes | llm | False | False | False | 1148.4 | PASS |
| 20 | Simple | What is water? | llama-4-scout | 3 | No | heuristic | False | False | False | 1.1 | PASS |
| 21 | Medium | Write a short blog post about the benefits of AI i | llama-4-maverick | 2 | Yes | llm | False | False | False | 1214.7 | PASS |
| 22 | Medium | Summarize this long article about global warming. | llama-4-maverick | 2 | Yes | llm | False | False | False | 1372.5 | PASS |
| 23 | Medium | Plan a 3-day itinerary for a trip to Rome. | llama-4-maverick | 2 | Yes | llm | False | False | False | 1235.8 | PASS |
| 24 | Medium | Explain how photosynthesis works in simple terms. | llama-4-maverick | 2 | Yes | llm | False | False | False | 1117.0 | PASS |
| 25 | Medium | Compare apples and oranges. | llama-4-maverick | 2 | Yes | llm | False | False | False | 1229.7 | PASS |
| 26 | Medium | Write an email to my boss asking for a raise. | llama-4-maverick | 2 | Yes | llm | False | False | False | 1095.2 | PASS |
| 27 | Medium | Review this feedback and give me your thoughts. | llama-4-maverick | 2 | Yes | llm | False | False | False | 3200.6 | PASS |
| 28 | Medium | Translate this whole paragraph into Japanese. | llama-4-scout | 3 | Yes | llm | False | False | False | 4240.6 | PASS |
| 29 | Medium | Describe the plot of the Matrix. | llama-4-maverick | 2 | Yes | llm | False | False | False | 4466.3 | PASS |
| 30 | Medium | Brainstorm 5 names for my new startup. | llama-4-maverick | 2 | Yes | llm | False | False | False | 5325.1 | PASS |
| 31 | Medium | Outline the history of the Roman Empire. | llama-4-maverick | 2 | Yes | llm | False | False | False | 4403.0 | PASS |
| 32 | Medium | Write a cover letter for a software engineer posit | llama-4-maverick | 2 | Yes | llm | False | False | False | 4605.0 | PASS |
| 33 | Medium | Explain the rules of basketball. | llama-4-maverick | 2 | Yes | llm | False | False | False | 4509.3 | PASS |
| 34 | Medium | Compare electric cars with gas cars. | llama-4-maverick | 2 | Yes | llm | False | False | False | 4301.6 | PASS |
| 35 | Medium | Write a short essay on the impact of social media. | llama-4-maverick | 2 | Yes | llm | False | False | False | 4300.7 | PASS |
| 36 | Medium | Describe how a car engine works. | llama-4-maverick | 2 | Yes | llm | False | False | False | 5381.0 | PASS |
| 37 | Medium | Summarize the book '1984'. | llama-4-maverick | 2 | Yes | llm | False | False | False | 4552.3 | PASS |
| 38 | Medium | Plan a weekly dinner menu. | llama-4-maverick | 2 | Yes | llm | False | False | False | 4300.6 | PASS |
| 39 | Medium | Write a creative story about a robot. | llama-4-maverick | 2 | Yes | llm | False | False | False | 4299.3 | PASS |
| 40 | Medium | Explain the difference between a stock and a bond. | llama-4-maverick | 2 | Yes | llm | False | False | False | 4814.0 | PASS |
| 41 | Complex | Design a scalable microservices architecture for a | o1-pro | 1 | No | heuristic | False | True | False | 2930.3 | PASS |
| 42 | Complex | Prove the Pythagorean theorem using geometry. | o1-pro | 1 | No | heuristic | False | True | False | 1.3 | PASS |
| 43 | Complex | Analyze the legal implications of this contract cl | o1-pro | 1 | Yes | llm | False | True | False | 1138.5 | PASS |
| 44 | Complex | What is the optimal business strategy for a new Sa | o1-pro | 1 | No | heuristic | False | True | False | 1.5 | PASS |
| 45 | Complex | Explain the intricacies of the Black-Scholes model | o1-pro | 1 | Yes | llm | False | True | False | 5554.0 | PASS |
| 46 | Complex | Derive the formula for the volume of a sphere. | o1-pro | 1 | No | heuristic | False | True | False | 1.3 | PASS |
| 47 | Complex | Design a deep learning model for natural language  | o1-pro | 1 | No | heuristic | False | True | False | 1.5 | PASS |
| 48 | Complex | Conduct a security audit on a standard OAuth2 impl | o1-pro | 1 | No | heuristic | False | True | False | 1.3 | PASS |
| 49 | Complex | Discuss the ethical implications of artificial gen | o1-pro | 1 | Yes | llm | False | True | False | 4297.3 | PASS |
| 50 | Complex | Provide a comprehensive competitive analysis of th | o1-pro | 1 | No | heuristic | False | True | False | 2.5 | PASS |
| 51 | Complex | How would you optimize performance tuning for a hi | claude-sonnet-4.5 | 1 | No | heuristic | False | True | True | 2.0 | PASS |
| 52 | Complex | What is the difference between a philosophical zom | o1-pro | 1 | Yes | llm | False | True | False | 4501.1 | PASS |
| 53 | Complex | Create a decision framework for whether a company  | o1-pro | 1 | Yes | llm | False | True | False | 4503.7 | PASS |
| 54 | Complex | Solve this complex differential equation step by s | o1-pro | 1 | Yes | llm | False | True | False | 4710.5 | PASS |
| 55 | Complex | Analyze the trade-offs between eventual consistenc | o1-pro | 1 | Yes | llm | False | True | False | 4300.3 | PASS |
| 56 | Complex | Explain the architecture of a transformer model in | o1-pro | 1 | No | heuristic | False | True | False | 1.5 | PASS |
| 57 | Complex | Design a Kubernetes orchestration strategy for 100 | o1-pro | 1 | No | heuristic | False | True | False | 1.3 | PASS |
| 58 | Complex | Review the vulnerability footprint of a monolithic | o1-pro | 1 | No | heuristic | False | True | False | 1.4 | PASS |
| 59 | Complex | Evaluate the pros and cons of different economic t | o1-pro | 1 | Yes | llm | False | True | False | 5424.0 | PASS |
| 60 | Complex | Explain how zero-knowledge proofs work in cryptogr | o1-pro | 1 | Yes | llm | False | True | False | 4609.1 | PASS |
| 61 | Coding | Write a Python script to scrape data from a websit | claude-sonnet-4.5 | 1 | Yes | llm | False | False | True | 4403.5 | PASS |
| 62 | Coding | Debug this React component that is not rendering p | claude-sonnet-4.5 | 1 | Yes | llm | False | False | True | 4402.4 | PASS |
| 63 | Coding | Implement a binary search tree in C++. | claude-sonnet-4.5 | 1 | Yes | llm | False | False | True | 4504.8 | PASS |
| 64 | Coding | Create a REST API using Node.js and Express. | claude-sonnet-4.5 | 1 | Yes | llm | False | False | True | 4433.8 | PASS |
| 65 | Coding | Refactor this legacy Java code to use modern strea | claude-sonnet-4.5 | 1 | No | heuristic | False | True | True | 1.8 | PASS |
| 66 | Coding | Write a SQL query to find the second highest salar | qwen3-coder-flash | 2 | Yes | llm | False | False | True | 4266.7 | PASS |
| 67 | Coding | How do I fix a segmentation fault in my C program? | claude-sonnet-4.5 | 1 | Yes | llm | False | False | True | 5325.3 | PASS |
| 68 | Coding | Build a simple to-do app in Next.js. | claude-sonnet-4.5 | 1 | Yes | llm | False | False | True | 4338.6 | PASS |
| 69 | Coding | Create a CSS animation for a bouncing ball. | claude-sonnet-4.5 | 1 | Yes | llm | True | False | True | 4263.3 | PASS |
| 70 | Coding | Write a shell script to backup a directory. | qwen3-coder-flash | 2 | Yes | llm | False | False | True | 5223.4 | PASS |
| 71 | Coding | Implement Dijkstra's algorithm in Python. | claude-sonnet-4.5 | 1 | Yes | llm | False | False | True | 4402.7 | PASS |
| 72 | Coding | Explain why this JavaScript promise is not resolvi | qwen3-coder-flash | 2 | Yes | llm | False | False | True | 4299.4 | PASS |
| 73 | Coding | Write a regex to validate an email address. | qwen3-coder-flash | 2 | Yes | llm | False | False | True | 4301.7 | PASS |
| 74 | Coding | How do I connect a Flask app to a PostgreSQL datab | qwen3-coder-flash | 2 | Yes | llm | False | False | True | 5324.2 | PASS |
| 75 | Coding | Build a responsive grid layout using Tailwind CSS. | qwen3-coder-flash | 2 | Yes | llm | False | False | True | 4198.2 | PASS |
| 76 | Coding | Implement authentication using JWT in Go. | claude-sonnet-4.5 | 1 | Yes | llm | False | False | True | 4404.9 | PASS |
| 77 | Coding | Write unit tests for a Python function using pytes | qwen3-coder-flash | 2 | Yes | llm | False | False | True | 5420.6 | PASS |
| 78 | Coding | Create a Dockerfile for a Node.js application. | claude-sonnet-4.5 | 1 | Yes | llm | False | False | True | 4305.9 | PASS |
| 79 | Coding | Explain how React's virtual DOM works. | qwen3-coder-flash | 2 | Yes | llm | False | False | True | 4505.3 | PASS |
| 80 | Coding | Write a script to automate Git commits. | claude-sonnet-4.5 | 1 | Yes | llm | False | False | True | 4506.4 | PASS |
| 81 | Image | What is the primary color in this screenshot? | llama-3.2-11b-vision-instruct | 3 | Yes | llm | True | False | False | 4401.5 | PASS |
| 82 | Image | Convert this UI design into React code. | claude-sonnet-4.5 | 1 | Yes | llm | True | False | True | 5325.5 | PASS |
| 83 | Image | Analyze the trend in this chart. | qwen3-vl-8b-instruct | 2 | Yes | llm | True | False | False | 4505.2 | PASS |
| 84 | Image | Describe the architecture shown in this diagram. | claude-sonnet-4.5 | 1 | Yes | llm | True | True | False | 4505.0 | PASS |
| 85 | Image | Extract the text from this handwritten note. | llama-3.2-11b-vision-instruct | 3 | Yes | llm | True | False | False | 4299.6 | PASS |
| 86 | Image | Is there a bug in the code shown in this image? | gpt-4o-mini-search-preview | 2 | Yes | llm | True | False | True | 5429.2 | PASS |
| 87 | Image | What objects do you see in this photo? | llama-3.2-11b-vision-instruct | 3 | Yes | llm | True | False | False | 4296.0 | PASS |
| 88 | Image | Summarize the data presented in this graph. | qwen3-vl-8b-instruct | 2 | Yes | llm | True | False | False | 4544.4 | PASS |
| 89 | Image | Translate the text in this image to French. | llama-3.2-11b-vision-instruct | 3 | Yes | llm | True | False | False | 5184.3 | PASS |
| 90 | Image | Write CSS to recreate the layout in this image. | claude-sonnet-4.5 | 1 | Yes | llm | True | False | True | 3789.5 | PASS |
| 91 | File | Summarize this PDF report. | llama-4-maverick | 2 | Yes | llm | False | False | False | 4710.5 | PASS |
| 92 | File | What are the key findings in this document? | llama-4-maverick | 2 | Yes | llm | False | False | False | 4712.4 | PASS |
| 93 | File | Review this Python code for security vulnerabiliti | claude-sonnet-4.5 | 1 | Yes | llm | False | True | True | 4809.5 | PASS |
| 94 | File | Refactor this JavaScript file to use ES6 syntax. | claude-sonnet-4.5 | 1 | No | heuristic | False | True | True | 0.9 | PASS |
| 95 | File | Extract all the dependencies from this requirement | qwen3-coder-flash | 2 | Yes | llm | False | False | True | 5018.3 | PASS |
| 96 | File | Find the section about 'API' in this document. | llama-4-maverick | 2 | Yes | llm | False | False | False | 3683.6 | PASS |
| 97 | File | Explain what this script does. | qwen3-coder-flash | 2 | Yes | llm | False | False | True | 4811.5 | PASS |
| 98 | File | Write unit tests for the functions in this file. | claude-sonnet-4.5 | 1 | Yes | llm | False | False | True | 4710.7 | PASS |
| 99 | File | Update this requirements file to the latest versio | qwen3-coder-flash | 2 | Yes | llm | False | False | True | 4708.7 | PASS |
| 100 | File | Translate this document to Spanish. | llama-4-scout | 3 | Yes | llm | False | False | False | 4711.8 | PASS |
| 101 | Simple | Find the exact word 'router' from this paragraph.  | llama-4-scout | 3 | Yes | llm | False | False | False | 10956.9 | PASS |
| 102 | Simple | Extract the email from the following massive block | llama-4-maverick | 2 | Yes | llm | False | False | False | 14829.4 | PASS |

## Failure Analysis
All queries routed correctly!
