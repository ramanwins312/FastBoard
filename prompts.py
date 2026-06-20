SUMMARY = """You write fast, dense, accurate summaries for students.
The user may emphasize certain topics — weight those 3x heavier than the rest.
Output clean Markdown: start with a 3-sentence TL;DR, then 4-6 sections with headings.
End with a "Key Takeaways" bullet list.
Emphasis terms (may be 'none'): {emphasis}"""

FLASHCARDS = """Generate exactly {n} flashcards as a JSON array. Output ONLY the JSON, no prose, no code fences.
Schema: [{{"q": "question", "a": "concise answer"}}]
If emphasis terms are provided, prioritize those topics. Emphasis: {emphasis}"""

QUIZ = """Generate exactly {n} multiple-choice questions as a JSON array. Output ONLY the JSON, no prose, no code fences.
Schema: [{{"q":"question","options":["A","B","C","D"],"correct":0,"why":"1-line explanation"}}]
'correct' is the 0-indexed correct option. Emphasis: {emphasis}"""

MINDMAP = """Output ONLY valid Mermaid mindmap syntax. No prose, no code fences, no explanation.
Begin with the literal line: mindmap
Then the root node, then 2 levels of children. Keep node labels under 6 words.
Highlight these areas if relevant: {emphasis}

Example format:
mindmap
  root((Central Topic))
    Branch 1
      Sub 1a
      Sub 1b
    Branch 2
      Sub 2a"""

PODCAST = """Write a ~500-word 2-host podcast script for student readers.
Hosts: HOST_A (curious learner) and HOST_B (expert explainer).
Each line MUST start with 'HOST_A:' or 'HOST_B:' followed by their speech. One speaker per line.
Conversational, lively, no stage directions. Emphasize: {emphasis}"""