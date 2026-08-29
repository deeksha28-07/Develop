# MP1 Prompt Lab — Reflection

## 1. Which strategy won, and on what dimension? (Accuracy? Parse rate? Cost?)

There was no single strategy that won,Few-shot and structured prompting have the highest accuracy with an average of 2.9 out of the 3 fields correct. Both strategies also achieved a 100% parse rate. CoT, few-shot, and structured prompting had the highest LLM judge score of 3.8 out of 4.CoT performed best in latency, with a median latency of 0.959 seconds. It was also lower-cost. Zero-shot had a lower total cost as well, but it had the lowest judge score of 3.6 and the highest median latency of 1.310 seconds.Overall, i would consider few-shot and structured prompting as better strategies because they have the highest accuracy while maintaining a high judge score.

## 2. What surprised you?

What surprised me was that all four strategies had a 100% parse rate. I expected structured prompting to perform better because it clearly tells the model what format to follow. But even zero-shot and CoT were able to return valid JSON for all 10 snippets.

I was also surprised that the accuracy difference was very small. Few-shot and structured got 2.9/3, while CoT and zero-shot got 2.8/3. Zero-shot also had the lowest judge score of 3.6, while CoT, few-shot and structured got 3.8.

## 3. For my capstone domain, which strategy would I reach for first? Justify in 2-3 sentences.

For my capstone, I would choose structured prompting because it gives me clear instructions about the role, task, context and output format. It also makes the output easier to validate. In the results that I got, structured prompting got 2.9/3 accuracy, 100% parse rate and 3.8/4 judge score.

## 4. If you had another day, what would you try next? (Different model? More snippets? Different prompts?)
If I had another day, I would try the same four strategies with more snippets and a different model like Claude to see if the results are consistent. I would also try different prompts compare the accuracy, cost and latency.


## Comparison Summary

| Strategy | Accuracy (mean of 3) | Parse Rate | Judge Score | Total Cost ($) | Latency p50 (s) |
|---|---:|---:|---:|---:|---:|
| CoT | 2.8 | 1.0 | 3.8 | 0.000 | 0.959 |
| Few-shot | 2.9 | 1.0 | 3.8 | 0.001 | 1.001 |
| Structured | 2.9 | 1.0 | 3.8 | 0.001 | 1.111 |
| Zero-shot | 2.8 | 1.0 | 3.6 | 0.000 | 1.310 |
