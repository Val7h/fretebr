"""E2E: Chat - só permite mensagens após match aceito."""
import requests
from .config import BASE_URL
from .helpers import create_user_and_token, auth_header, sample_frete_payload


def _setup_match(accept=True):
    shipper_token, _ = create_user_and_token("shipper")
    driver_token, _ = create_user_and_token("driver")

    fr = requests.post(
        f"{BASE_URL}/fretes",
        json=sample_frete_payload(),
        headers=auth_header(shipper_token),
        timeout=10,
    )
    assert fr.status_code in (200, 201)
    frete_id = fr.json()["id"]

    payload = {"frete_id": frete_id, "valor_proposto": 2400.0, "mensagem": "ok"}
    pr = requests.post(f"{BASE_URL}/matches", json=payload, headers=auth_header(driver_token), timeout=10)
    if pr.status_code == 404:
        pr = requests.post(f"{BASE_URL}/propostas", json=payload, headers=auth_header(driver_token), timeout=10)
    assert pr.status_code in (200, 201), f"proposta: {pr.text}"
    match_id = pr.json().get("id")

    if accept:
        ar = requests.post(
            f"{BASE_URL}/matches/{match_id}/accept",
            headers=auth_header(shipper_token),
            timeout=10,
        )
        if ar.status_code == 404:
            ar = requests.patch(
                f"{BASE_URL}/matches/{match_id}",
                json={"status": "accepted"},
                headers=auth_header(shipper_token),
                timeout=10,
            )
        assert ar.status_code in (200, 204), f"aceitar: {ar.text}"

    return shipper_token, driver_token, frete_id, match_id


def _send_msg(token, match_id, texto):
    # tenta /chat/{match_id}/messages, depois /messages
    r = requests.post(
        f"{BASE_URL}/chat/{match_id}/messages",
        json={"text": texto},
        headers=auth_header(token),
        timeout=10,
    )
    if r.status_code == 404:
        r = requests.post(
            f"{BASE_URL}/messages",
            json={"match_id": match_id, "text": texto},
            headers=auth_header(token),
            timeout=10,
        )
    return r


def _list_msgs(token, match_id):
    r = requests.get(
        f"{BASE_URL}/chat/{match_id}/messages",
        headers=auth_header(token),
        timeout=10,
    )
    if r.status_code == 404:
        r = requests.get(
            f"{BASE_URL}/messages?match_id={match_id}",
            headers=auth_header(token),
            timeout=10,
        )
    return r


def test_motorista_envia_e_shipper_responde():
    shipper_token, driver_token, _, match_id = _setup_match(accept=True)

    r1 = _send_msg(driver_token, match_id, "Oi, posso pegar agora")
    assert r1.status_code in (200, 201), f"driver envio: {r1.status_code} {r1.text}"

    r2 = _send_msg(shipper_token, match_id, "Beleza, te espero")
    assert r2.status_code in (200, 201), f"shipper envio: {r2.status_code} {r2.text}"


def test_lista_historico_chat():
    shipper_token, driver_token, _, match_id = _setup_match(accept=True)
    _send_msg(driver_token, match_id, "msg 1")
    _send_msg(shipper_token, match_id, "msg 2")
    _send_msg(driver_token, match_id, "msg 3")

    r = _list_msgs(shipper_token, match_id)
    assert r.status_code == 200, f"listar historico: {r.text}"
    data = r.json()
    items = data if isinstance(data, list) else data.get("items", data.get("messages", []))
    assert len(items) >= 3


def test_chat_bloqueado_se_match_nao_aceito():
    _, driver_token, _, match_id = _setup_match(accept=False)
    r = _send_msg(driver_token, match_id, "tentando antes do accept")
    assert r.status_code in (400, 401, 403, 409), (
        f"deveria bloquear msg sem match aceito, veio {r.status_code}"
    )


if __name__ == "__main__":
    for fn_name in [n for n in dir() if n.startswith("test_")]:
        try:
            globals()[fn_name]()
            print(f"PASS  {fn_name}")
        except Exception as e:
            print(f"FAIL  {fn_name}: {e}")
