"""E2E: Fluxo completo de fretes - criar, listar, ver, editar, deletar."""
import requests
from .config import BASE_URL
from .helpers import create_user_and_token, auth_header, sample_frete_payload


def _create_frete(token, **overrides):
    payload = sample_frete_payload(**overrides)
    r = requests.post(
        f"{BASE_URL}/fretes",
        json=payload,
        headers=auth_header(token),
        timeout=10,
    )
    return r, payload


def test_shipper_cria_frete():
    token, _ = create_user_and_token("shipper")
    r, payload = _create_frete(token)
    assert r.status_code in (200, 201), f"criar frete falhou: {r.text}"
    body = r.json()
    assert "id" in body
    assert body.get("origem") == payload["origem"]


def test_lista_publica_de_fretes():
    token, _ = create_user_and_token("shipper")
    _create_frete(token, origem="Curitiba, PR")
    r = requests.get(f"{BASE_URL}/fretes", timeout=10)
    assert r.status_code == 200, f"listagem pública falhou: {r.text}"
    data = r.json()
    items = data if isinstance(data, list) else data.get("items", data.get("fretes", []))
    assert len(items) >= 1


def test_motorista_ve_frete():
    shipper_token, _ = create_user_and_token("shipper")
    cr, _ = _create_frete(shipper_token)
    frete_id = cr.json()["id"]

    driver_token, _ = create_user_and_token("driver")
    r = requests.get(
        f"{BASE_URL}/fretes/{frete_id}",
        headers=auth_header(driver_token),
        timeout=10,
    )
    assert r.status_code == 200, f"motorista nao consegue ver frete: {r.text}"


def test_shipper_edita_frete():
    token, _ = create_user_and_token("shipper")
    cr, _ = _create_frete(token)
    frete_id = cr.json()["id"]

    r = requests.put(
        f"{BASE_URL}/fretes/{frete_id}",
        json={"valor_oferecido": 3000.00, "descricao": "atualizado"},
        headers=auth_header(token),
        timeout=10,
    )
    if r.status_code == 405:
        r = requests.patch(
            f"{BASE_URL}/fretes/{frete_id}",
            json={"valor_oferecido": 3000.00},
            headers=auth_header(token),
            timeout=10,
        )
    assert r.status_code in (200, 204), f"editar frete falhou: {r.status_code} {r.text}"


def test_shipper_deleta_frete():
    token, _ = create_user_and_token("shipper")
    cr, _ = _create_frete(token)
    frete_id = cr.json()["id"]

    r = requests.delete(
        f"{BASE_URL}/fretes/{frete_id}",
        headers=auth_header(token),
        timeout=10,
    )
    assert r.status_code in (200, 204), f"deletar frete falhou: {r.text}"

    check = requests.get(f"{BASE_URL}/fretes/{frete_id}", timeout=10)
    assert check.status_code in (404, 410), "frete deveria ter sido removido"


if __name__ == "__main__":
    for fn_name in [n for n in dir() if n.startswith("test_")]:
        try:
            globals()[fn_name]()
            print(f"PASS  {fn_name}")
        except Exception as e:
            print(f"FAIL  {fn_name}: {e}")
