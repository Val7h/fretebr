import pytest
from uuid import uuid4
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models import User, Frete, Referral, Match
from app.database import get_db
from app.routes.referral import calculate_and_apply_referral_commission

client = TestClient(app)


@pytest.fixture
def test_motorista1(db: Session):
    """Criar primeiro motorista para testes"""
    motorista = User(
        id=uuid4(),
        email="motorista1@test.com",
        senha_hash="hashed",
        nome_completo="João Silva",
        tipo_usuario="motorista",
        is_active=True,
    )
    db.add(motorista)
    db.commit()
    db.refresh(motorista)
    return motorista


@pytest.fixture
def test_motorista2(db: Session):
    """Criar segundo motorista para testes"""
    motorista = User(
        id=uuid4(),
        email="motorista2@test.com",
        senha_hash="hashed",
        nome_completo="Maria Santos",
        tipo_usuario="motorista",
        is_active=True,
    )
    db.add(motorista)
    db.commit()
    db.refresh(motorista)
    return motorista


@pytest.fixture
def test_shipper(db: Session):
    """Criar shipper para criar fretes"""
    shipper = User(
        id=uuid4(),
        email="shipper@test.com",
        senha_hash="hashed",
        nome_completo="Empresa XYZ",
        tipo_usuario="shipper",
        is_active=True,
    )
    db.add(shipper)
    db.commit()
    db.refresh(shipper)
    return shipper


@pytest.fixture
def test_frete(test_shipper: User, db: Session):
    """Criar frete para testes"""
    frete = Frete(
        id=uuid4(),
        shipper_id=test_shipper.id,
        origem_endereco="São Paulo, SP",
        destino_endereco="Rio de Janeiro, RJ",
        valor_frete=Decimal("1000.00"),
        data_coleta="2026-06-10",
        descricao="Teste frete",
        status="disponivel",
    )
    db.add(frete)
    db.commit()
    db.refresh(frete)
    return frete


class TestReferralEndpoints:
    """Testes para endpoints de referência"""

    def test_indicate_motorista_success(
        self,
        test_motorista1: User,
        test_motorista2: User,
        test_frete: Frete,
        db: Session,
    ):
        """Teste indicação bem-sucedida"""
        # Setup: fazer login como motorista1
        # (em um teste real, você teria um token)

        referral = Referral(
            referrer_motorista_id=test_motorista1.id,
            referred_motorista_id=test_motorista2.id,
            frete_id=test_frete.id,
            status="pending",
        )
        db.add(referral)
        db.commit()

        # Validar que foi criado
        assert referral.id is not None
        assert referral.status == "pending"
        assert referral.comissao_valor == Decimal("0.00")

    def test_indicate_motorista_self_fail(
        self,
        test_motorista1: User,
        test_frete: Frete,
        db: Session,
    ):
        """Teste falha quando tenta indicar a si mesmo"""
        with pytest.raises(Exception):  # CheckConstraint violation
            referral = Referral(
                referrer_motorista_id=test_motorista1.id,
                referred_motorista_id=test_motorista1.id,
                frete_id=test_frete.id,
            )
            db.add(referral)
            db.commit()

    def test_get_earnings_empty(self, test_motorista1: User, db: Session):
        """Teste ganhos vazios para motorista novo"""
        earnings = (
            db.query(Referral)
            .filter(
                Referral.referrer_motorista_id == test_motorista1.id,
                Referral.status == "completed",
            )
            .all()
        )
        assert len(earnings) == 0

    def test_calculate_referral_commission(
        self,
        test_motorista1: User,
        test_motorista2: User,
        test_frete: Frete,
        test_shipper: User,
        db: Session,
    ):
        """Teste cálculo de comissão após frete completo"""

        # Criar referência
        referral = Referral(
            referrer_motorista_id=test_motorista1.id,
            referred_motorista_id=test_motorista2.id,
            frete_id=test_frete.id,
            status="pending",
        )
        db.add(referral)
        db.commit()

        # Criar match (frete aceito)
        match = Match(
            id=uuid4(),
            frete_id=test_frete.id,
            motorista_id=test_motorista2.id,
            status="em_transito",
        )
        db.add(match)
        db.commit()

        # Simular conclusão com comissão
        frete_comissao = Decimal("100.00")  # 10% de 1000
        calculate_and_apply_referral_commission(match.id, frete_comissao, db)

        # Validar resultado
        updated_referral = db.query(Referral).filter(Referral.id == referral.id).first()
        assert updated_referral.status == "completed"
        assert updated_referral.comissao_valor == Decimal(
            "20.00"
        )  # 20% de 100
        assert updated_referral.completed_at is not None

    def test_commission_boundaries(
        self,
        test_motorista1: User,
        test_motorista2: User,
        test_frete: Frete,
        db: Session,
    ):
        """Teste limites de comissão (min/max)"""

        # Criar referência
        referral = Referral(
            referrer_motorista_id=test_motorista1.id,
            referred_motorista_id=test_motorista2.id,
            frete_id=test_frete.id,
            status="pending",
        )
        db.add(referral)
        db.commit()

        # Match para teste
        match = Match(
            id=uuid4(),
            frete_id=test_frete.id,
            motorista_id=test_motorista2.id,
            status="em_transito",
        )
        db.add(match)
        db.commit()

        # Teste 1: Comissão muito pequena (deve ir para mín R$ 5)
        frete_comissao = Decimal("10.00")  # 20% = 2.00 < 5.00 mín
        calculate_and_apply_referral_commission(match.id, frete_comissao, db)

        referral_db = db.query(Referral).filter(Referral.id == referral.id).first()
        assert referral_db.comissao_valor >= Decimal("5.00")

        # Teste 2: Comissão muito grande (deve ir para máx R$ 100)
        referral.status = "pending"
        referral.comissao_valor = Decimal("0.00")
        db.commit()

        frete_comissao = Decimal("1000.00")  # 20% = 200.00 > 100.00 máx
        calculate_and_apply_referral_commission(match.id, frete_comissao, db)

        referral_db = db.query(Referral).filter(Referral.id == referral.id).first()
        assert referral_db.comissao_valor <= Decimal("100.00")


