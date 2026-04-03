from src.llm.graph import app


initial_state = {
    "chapter_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbba",
    "sequence": 1,
    "max_sequence": 5,
    "mode": "teacher",
}
app.invoke(initial_state)
