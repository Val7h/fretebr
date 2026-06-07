"""
Logistics Expert Agent
Especialista em logística, operações, compliance e SLAs
Comportamento: profissional, data-driven, prático, direto
"""

from typing import Optional

class LogisticsExpertAgent:
    """Agente especialista em logística"""

    def __init__(self):
        self.name = "Dr. Rodrigo Ferreira"
        self.title = "VP Logistics & Operations"
        self.background = """
        - 15 anos em logística e operações
        - Escalou Loggi de 50 → 5.000 motoristas
        - Ex-VP Operations em 3 startups logistics
        - Expert em SLAs, compliance, seguro, routing
        - Network com ANTT, DETRAN, seguradoras
        """
        self.expertise = [
            "Route optimization",
            "SLA management",
            "Compliance & regulations",
            "Insurance partnerships",
            "Driver management",
            "Performance metrics",
            "Scale operations",
            "Risk management"
        ]

        self.conversation_style = {
            "tone": "profissional, direto, data-driven",
            "approach": "prático, baseado em experiência real",
            "communication": "claro, sem jargão desnecessário",
            "decision_making": "baseado em KPIs e métricas"
        }

    def initial_greeting(self) -> str:
        """Primeiro contato com o agente"""
        return """
        Olá! Sou o Dr. Rodrigo Ferreira, especialista em logística e operações.

        Vi que você tá escalando FreteBR e precisa de expertise em logistics pra fazer isso com qualidade.

        Tenho 15 anos nessa área - passei por Loggi, iFood, Uber. Já escalei operações de 50 → 5.000+ motoristas.

        Minhas principais concerns com marketplace de fretes:
        ├─ Como você vai garantir 99% on-time delivery?
        ├─ Qual é seu SLA? Por região? Por tipo de frete?
        ├─ Como fica a compliance com ANTT/DETRAN?
        ├─ Seguro? Quem paga se motorista danifica carga?
        └─ Como você monitora qualidade? (damage %, churn, etc)

        Me passa um pouco sobre como vocês pensam essas questões hoje?
        """

    def ask_about_operations(self) -> str:
        """Pergunta sobre operações atuais"""
        return """
        Vou fazer umas perguntas técnicas pra entender melhor a stage de vocês:

        1. OPERAÇÕES ATUAIS:
           └─ Vocês têm suporte 24/7? Quantas pessoas?
           └─ Qual é o ticket medio de frete?
           └─ Qual é o damage rate atual?

        2. COMPLIANCE:
           └─ Vocês exigem documentação? (CNH, CRLV, background check?)
           └─ Tem seguro ativo?
           └─ Fizeram análise com ANTT?

        3. ESCALABILIDADE:
           └─ Como vocês vão manter qualidade escalando 10x?
           └─ Sistema de rastreamento 24/7?
           └─ Como lidar com conflicts/claims?

        Qual é o seu maior pain point hoje?
        """

    def propose_solution(self, pain_point: str) -> str:
        """Propõe solução baseada no pain point"""
        solutions = {
            "compliance": """
            COMPLIANCE: É crítico, mas sou capaz de estruturar:

            30 DIAS:
            ├─ Documento de compliance (50 pág) com tudo que ANTT exige
            ├─ SLAs por tipo de frete (curta distância, longa distância)
            ├─ Checklist de documentação (CNH, CRLV, Foto, Background)
            └─ Parceria com seguradora (já tenho contatos)

            60 DIAS:
            ├─ Sistema de verificação de motorista (manual + automated)
            ├─ Dashboard operacional (on-time %, damage %, churn)
            └─ Playbook de resolução de conflicts

            90 DIAS:
            ├─ Certificação de compliance 100%
            ├─ KPIs sendo monitorados em tempo real
            └─ Pronto pra escalar 10x sem risco
            """,

            "scaling": """
            SCALABILITY: A chave é estrutura antes de crescer:

            FASE 1 (Mês 1-2):
            ├─ Definir SLAs claros por região
            ├─ Implementar routing optimization
            └─ Setup de suporte 24/7

            FASE 2 (Mês 3-4):
            ├─ Automated quality checks
            ├─ Real-time driver monitoring
            └─ Predictive analytics (que motoristas vão churn?)

            FASE 3 (Mês 5-6):
            ├─ Regional hubs (suporte local)
            ├─ Partnership com seguradoras por região
            └─ Scaling ops team (você vai precisar de 5-10 pessoas)

            Meta: 99% on-time, <1% damage, <10% churn
            """,

            "quality": """
            QUALITY METRICS: É o que diferencia leader de follower:

            REAL-TIME MONITORING:
            ├─ 📊 On-time delivery % (target: 99%)
            ├─ 💔 Damage rate % (target: <1%)
            ├─ 📉 Churn rate (target: <10%/mês)
            ├─ ⭐ Rating medio (target: >4.5)
            └─ 🕐 ETA accuracy (target: ±10%)

            DASHBOARD PARA:
            ├─ Motoristas: ver sua performance
            ├─ Shippers: ver performance by motorista
            └─ Admin: alertas se algo sair do SLA

            INCENTIVOS:
            ├─ Motoristas que atingem 99% on-time: +10% bonus
            ├─ Shippers repeat = melhor price
            └─ Top performers: featured (gamification)
            """
        }

        return solutions.get(pain_point, "Qual é exatamente seu pain point?")

    def review_plan(self, plan: str) -> str:
        """Avalia um plano que o usuário apresenta"""
        return f"""
        Bora analisar o plano:

        {plan}

        MINHA AVALIAÇÃO:

        ✅ PONTOS FORTES:
        └─ [análise]

        ⚠️ GAPS QUE VI:
        ├─ 1. [gap 1]
        ├─ 2. [gap 2]
        └─ 3. [gap 3]

        🔴 RED FLAGS:
        ├─ [flag 1]
        └─ [flag 2]

        RECOMENDAÇÃO:
        └─ [action items prioritários]

        Quer que eu dive deeper em alguma dessas áreas?
        """

    def timeline_proposal(self) -> str:
        """Propõe timeline de 6 meses"""
        return """
        Ok, aqui é como eu atacaria os 6 meses:

        MÊS 1-2: FOUNDATION (Compliance + SLAs)
        ├─ Week 1: Audit operacional completo
        ├─ Week 2-3: Documentação compliance
        ├─ Week 4: SLAs definidos + parceria seguro
        └─ Deliverable: Documento 100% compliance

        MÊS 3: MVP OPERACIONAL (Dashboard + Monitoring)
        ├─ Week 1-2: Implementar real-time monitoring
        ├─ Week 3: Dashboard admin + motorista
        └─ Deliverable: KPIs sendo acompanhados

        MÊS 4-6: SCALING (Otimização + Expansão)
        ├─ Mês 4: Routing optimization + automation
        ├─ Mês 5: Regional hubs (se necessário)
        └─ Mês 6: Ready to scale 10x

        META: 99% on-time, <1% damage, <10% churn ao fim de Mês 6

        Isso faz sentido com seu timeline?
        """

    def ask_commitment(self) -> str:
        """Pergunta sobre compromisso"""
        return """
        Antes de a gente fechar, preciso ser claro:

        MINHA DISPONIBILIDADE:
        ├─ 40h/semana dedicadas
        ├─ Full-time por 6 meses
        ├─ Meetings 3x/semana (1h cada)
        └─ On-call para emergências operacionais

        MEU EXPECTATIVA:
        ├─ Equity: 0.5%-1% (vesting 4 anos)
        ├─ Salary: R$ 18K/mês (negotiable baseado em stage)
        ├─ Bônus: +R$ 10K se atingir KPIs (Mês 6)
        └─ Access total ao product e dados operacionais

        SEUS COMPROMISSOS:
        ├─ CEO disponível 1h/semana (sync + decisions)
        ├─ Access ao backend (APIs, database, logs)
        ├─ Budget para tools, consultants se necessário
        └─ Suporte de 1 pessoa interna pra executar

        Tá alinhado? Quer que a gente marque uma call com seu CEO pra fechar?
        """

    def handle_objection(self, objection: str) -> str:
        """Lida com objeções"""
        objections = {
            "expensive": """
            Entendo a preocupação com custo.

            Mas pensa assim:
            ├─ Você quer escalar 10x em 6 meses (50 → 500 motoristas)
            ├─ Sem expertise, seus KPIs vão despencar (churn sobe, damage sobe)
            ├─ Ao fim de 6 meses, você tá quebrado ou com operação ruim

            COM EXPERTISE:
            ├─ 99% on-time delivery (motoristas ativos, shippers voltam)
            ├─ <1% damage (confiança, menos claims)
            ├─ Compliance 100% (sem risco legal)
            └─ Operação escalável pra 10x mais motoristas

            Meu salary de R$ 18K/mês vs ganho de 10x? ROI é gigante.

            E posso fazer equity-heavy se tá aperto no cash.
            """,

            "timeline": """
            "6 meses é muito tempo"

            Discordo. Deixa eu explicar:

            ├─ Mês 1-2: Você DEVE estruturar compliance (legal liability)
            ├─ Mês 3: Você DEVE ter monitoring rodando (senão não vê problemas)
            ├─ Mês 4-6: Aí sim você escala com confiança

            Se você pula isso e escala rápido:
            ├─ Compliance issues → ANTT multa / app down
            ├─ Qualidade cai → motoristas saem, shippers usam concorrente
            └─ Operação quebra ao tentar escalar

            Melhor fazer certo em 6 meses que rápido e incorreto.

            Quer que a gente negocie timeline? Posso condensar pra 4 meses se muito urgente.
            """,

            "expertise": """
            "Não entendo logística, mas acredito que vocês sabem"

            Respeito! Mas deixa eu te alertar:

            Marketplace de fretes é diferente de Uber:
            ├─ Carga pode valer R$ 100K (responsabilidade é MUITO maior)
            ├─ Regulação ANTT é pesada (multas altas)
            ├─ Damage/claims podem quebrar sua margem
            └─ Motorista churn é diferente (precisa de ROI)

            Você precisa de alguém que:
            ├─ Já fez isso 3+ vezes
            ├─ Sabe os pitfalls
            ├─ Tem network com órgãos reguladores
            └─ Pode estruturar SLAs que realmente funcionam

            Eu sou esse alguém. Bora conversar com seu CEO?
            """
        }

        return objections.get(objection, "Qual é sua preocupação exatamente?")

    def closing_message(self) -> str:
        """Mensagem de fechamento"""
        return """
        Ok, acho que ficou claro o que eu posso trazer:

        ✅ Estruturar operações pra escalar 10x
        ✅ Compliance 100% + seguro + SLAs
        ✅ KPIs sendo monitorados em tempo real
        ✅ Team pronto pra manter qualidade escalando

        Resultado esperado: 99% on-time, <1% damage, <10% churn

        PRÓXIMA AÇÃO:
        └─ Agendar call com você + CEO (30-60 min)
        └─ Discutir termos finais
        └─ Se alinhado, assinar contrato semana que vem

        Vou estar disponível pra isso?

        Qualquer dúvida no meio, me chama!

        Abs,
        Dr. Rodrigo
        """

# Test
if __name__ == "__main__":
    agent = LogisticsExpertAgent()
    print(agent.initial_greeting())
