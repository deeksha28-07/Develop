import asyncio
import json
import os
import time
from pathlib import Path

import pandas as pd
from openai import AsyncOpenAI

assert os.environ.get('OPENAI_API_KEY'), 'Set OPENAI_API_KEY first'

client = AsyncOpenAI()

MODEL = 'gpt-4o-mini'
JUDGE_MODEL = 'gpt-4o'
TEMPERATURE = 0.0

RATES = {
    'gpt-4o-mini': {
        'in': 0.15 / 1_000_000,
        'out': 0.60 / 1_000_000
    },
    'gpt-4o': {
        'in': 2.50 / 1_000_000,
        'out': 10.00 / 1_000_000
    },
}

print('Setup complete.')

DATA_DIR = Path('data')
snippets = [json.loads(line) for line in (DATA_DIR / 'job_snippets.jsonl').read_text().splitlines() if line.strip()]
golden = {row['id']: row for row in (json.loads(line) for line in (DATA_DIR / 'golden_set.jsonl').read_text().splitlines() if line.strip())}


print(f'Loaded {len(snippets)} snippets, {len(golden)} golden entries.')
print('Sample snippet:', snippets[0])


def prompt_zero_shot(snippet_text: str) -> list[dict]:
    """Strategy 1 — zero-shot."""

    return [
        {
            'role': 'user',
            'content': f"""
Extract the following information from the job description:

1. company
2. role
3. years_experience_required

Return the answer as a JSON object with exactly these fields:

{{
    "company": "...",
    "role": "...",
    "years_experience_required": number or null
}}

Job description:
{snippet_text}
"""
        }
    ]


def prompt_few_shot(snippet_text: str) -> list[dict]:
    """Strategy 2 — few-shot."""

    return [
        {
            'role': 'user',
            'content': f"""
Extract company, role, and years_experience_required from the job
description.

Examples:

Example 1:
Job description:
"Acme Corp is hiring a Senior Software Engineer with 5+ years
of backend development experience."

Output:
{{
    "company": "Acme Corp",
    "role": "Senior Software Engineer",
    "years_experience_required": 5
}}

Example 2:
Job description:
"Hooli is looking for a Junior Frontend Developer. Fresh grads
welcome — no prior experience required."

Output:
{{
    "company": "Hooli",
    "role": "Junior Frontend Developer",
    "years_experience_required": 0
}}

Example 3:
Job description:
"Cyberdyne Systems is hiring an AI/ML Research Scientist.
We don't list a specific years requirement."

Output:
{{
    "company": "Cyberdyne Systems",
    "role": "AI/ML Research Scientist",
    "years_experience_required": null
}}

Now extract the same three fields from this job description:

{snippet_text}

Return only a JSON object with these fields:
company
role
years_experience_required
"""
        }
    ]


def prompt_structured(snippet_text: str) -> list[dict]:
    """Strategy 3 — structured / role-based."""

    return [
        {
            'role': 'system',
            'content': """
ROLE:
You are an expert technical recruiter and information extraction
specialist.

TASK:
Extract exactly three pieces of information from the supplied job
description:

1. company
2. role
3. years_experience_required

CONTEXT:
The years_experience_required field should represent the minimum
number of years explicitly stated or implied as the requirement.

Rules:
- "5+ years" -> 5
- "at least 4 years" -> 4
- "around 6 years" -> 6
- "about three years" -> 3
- "3 to 5 years" -> 3
- "fresh graduates welcome" / "no prior experience required" -> 0
- If no years requirement is stated -> null
- Do not fabricate a number.

EXAMPLES:

Example:
"Acme Corp is hiring a Senior Software Engineer with 5+ years
of backend development experience."

Output:
{
    "company": "Acme Corp",
    "role": "Senior Software Engineer",
    "years_experience_required": 5
}

Example:
"Cyberdyne Systems is hiring an AI/ML Research Scientist.
We don't list a specific years requirement."

Output:
{
    "company": "Cyberdyne Systems",
    "role": "AI/ML Research Scientist",
    "years_experience_required": null
}

FORMAT:
Return ONLY valid JSON.

Use exactly these fields:

{
    "company": "string",
    "role": "string",
    "years_experience_required": number or null
}
"""
        },
        {
            'role': 'user',
            'content': snippet_text
        }
    ]


def prompt_cot(snippet_text: str) -> list[dict]:
    """Strategy 4 — chain-of-thought."""

    return [
        {
            'role': 'user',
            'content': f"""
Extract the following fields from the job description:

- company
- role
- years_experience_required

Think through the job description carefully before producing
the answer.

For years_experience_required:
- Extract the minimum explicitly stated number.
- "5+ years" means 5.
- "3 to 5 years" means 3.
- "about three years" means 3.
- "fresh grads welcome" means 0.
- If there is no years requirement, return null.
- Do not fabricate a number.

Return the final answer as JSON with exactly these fields:

{{
    "company": "...",
    "role": "...",
    "years_experience_required": number or null
}}

Job description:
{snippet_text}
"""
        }
    ]


STRATEGIES = {
    'zero_shot': prompt_zero_shot,
    'few_shot': prompt_few_shot,
    'structured': prompt_structured,
    'cot': prompt_cot,
}


