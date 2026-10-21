"""
End-to-end test script for the AI Research Agent.
Tests all 6 scenarios from the spec without the interactive CLI.
"""
import sys
import os

# Ensure we're running from the project root
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Fix Windows encoding for console output
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from app.graph.graph_builder import app
from app.tools.retriever import has_pdf_collection


def run_query(query, conversation_history=""):
    """Run a single query through the graph and return the result."""
    result = app.invoke(
        {
            "query": query,
            "plan": "",
            "search_results": [],
            "sources": [],
            "documents": [],
            "draft_summary": "",
            "conversation_history": conversation_history,
            "intent": "",
            "pdf_relevant": False,
        }
    )
    return result


def print_separator():
    print("\n" + "=" * 70 + "\n")


def check(condition, label):
    """Print PASS/FAIL for a test condition."""
    status = "[PASS]" if condition else "[FAIL]"
    print(f"  {status}  {label}")
    return condition


def test_all():
    print("=" * 70)
    print("  AI Research Agent -- End-to-End Test Suite")
    print("=" * 70)

    pdf_available = has_pdf_collection()
    print(f"\nPDF Collection Available: {pdf_available}")

    if not pdf_available:
        print("\n[WARNING] No PDF collection found. PDF tests will default to WEB_ONLY.")
        print("         This is EXPECTED behavior (hard rule: no PDF -> WEB_ONLY).")

    conversation_history = ""
    all_passed = True

    # -----------------------------------------------------------
    # TEST 1: PDF_ONLY query
    # -----------------------------------------------------------
    print_separator()
    print("TEST 1: Explain residual learning from the uploaded PDF")
    print("-" * 70)

    result = run_query(
        "Explain residual learning from the uploaded PDF",
        conversation_history=conversation_history,
    )

    intent = result.get("intent", "UNKNOWN")
    has_docs = len(result.get("documents", [])) > 0
    has_search = len(result.get("search_results", [])) > 0
    report_len = len(result.get("draft_summary", ""))

    print(f"\n  Intent:          {intent}")
    print(f"  PDF chunks:      {len(result.get('documents', []))}")
    print(f"  Web search done: {has_search}")
    print(f"  Report length:   {report_len} chars")

    if pdf_available:
        expected = "PDF_ONLY"
        pass_1 = intent == expected and not has_search
    else:
        expected = "WEB_ONLY"
        pass_1 = intent == expected

    print(f"  Expected intent: {expected}")
    print(f"  RESULT: {'PASS' if pass_1 else 'FAIL'}")

    if not pass_1:
        all_passed = False

    # Save history for follow-up tests
    conversation_history = result["conversation_history"]

    # Show first 200 chars of report
    print(f"\n  Report preview: {result['draft_summary'][:200]}...")

    # -----------------------------------------------------------
    # TEST 2: WEB_ONLY query
    # -----------------------------------------------------------
    print_separator()
    print("TEST 2: What is the latest research on residual learning?")
    print("-" * 70)

    result2 = run_query(
        "What is the latest research on residual learning?",
        conversation_history=conversation_history,
    )

    intent2 = result2.get("intent", "UNKNOWN")
    has_search2 = len(result2.get("search_results", [])) > 0
    report_len2 = len(result2.get("draft_summary", ""))

    print(f"\n  Intent:          {intent2}")
    print(f"  Web search done: {has_search2}")
    print(f"  Report length:   {report_len2} chars")

    expected2 = "WEB_ONLY"
    pass_2 = intent2 == expected2 and has_search2

    print(f"  Expected intent: {expected2}")
    print(f"  RESULT: {'PASS' if pass_2 else 'FAIL'}")

    if not pass_2:
        all_passed = False

    conversation_history = result2["conversation_history"]

    # -----------------------------------------------------------
    # TEST 3: PDF_AND_WEB query
    # -----------------------------------------------------------
    print_separator()
    print("TEST 3: Compare the uploaded PDF with the latest research on residual learning")
    print("-" * 70)

    result3 = run_query(
        "Compare the uploaded PDF with the latest research on residual learning",
        conversation_history=conversation_history,
    )

    intent3 = result3.get("intent", "UNKNOWN")
    has_docs3 = len(result3.get("documents", [])) > 0
    has_search3 = len(result3.get("search_results", [])) > 0
    report_len3 = len(result3.get("draft_summary", ""))

    print(f"\n  Intent:          {intent3}")
    print(f"  PDF chunks:      {len(result3.get('documents', []))}")
    print(f"  Web search done: {has_search3}")
    print(f"  Report length:   {report_len3} chars")

    if pdf_available:
        expected3 = "PDF_AND_WEB"
        pass_3 = intent3 == expected3 and has_search3
    else:
        expected3 = "WEB_ONLY"
        pass_3 = intent3 == expected3

    print(f"  Expected intent: {expected3}")
    print(f"  RESULT: {'PASS' if pass_3 else 'FAIL'}")

    if not pass_3:
        all_passed = False

    conversation_history = result3["conversation_history"]

    # -----------------------------------------------------------
    # TEST 4: Follow-up -- "Explain this simply"
    # -----------------------------------------------------------
    print_separator()
    print("TEST 4: Explain this simply (follow-up after PDF discussion)")
    print("-" * 70)

    # Reset history to simulate after TEST 1 (PDF discussion)
    followup_history = result["conversation_history"]

    result4 = run_query(
        "Explain this simply",
        conversation_history=followup_history,
    )

    intent4 = result4.get("intent", "UNKNOWN")
    report_len4 = len(result4.get("draft_summary", ""))

    print(f"\n  Intent:          {intent4}")
    print(f"  PDF chunks:      {len(result4.get('documents', []))}")
    print(f"  Report length:   {report_len4} chars")

    if pdf_available:
        expected4 = "PDF_ONLY"
        pass_4 = intent4 == expected4
    else:
        expected4 = "WEB_ONLY"
        pass_4 = intent4 == expected4

    print(f"  Expected intent: {expected4}")
    print(f"  RESULT: {'PASS' if pass_4 else 'FAIL'}")

    if not pass_4:
        all_passed = False

    # -----------------------------------------------------------
    # TEST 5: Follow-up -- "What is F(x)?"
    # -----------------------------------------------------------
    print_separator()
    print("TEST 5: What is F(x)? (follow-up after PDF discussion)")
    print("-" * 70)

    result5 = run_query(
        "What is F(x)?",
        conversation_history=followup_history,
    )

    intent5 = result5.get("intent", "UNKNOWN")
    report_len5 = len(result5.get("draft_summary", ""))

    print(f"\n  Intent:          {intent5}")
    print(f"  PDF chunks:      {len(result5.get('documents', []))}")
    print(f"  Report length:   {report_len5} chars")

    if pdf_available:
        expected5 = "PDF_ONLY"
        pass_5 = intent5 == expected5
    else:
        expected5 = "WEB_ONLY"
        pass_5 = intent5 == expected5

    print(f"  Expected intent: {expected5}")
    print(f"  RESULT: {'PASS' if pass_5 else 'FAIL'}")

    if not pass_5:
        all_passed = False

    # -----------------------------------------------------------
    # TEST 6: Fresh web query
    # -----------------------------------------------------------
    print_separator()
    print("TEST 6: What is transformer architecture? (fresh query, no PDF context)")
    print("-" * 70)

    result6 = run_query(
        "What is transformer architecture?",
        conversation_history="",  # Fresh -- no history
    )

    intent6 = result6.get("intent", "UNKNOWN")
    has_search6 = len(result6.get("search_results", [])) > 0
    report_len6 = len(result6.get("draft_summary", ""))

    print(f"\n  Intent:          {intent6}")
    print(f"  Web search done: {has_search6}")
    print(f"  Report length:   {report_len6} chars")

    # Basic check: we got a report
    pass_6 = report_len6 > 0
    print(f"  RESULT: {'PASS' if pass_6 else 'FAIL'}")

    if not pass_6:
        all_passed = False

    # -----------------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------------
    print_separator()
    print("TEST SUMMARY")
    print("-" * 70)
    results = [
        ("TEST 1: PDF_ONLY query", pass_1),
        ("TEST 2: WEB_ONLY query", pass_2),
        ("TEST 3: PDF_AND_WEB query", pass_3),
        ("TEST 4: Follow-up 'Explain this simply'", pass_4),
        ("TEST 5: Follow-up 'What is F(x)?'", pass_5),
        ("TEST 6: Fresh web query", pass_6),
    ]

    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status}  {name}")

    print()
    total = len(results)
    passed_count = sum(1 for _, p in results if p)
    print(f"  {passed_count}/{total} tests passed")

    if all_passed:
        print("\n  All tests PASSED!")
    else:
        print("\n  Some tests FAILED. Review the output above.")

    return all_passed


if __name__ == "__main__":
    try:
        success = test_all()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FATAL ERROR] Test suite crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)
