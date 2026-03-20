from summarise.chunker import chunk_text, merge_summary

def test_short_text_single_chunk():
    text = "Hello world"
    assert chunk_text(text) == [text]

def test_long_text_multiple_chunks():
    para = "A" * 5000
    text = "\n\n".join([para] * 10)
    chunks = chunk_text(text, max_chars=12000)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 12000

def test_merge_summary():
    summaries = ["Part 1 summary", "Part 2 summary"]
    merged = merge_summary(summaries)
    assert "Part 1 summary" in merged
    assert "Part 2 summary" in merged
    assert "---" in merged

def test_empty_text():
    assert chunk_text("") == [""]

def test_exact_limit():
    text = "A" * 24000
    assert chunk_text(text) == [text]