def parse_response(text: str) -> dict | None:
    """Try to parse a JSON object from the model response."""

    text = text.strip()

    if text.startswith('```'):
        lines = text.splitlines()

        if lines[0].startswith('```'):
            lines = lines[1:]

        if lines and lines[-1].strip() == '```':
            lines = lines[:-1]

        text = '\n'.join(lines).strip()

    try:
        return json.loads(text)

    except json.JSONDecodeError:
        start = text.find('{')
        end = text.rfind('}')

        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                return None

        return None


async def run_one(strategy_name: str, snippet: dict) -> dict:
    """Run one strategy on one snippet."""

    start_time = time.perf_counter()

    try:
        messages = STRATEGIES[strategy_name](snippet['snippet'])

        response = await client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=TEMPERATURE
        )

        latency = time.perf_counter() - start_time

        raw_response = response.choices[0].message.content

        extracted = parse_response(raw_response)

        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens

        cost_usd = (
            input_tokens * RATES[MODEL]['in']
            + output_tokens * RATES[MODEL]['out']
        )

        return {
            'strategy': strategy_name,
            'snippet_id': snippet['id'],
            'raw_response': raw_response,
            'extracted': extracted,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cost_usd': cost_usd,
            'latency_s': latency,
            'error': None
        }

    except Exception as e:

        latency = time.perf_counter() - start_time

        return {
            'strategy': strategy_name,
            'snippet_id': snippet['id'],
            'raw_response': None,
            'extracted': None,
            'input_tokens': 0,
            'output_tokens': 0,
            'cost_usd': 0.0,
            'latency_s': latency,
            'error': str(e)
        }


async def run_all() -> list[dict]:
    """Run all 10 snippets × 4 strategies."""

    tasks = []

    for snippet in snippets:
        for strategy_name in STRATEGIES:
            tasks.append(
                run_one(strategy_name, snippet)
            )

    results = await asyncio.gather(*tasks)

    return results


def score_accuracy(extracted: dict | None, gold: dict) -> int:
    """Compare the three fields and return 0, 1, 2, or 3."""

    if extracted is None:
        return 0

    score = 0

    fields = [
        'company',
        'role',
        'years_experience_required'
    ]

    for field in fields:

        predicted = extracted.get(field)
        expected = gold.get(field)

        if isinstance(predicted, str):
            predicted = predicted.strip().lower()

        if isinstance(expected, str):
            expected = expected.strip().lower()

        if predicted == expected:
            score += 1

    return score


async def score_llm_judge(
    snippet_text: str,
    extracted: dict | None,
    gold: dict
) -> int:
    """Use GPT-4o as a judge and return 1-4."""

    prompt = f"""
You are evaluating an information extraction result.

JOB DESCRIPTION:
{snippet_text}

GOLD ANSWER:
{json.dumps(gold, indent=2)}

MODEL ANSWER:
{json.dumps(extracted, indent=2)}

Score the model answer using this rubric:

4 — all three fields correct
3 — two of three fields correct, with no fabricated data
2 — one of three fields correct, or fabricated a field
1 — none correct or answer is unparsable

Return ONLY the integer score:
1, 2, 3, or 4.
"""

    response = await client.chat.completions.create(
        model=JUDGE_MODEL,
        messages=[
            {
                'role': 'user',
                'content': prompt
            }
        ],
        temperature=0.0
    )

    text = response.choices[0].message.content.strip()

    try:
        score = int(text)

        if score in [1, 2, 3, 4]:
            return score

    except ValueError:
        pass

    return 1


async def score_all(results: list[dict]) -> list[dict]:
    """Score all 40 results."""

    scored = []

    for result in results:

        gold = golden[result['snippet_id']]

        result['accuracy'] = score_accuracy(
            result['extracted'],
            gold
        )

        result['parse_success'] = int(
            result['extracted'] is not None
        )

        snippet_text = next(
            snippet['snippet']
            for snippet in snippets
            if snippet['id'] == result['snippet_id']
        )

        result['llm_judge_score'] = await score_llm_judge(
            snippet_text,
            result['extracted'],
            gold
        )

        scored.append(result)

    return scored


async def main():

    print()
    print('Running 40 LLM calls...')

    results = await run_all()

    print(f'Got {len(results)} results.')

    print()
    print('Scoring results...')

    scored = await score_all(results)

    print(f'Scored {len(scored)} results.')

    df = pd.DataFrame(scored)

    summary = df.groupby('strategy').agg({
        'accuracy': 'mean',
        'parse_success': 'mean',
        'llm_judge_score': 'mean',
        'cost_usd': 'sum',
        'latency_s': 'median',
    }).round(3)

    summary.columns = [
        'Accuracy (mean of 3)',
        'Parse rate',
        'Judge score',
        'Total cost ($)',
        'Latency p50 (s)'
    ]

    print()
    print('Comparison Table:')
    print(summary)

    print()
    print('Sample Result:')
    print(
        json.dumps(
            scored[0],
            indent=2
        )
    )


if __name__ == '__main__':
    asyncio.run(main())