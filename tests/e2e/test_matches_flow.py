"""E2E: Fluxo de matches/propostas - 3 motoristas, aceitar uma, rejeitar outras."""
import requests
from .config import BASE_URL
from .helpers import create_user_and_token, auth_header, sample_frete_payload


def _criar_frete(shipper_token):
    r = requests.post(
        f"{BASE_URL}/fretes",
        json=sample_frete_payload(),
        headers=auth_header(shipper_token),
        timeout=10,
    )
    assert r.status_code in (200, 201), f"criar frete: {r.text}"
    return r.json()["id"]


def _fazer_proposta(driver_token, frete_id, valor=2400.00):
    payload = {"frete_id": frete_id, "valor_proposto": valor, "mensagem": "Posso fazer"}
    # tenta /matches primeiro, depois /propostas
    r = requests.post(
        f"{BASE_URL}/matches",
        json=payload,
        headers=auth_header(driver_token),
        timeout=10,
    )
    if r.status_code == 404:
        r = requests.post(
            f"{BASE_URL}/propostas",
            json=payload,
            headers=auth_header(driver_token),
            timeout=10,
        )
    return r


def test_fluxo_completo_matches():
    shipper_token, _ = create_user_and_token("shipper")
    frete_id = _criar_frete(shipper_token)

    # 3 motoristas fazem proposta
    drivers = [create_user_and_token("driver") for _ in range(3)]
    propostas = []
    for i, (dt, _) in enumerate(drivers):
        pr = _fazer_proposta(dt, frete_id, valor=2400 + i * 50)
        assert pr.status_code in (200, 201), f"proposta {i} falhou: {pr.status_code} {pr.text}"
        propostas.append(pr.json())

    # shipper lista todas as propostas
    lr = requests.get(
        f"{BASE_URL}/fretes/{frete_id}/matches",
        headers=auth_header(shipper_token),
        timeout=10,
    )
    if lr.status_code == 404:
        lr = requests.get(
            f"{BASE_URL}/matches?frete_id={frete_id}",
            headers=auth_header(shipper_token),
            timeout=10,
        )
    assert lr.status_code == 200, f"listar propostas falhou: {lr.text}"
    lista = lr.json()
    items = lista if isinstance(lista, list) else lista.get("items", lista.get("matches", []))
    assert len(items) >= 3, f"esperava 3 propostas, veio {len(items)}"

    # aceita a primeira
    proposta_id = propostas[0].get("id")
    ar = requests.post(
        f"{BASE_URL}/matches/{proposta_id}/accept",
        headers=auth_header(shipper_token),
        timeout=10,
    )
    if ar.status_code == 404:
        ar = requests.patch(
            f"{BASE_URL}/matches/{proposta_id}",
            json={"status": "accepted"},
            headers=auth_header(shipper_token),
            timeout=10,
        )
    assert ar.status_code in (200, 204), f"aceitar falhou: {ar.text}"

    # verifica outras foram rejeitadas
    lr2 = requests.get(
        f"{BASE_URL}/fretes/{frete_id}/matches",
        headers=auth_header(shipper_token),
        timeout=10,
    )
    if lr2.status_code == 404:
        lr2 = requests.get(
            f"{BASE_URL}/matches?frete_id={frete_id}",
            headers=auth_header(shipper_token),
            timeout=10,
        )
    data2 = lr2.json()
    items2 = data2 if isinstance(data2, list) else data2.get("items", data2.get("matches", []))
    accepted = [m for m in items2 if str(m.get("status", "")).lower() in ("accepted", "aceito", "aceita")]
    rejected = [m for m in items2 if str(m.get("status", "")).lower() in ("rejected", "rejeitado", "rejeitada", "recusado")]
    assert len(accepted) == 1, f"deveria ter 1 aceita, tem {len(accepted)}"
    assert len(rejected) >= 2, f"as outras 2 deveriam estar rejeitadas, tem {len(rejected)}"


if __name__ == "__main__":
    try:
        test_fluxo_completo_matches()
        print("PASS  test_fluxo_completo_matches")
    except Exception as e:
        print(f"FAIL  test_fluxo_completo_matches: {e}")
