from app.domain.entities import Chunk, Course
from app.services.generation.rag_retriever import RAGRetriever


def test_rag_retriever_is_deterministic_for_fixed_seed() -> None:
    chunks = [
        Chunk(doc_id="doc-1", page=1, span="a", text="Alpha"),
        Chunk(doc_id="doc-2", page=2, span="b", text="Beta"),
        Chunk(doc_id="doc-3", page=3, span="c", text="Gamma"),
        Chunk(doc_id="doc-2", page=2, span="b", text="Beta"),
    ]
    retriever = RAGRetriever(chunk_source=lambda course: chunks)
    course = Course(id="course-1", org_id="org-1", title="Cardiology CE")

    first = retriever.retrieve(course=course, n=3, seed="seed-1")
    second = retriever.retrieve(course=course, n=3, seed="seed-1")
    third = retriever.retrieve(course=course, n=3, seed="seed-2")

    assert first == second
    assert len(first) == 3
    assert len({chunk for chunk in first}) == 3
    assert first != third


def test_rag_retriever_returns_empty_list_for_non_positive_n() -> None:
    retriever = RAGRetriever(chunk_source=lambda course: [])
    course = Course(id="course-1", org_id="org-1", title="Cardiology CE")

    assert retriever.retrieve(course=course, n=0, seed="seed-1") == []
