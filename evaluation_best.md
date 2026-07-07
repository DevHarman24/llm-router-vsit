# LLM Router Best Mode Evaluation Report

## Overview
- Total Queries: 102
- Tier 1 (High Complexity): 37
- Tier 2 (Medium Complexity): 37
- Tier 3 (Low Complexity): 28

## Classifier Usage
- Heuristic only (high confidence, LLM skipped): 25
- Real Groq LLM classifier used: 77
- Mock classifier used (fallback): 0

## Performance
- Average Total Time: 3155.79 ms
- Average Heuristic Time: 1.17 ms
- Average LLM Classifier Time: 3126.01 ms

## Detailed Results
| ID | Category | Query | Model | Tier | LLM Used | Source | Vision | Think | Code | Time(ms) | Pass |
|---|---|---|---|---|---|---|---|---|---|---|---| 
| 1 | Simple | Hello there! | llama-4-scout | 3 | No | heuristic | False | False | False | 2858.9 | PASS |
| 2 | Simple | What is the capital of France? | llama-4-scout | 3 | No | heuristic | False | False | False | 1.0 | PASS |
| 3 | Simple | Define entropy. | llama-4-scout | 3 | No | heuristic | False | False | False | 0.7 | PASS |
| 4 | Simple | Is the sky blue? Yes or no. | llama-4-scout | 3 | No | heuristic | False | False | False | 0.7 | PASS |
| 5 | Simple | Who is the president of the US? | llama-4-scout | 3 | Yes | llm | False | False | False | 934.9 | PASS |
| 6 | Simple | Tell me a joke. | llama-4-scout | 3 | No | heuristic | False | False | False | 0.4 | PASS |
| 7 | Simple | What's the weather like? | llama-4-scout | 3 | No | heuristic | False | False | False | 0.4 | PASS |
| 8 | Simple | Translate 'apple' to Spanish. | llama-4-scout | 3 | Yes | llm | False | False | False | 664.2 | PASS |
| 9 | Simple | Format this list of names: John, Jane, Joe. | llama-4-scout | 3 | No | heuristic | False | False | False | 1.1 | PASS |
| 10 | Simple | Thank you very much. | llama-4-scout | 3 | No | heuristic | False | False | False | 0.8 | PASS |
| 11 | Simple | What is 2+2? | llama-4-scout | 3 | Yes | llm | False | False | False | 613.1 | PASS |
| 12 | Simple | Synonym for happy. | llama-4-scout | 3 | No | heuristic | False | False | False | 1.3 | PASS |
| 13 | Simple | Where is the Eiffel Tower? | llama-4-scout | 3 | Yes | llm | False | False | False | 714.6 | PASS |
| 14 | Simple | Find the word 'test' in this short sentence. | llama-4-scout | 3 | Yes | llm | False | False | False | 616.0 | PASS |
| 15 | Simple | Extract the date from this string: 2024-05-12. | llama-4-scout | 3 | Yes | llm | False | False | False | 613.2 | PASS |
| 16 | Simple | True or false: Earth is flat. | llama-4-scout | 3 | No | heuristic | False | False | False | 1.0 | PASS |
| 17 | Simple | What time is it in Tokyo? | llama-4-scout | 3 | Yes | llm | False | False | False | 598.7 | PASS |
| 18 | Simple | Hey! | llama-4-scout | 3 | No | heuristic | False | False | False | 0.8 | PASS |
| 19 | Simple | How many days in a leap year? | llama-4-scout | 3 | Yes | llm | False | False | False | 749.6 | PASS |
| 20 | Simple | What is water? | llama-4-scout | 3 | No | heuristic | False | False | False | 1.3 | PASS |
| 21 | Medium | Write a short blog post about the benefits of AI i | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | False | 538.2 | PASS |
| 22 | Medium | Summarize this long article about global warming. | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | False | 669.6 | PASS |
| 23 | Medium | Plan a 3-day itinerary for a trip to Rome. | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | False | 614.1 | PASS |
| 24 | Medium | Explain how photosynthesis works in simple terms. | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | False | 717.0 | PASS |
| 25 | Medium | Compare apples and oranges. | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | False | 596.9 | PASS |
| 26 | Medium | Write an email to my boss asking for a raise. | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | False | 5034.6 | PASS |
| 27 | Medium | Review this feedback and give me your thoughts. | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | False | 3796.7 | PASS |
| 28 | Medium | Translate this whole paragraph into Japanese. | llama-4-scout | 3 | Yes | llm | False | False | False | 4803.7 | PASS |
| 29 | Medium | Describe the plot of the Matrix. | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | False | 4001.1 | PASS |
| 30 | Medium | Brainstorm 5 names for my new startup. | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | False | 4632.4 | PASS |
| 31 | Medium | Outline the history of the Roman Empire. | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | False | 4883.7 | PASS |
| 32 | Medium | Write a cover letter for a software engineer posit | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | False | 4711.0 | PASS |
| 33 | Medium | Explain the rules of basketball. | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | False | 4812.0 | PASS |
| 34 | Medium | Compare electric cars with gas cars. | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | False | 3996.8 | PASS |
| 35 | Medium | Write a short essay on the impact of social media. | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | False | 4809.7 | PASS |
| 36 | Medium | Describe how a car engine works. | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | False | 4813.6 | PASS |
| 37 | Medium | Summarize the book '1984'. | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | False | 4506.4 | PASS |
| 38 | Medium | Plan a weekly dinner menu. | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | False | 3887.7 | PASS |
| 39 | Medium | Write a creative story about a robot. | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | False | 4814.6 | PASS |
| 40 | Medium | Explain the difference between a stock and a bond. | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | False | 4813.0 | PASS |
| 41 | Complex | Design a scalable microservices architecture for a | o1-pro | 1 | No | heuristic | False | True | False | 1.2 | PASS |
| 42 | Complex | Prove the Pythagorean theorem using geometry. | o1-pro | 1 | No | heuristic | False | True | False | 1.0 | PASS |
| 43 | Complex | Analyze the legal implications of this contract cl | o1-pro | 1 | Yes | llm | False | True | False | 4810.1 | PASS |
| 44 | Complex | What is the optimal business strategy for a new Sa | o1-pro | 1 | No | heuristic | False | True | False | 1.3 | PASS |
| 45 | Complex | Explain the intricacies of the Black-Scholes model | o1-pro | 1 | Yes | llm | False | True | False | 3789.2 | PASS |
| 46 | Complex | Derive the formula for the volume of a sphere. | o1-pro | 1 | No | heuristic | False | True | False | 1.0 | PASS |
| 47 | Complex | Design a deep learning model for natural language  | o1-pro | 1 | No | heuristic | False | True | False | 1.0 | PASS |
| 48 | Complex | Conduct a security audit on a standard OAuth2 impl | o1-pro | 1 | No | heuristic | False | True | False | 1.0 | PASS |
| 49 | Complex | Discuss the ethical implications of artificial gen | o1-pro | 1 | Yes | llm | False | True | False | 4808.1 | PASS |
| 50 | Complex | Provide a comprehensive competitive analysis of th | o1-pro | 1 | No | heuristic | False | True | False | 1.2 | PASS |
| 51 | Complex | How would you optimize performance tuning for a hi | claude-sonnet-4.5 | 1 | No | heuristic | False | True | True | 0.9 | PASS |
| 52 | Complex | What is the difference between a philosophical zom | o1-pro | 1 | Yes | llm | False | True | False | 4614.1 | PASS |
| 53 | Complex | Create a decision framework for whether a company  | o1-pro | 1 | Yes | llm | False | True | False | 4804.0 | PASS |
| 54 | Complex | Solve this complex differential equation step by s | o1-pro | 1 | Yes | llm | False | True | False | 4813.2 | PASS |
| 55 | Complex | Analyze the trade-offs between eventual consistenc | o1-pro | 1 | Yes | llm | False | True | False | 4712.2 | PASS |
| 56 | Complex | Explain the architecture of a transformer model in | o1-pro | 1 | No | heuristic | False | True | False | 1.1 | PASS |
| 57 | Complex | Design a Kubernetes orchestration strategy for 100 | o1-pro | 1 | No | heuristic | False | True | False | 1.0 | PASS |
| 58 | Complex | Review the vulnerability footprint of a monolithic | o1-pro | 1 | No | heuristic | False | True | False | 1.1 | PASS |
| 59 | Complex | Evaluate the pros and cons of different economic t | o1-pro | 1 | Yes | llm | False | True | False | 4909.2 | PASS |
| 60 | Complex | Explain how zero-knowledge proofs work in cryptogr | gpt-4o-mini-search-preview | 2 | Yes | llm | False | True | False | 3663.2 | PASS |
| 61 | Coding | Write a Python script to scrape data from a websit | claude-sonnet-4.5 | 1 | Yes | llm | False | False | True | 4836.6 | PASS |
| 62 | Coding | Debug this React component that is not rendering p | claude-sonnet-4.5 | 1 | Yes | llm | False | False | True | 4812.5 | PASS |
| 63 | Coding | Implement a binary search tree in C++. | claude-sonnet-4.5 | 1 | Yes | llm | False | False | True | 4608.1 | PASS |
| 64 | Coding | Create a REST API using Node.js and Express. | claude-sonnet-4.5 | 1 | Yes | llm | False | False | True | 3893.1 | PASS |
| 65 | Coding | Refactor this legacy Java code to use modern strea | claude-sonnet-4.5 | 1 | No | heuristic | False | True | True | 1.0 | PASS |
| 66 | Coding | Write a SQL query to find the second highest salar | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | True | 4707.3 | PASS |
| 67 | Coding | How do I fix a segmentation fault in my C program? | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | True | 4813.3 | PASS |
| 68 | Coding | Build a simple to-do app in Next.js. | claude-sonnet-4.5 | 1 | Yes | llm | False | False | True | 5119.6 | PASS |
| 69 | Coding | Create a CSS animation for a bouncing ball. | claude-sonnet-4.5 | 1 | Yes | llm | True | False | True | 5017.7 | PASS |
| 70 | Coding | Write a shell script to backup a directory. | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | True | 3788.2 | PASS |
| 71 | Coding | Implement Dijkstra's algorithm in Python. | claude-sonnet-4.5 | 1 | Yes | llm | False | False | True | 5532.1 | PASS |
| 72 | Coding | Explain why this JavaScript promise is not resolvi | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | True | 3952.1 | PASS |
| 73 | Coding | Write a regex to validate an email address. | claude-sonnet-4.5 | 1 | Yes | llm | False | True | True | 4852.9 | PASS |
| 74 | Coding | How do I connect a Flask app to a PostgreSQL datab | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | True | 4683.4 | PASS |
| 75 | Coding | Build a responsive grid layout using Tailwind CSS. | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | True | 4634.3 | PASS |
| 76 | Coding | Implement authentication using JWT in Go. | claude-sonnet-4.5 | 1 | Yes | llm | False | False | True | 3891.3 | PASS |
| 77 | Coding | Write unit tests for a Python function using pytes | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | True | 5019.2 | PASS |
| 78 | Coding | Create a Dockerfile for a Node.js application. | claude-sonnet-4.5 | 1 | Yes | llm | False | False | True | 4913.3 | PASS |
| 79 | Coding | Explain how React's virtual DOM works. | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | True | 4915.2 | PASS |
| 80 | Coding | Write a script to automate Git commits. | claude-sonnet-4.5 | 1 | Yes | llm | False | False | True | 3791.1 | PASS |
| 81 | Image | What is the primary color in this screenshot? | qwen3-vl-32b-instruct | 3 | Yes | llm | True | False | False | 4812.5 | PASS |
| 82 | Image | Convert this UI design into React code. | claude-sonnet-4.5 | 1 | Yes | llm | True | True | True | 4504.6 | PASS |
| 83 | Image | Analyze the trend in this chart. | gpt-4o-mini-search-preview | 2 | Yes | llm | True | False | False | 5358.5 | PASS |
| 84 | Image | Describe the architecture shown in this diagram. | claude-sonnet-4.5 | 1 | Yes | llm | True | True | False | 4264.7 | PASS |
| 85 | Image | Extract the text from this handwritten note. | qwen3-vl-32b-instruct | 3 | Yes | llm | True | False | False | 4301.3 | PASS |
| 86 | Image | Is there a bug in the code shown in this image? | gpt-4o-mini-search-preview | 2 | Yes | llm | True | False | True | 5326.0 | PASS |
| 87 | Image | What objects do you see in this photo? | qwen3-vl-32b-instruct | 3 | Yes | llm | True | False | False | 4210.6 | PASS |
| 88 | Image | Summarize the data presented in this graph. | gpt-4o-mini-search-preview | 2 | Yes | llm | True | False | False | 4594.3 | PASS |
| 89 | Image | Translate the text in this image to French. | qwen3-vl-32b-instruct | 3 | Yes | llm | True | False | False | 4503.5 | PASS |
| 90 | Image | Write CSS to recreate the layout in this image. | claude-sonnet-4.5 | 1 | Yes | llm | True | False | True | 5323.8 | PASS |
| 91 | File | Summarize this PDF report. | grok-4.20-multi-agent | 2 | Yes | llm | False | False | False | 4198.7 | PASS |
| 92 | File | What are the key findings in this document? | grok-4.20-multi-agent | 2 | Yes | llm | False | False | False | 4439.2 | PASS |
| 93 | File | Review this Python code for security vulnerabiliti | claude-sonnet-4.5 | 1 | Yes | llm | False | True | True | 4259.3 | PASS |
| 94 | File | Refactor this JavaScript file to use ES6 syntax. | claude-sonnet-4.5 | 1 | No | heuristic | False | True | True | 1.0 | PASS |
| 95 | File | Extract all the dependencies from this requirement | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | True | 5326.9 | PASS |
| 96 | File | Find the section about 'API' in this document. | llama-4-scout | 3 | Yes | llm | False | False | False | 4231.8 | PASS |
| 97 | File | Explain what this script does. | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | True | 4369.7 | PASS |
| 98 | File | Write unit tests for the functions in this file. | claude-sonnet-4.5 | 1 | Yes | llm | False | False | True | 4812.5 | PASS |
| 99 | File | Update this requirements file to the latest versio | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | True | 4300.4 | PASS |
| 100 | File | Translate this document to Spanish. | llama-4-scout | 3 | Yes | llm | False | False | False | 5212.8 | PASS |
| 101 | Simple | Find the exact word 'router' from this paragraph.  | llama-4-scout | 3 | Yes | llm | False | False | False | 10351.1 | PASS |
| 102 | Simple | Extract the email from the following massive block | gpt-4o-mini-search-preview | 2 | Yes | llm | False | False | False | 14644.6 | PASS |

## Failure Analysis
All queries routed correctly!
