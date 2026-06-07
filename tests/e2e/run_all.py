"""Runner E2E: executa todos os módulos de teste e gera relatório.

Uso:
    python -m tests.e2e.run_all
    # ou (após cd no diretório do projeto):
    python tests/e2e/run_all.py

Pré-requisito: backend rodando em http://localhost:8001
"""
import importlib
import sys
import time
import traceback
from pathlib import Path

# Garante que o pacote tests.e2e seja importável
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import requests  # noqa: E402
from tests.e2e.config import BASE_URL  # noqa: E402


TEST_MODULES = [
    "tests.e2e.test_auth",
    "tests.e2e.test_fretes_flow",
    "tests.e2e.test_matches_flow",
    "tests.e2e.test_chat",
    "tests.e2e.test_security",
]


def check_backend():
    try:
        r = requests.get(f"{BASE_URL}/", timeout=5)
        return r.status_code < 500
    except Exception:
        try:
            r = requests.get(f"{BASE_URL}/docs", timeout=5)
            return r.status_code < 500
        except Exception:
            return False


def run_module(mod_name):
    print(f"\n{'='*70}\nMÓDULO: {mod_name}\n{'='*70}")
    results = []
    try:
        mod = importlib.import_module(mod_name)
    except Exception as e:
        print(f"ERRO ao importar {mod_name}: {e}")
        return [(mod_name, "IMPORT_ERROR", str(e), 0.0)]

    test_fns = [name for name in dir(mod) if name.startswith("test_")]
    for fn_name in test_fns:
        fn = getattr(mod, fn_name)
        t0 = time.time()
        try:
            fn()
            dt = time.time() - t0
            print(f"  PASS  {fn_name}  ({dt:.2f}s)")
            results.append((fn_name, "PASS", "", dt))
        except AssertionError as e:
            dt = time.time() - t0
            print(f"  FAIL  {fn_name}  ({dt:.2f}s)\n        {e}")
            results.append((fn_name, "FAIL", str(e), dt))
        except Exception as e:
            dt = time.time() - t0
            tb = traceback.format_exc(limit=3)
            print(f"  ERRO  {fn_name}  ({dt:.2f}s)\n{tb}")
            results.append((fn_name, "ERROR", str(e), dt))
    return results


def main():
    print(f"FreteBR E2E Test Runner")
    print(f"Backend: {BASE_URL}")

    if not check_backend():
        print(f"\nERRO: backend nao respondeu em {BASE_URL}")
        print("Suba o backend antes de rodar: uvicorn backend.main:app --port 8001")
        sys.exit(2)
    print("Backend OK\n")

    all_results = []
    t_inicio = time.time()
    for mod in TEST_MODULES:
        all_results.extend([(mod, *r) for r in run_module(mod)])
    duracao = time.time() - t_inicio

    # Relatório
    total = len(all_results)
    passed = sum(1 for r in all_results if r[2] == "PASS")
    failed = sum(1 for r in all_results if r[2] == "FAIL")
    errored = sum(1 for r in all_results if r[2] in ("ERROR", "IMPORT_ERROR"))

    print(f"\n{'='*70}\nRELATÓRIO FINAL\n{'='*70}")
    print(f"Total:      {total}")
    print(f"PASS:       {passed}")
    print(f"FAIL:       {failed}")
    print(f"ERROR:      {errored}")
    print(f"Duração:    {duracao:.2f}s")
    print(f"Taxa:       {(passed/total*100) if total else 0:.1f}%")

    if failed or errored:
        print(f"\nFalhas:")
        for mod, fn, status, msg, dt in all_results:
            if status != "PASS":
                print(f"  [{status}] {mod}::{fn}")
                if msg:
                    print(f"           {msg[:200]}")

    # Salva relatório em arquivo
    report_path = Path(__file__).parent / "last_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"FreteBR E2E Report\nBackend: {BASE_URL}\nDuração: {duracao:.2f}s\n")
        f.write(f"Total={total} PASS={passed} FAIL={failed} ERROR={errored}\n\n")
        for mod, fn, status, msg, dt in all_results:
            f.write(f"[{status}] {mod}::{fn} ({dt:.2f}s) {msg}\n")
    print(f"\nRelatório salvo em: {report_path}")

    sys.exit(0 if (failed == 0 and errored == 0) else 1)


if __name__ == "__main__":
    main()