class TestReferralLogic:
    """Testes para lógica de negócio de referências"""

    def test_referral_status_flow(
        self,
        test_motorista1: User,
        test_motorista2: User,
        test_frete: Frete,
        db: Session,
    ):
        """Teste fluxo de status: pending -> completed"""

        referral = Referral(
            referrer_motorista_id=test_motorista1.id,
            referred_motorista_id=test_motorista2.id,
            frete_id=test_frete.id,
            status="pending",
        )
        db.add(referral)
        db.commit()

        # Validar status inicial
        assert referral.status == "pending"
        assert referral.completed_at is None

        # Simular conclusão
        referral.status = "completed"
        referral.comissao_valor = Decimal("50.00")
        from datetime import datetime

        referral.completed_at = datetime.utcnow()
        db.commit()

        # Validar mudança
        updated = db.query(Referral).filter(Referral.id == referral.id).first()
        assert updated.status == "completed"
        assert updated.completed_at is not None
        assert updated.comissao_valor == Decimal("50.00")

    def test_multiple_referrals_same_motorista(
        self,
        test_motorista1: User,
        test_motorista2: User,
        test_shipper: User,
        db: Session,
    ):
        """Teste múltiplas referências do mesmo motorista"""

        # Criar múltiplos fretes
        fretes = []
        for i in range(3):
            frete = Frete(
                id=uuid4(),
                shipper_id=test_shipper.id,
                origem_endereco="São Paulo, SP",
                destino_endereco="Rio de Janeiro, RJ",
                valor_frete=Decimal("1000.00"),
                data_coleta="2026-06-10",
                descricao=f"Frete {i}",
                status="disponivel",
            )
            db.add(frete)
            fretes.append(frete)

        db.commit()

        # Criar 3 referências
        for frete in fretes:
            referral = Referral(
                referrer_motorista_id=test_motorista1.id,
                referred_motorista_id=test_motorista2.id,
                frete_id=frete.id,
                status="pending",
            )
            db.add(referral)

        db.commit()

        # Validar contagem
        referrals = db.query(Referral).filter(
            Referral.referrer_motorista_id == test_motorista1.id
        ).all()
        assert len(referrals) == 3
