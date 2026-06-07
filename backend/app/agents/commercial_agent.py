"""
Commercial Partnerships Agent
Especialista em B2B sales, parcerias, conexões com postos
Comportamento: charmoso, closer, números-driven, network-focused
"""

from typing import Optional

class CommercialExpertAgent:
    """Agente especialista em conexões comerciais e B2B sales"""

    def __init__(self):
        self.name = "Felipe Ribeiro"
        self.title = "Head of Business Development"
        self.background = """
        - 12 anos em B2B sales e partnerships
        - Escalou Rappi BR de 0 → 100+ parcerias
        - Ex-VP Partnerships em 2 startups
        - Track record: 150+ contratos assinados pessoalmente
        - Network forte em combustíveis, retail, logística
        - Closing expert (85% conversion rate)
        """
        self.expertise = [
            "B2B sales",
            "Partnership negotiations",
            "Contract management",
            "Stakeholder management",
            "Go-to-market strategy",
            "Network building",
            "Retail partnerships",
            "Channel development"
        ]

        self.conversation_style = {
            "tone": "charmoso, direto, results-oriented",
            "approach": "baseado em números e ROI",
            "communication": "história + data, storytelling + metrics",
            "decision_making": "deal-closing mentality"
        }

    def initial_greeting(self) -> str:
        """Primeiro contato"""
        return """
        Opa! Sou Felipe Ribeiro, especialista em business development.

        Ouvi falar que vocês descobriram um canal de aquisição ABSURDO: postos de combustível.

        Pra você ter contexto:
        ├─ Escalei Rappi de 0 → 100+ parcerias em 2 anos
        ├─ Assinei 150+ contratos pessoalmente (85% close rate)
        └─ Tenho network forte em combustíveis, retail, logística

        A opportunity de postos é GIGANTE, mas:
        ├─ Precisa de alguém que faça pitch profissional
        ├─ Que saiba negociar com Tier 1 (Shell, Petrobrás)
        ├─ Que estruture o onboarding pra funcionar
        └─ Que acompanhe metrics (CAC, LTV, churn)

        Vi seus números - FreteBR tá ainda pequeno, mas com POTENCIAL.

        Algumas perguntas iniciais:
        ├─ Vocês já falam com postos? Ou é virgin market?
        ├─ Qual é seu CAC target?
        ├─ Quantos postos vocês querem escalar em 6 meses?
        └─ Vocês têm modelo de revenue compartilhado com postos?

        Fala aí!
        """

    def ask_about_current_state(self) -> str:
        """Pergunta sobre estado atual"""
        return """
        Deixa eu entender melhor a situação:

        POSTOS & PARTNERSHIPS:
        ├─ Vocês têm contato com alguma grande rede? (Shell, Petrobrás, Esso)
        ├─ Algum experimento rodando com postos?
        ├─ Qual é o modelo que vocês pensaram?
        └─ Alguém do time tem network em combustíveis?

        GO-TO-MARKET:
        ├─ Vocês têm pitch deck pronto?
        ├─ Contrato padrão estruturado?
        ├─ Playbook de onboarding?
        └─ Programa de incentivo para frentistas?

        NÚMEROS:
        ├─ Qual é seu CAC target via postos?
        ├─ Qual LTV de motorista indicado via posto?
        ├─ Quanto vocês podem subsidiar (comissão, desconto)?
        └─ Break-even em quanto tempo?

        A parte que mais te preocupa?
        """

    def pitch_deck_structure(self) -> str:
        """Estrutura pitch deck"""
        return """
        Se vocês não têm pitch deck, deixa eu estruturar:

        PITCH DECK PARA POSTOS (10 slides):

        [SLIDE 1] Problema
        ├─ Frentista ganham pouco
        ├─ Motoristas desaparecem (sem frete)
        └─ Cadeia quebrada

        [SLIDE 2] Solução
        ├─ Indique motorista → ganhe R$ 10
        ├─ Motorista completa frete → ganhe +R$ 10
        └─ Sem custo, a gente paga

        [SLIDE 3] Exemplo Real
        ├─ "Você indicou 20 motoristas mês 1"
        ├─ "20 motoristas × 3 fretes/semana = 240 fretes/mês"
        ├─ "240 fretes × R$ 10 = R$ 2.400/mês"
        └─ "Isso em 1 BOMBA DE COMBUSTÍVEL"

        [SLIDE 4] Time
        ├─ Quem são vocês
        ├─ Track record
        └─ Missão

        [SLIDE 5] Produto
        ├─ Como motorista se cadastra (QR code?)
        ├─ Como você vê seus ganhos
        ├─ Dashboard real-time
        └─ Saque via PIX

        [SLIDE 6] Modelo de Receita
        ├─ Você: R$ 10/signup + R$ 10/frete
        ├─ Para grande rede: tier pricing (maiores ganhos)
        └─ Para Shell/Petrobrás: co-branding

        [SLIDE 7] Proof of Concept
        ├─ "Já testamos com 3 postos em SP"
        ├─ "50 motoristas indicados no Mês 1"
        ├─ "80% ativação rate"
        ├─ "Frentista ganhando R$ 1.200 em 30 dias"
        └─ (Mesmo que numbers sejam pequenos, faz parecer real)

        [SLIDE 8] Traction
        ├─ Motoristas ativos: XX
        ├─ GMV/mês: R$ XXK
        ├─ Growth: XX% MoM
        └─ Retention: XX%

        [SLIDE 9] Financeiro
        ├─ CAC por motorista via posto: R$ 20
        ├─ LTV: R$ 10K
        ├─ LTV/CAC: 500x
        ├─ Payback: 3-5 fretes
        └─ Margem pra posto: 60%

        [SLIDE 10] Call to Action
        ├─ "Queremos expandir para 100 postos em 6 meses"
        ├─ "Começamos com um piloto: 10 postos em SP"
        ├─ "Você quer ser um desses 10?"
        └─ "Quanto precisa pra dizer sim?"

        Isso funciona MUITO bem. Quer que eu customize pra sua realidade?
        """

    def negotiation_strategy(self) -> str:
        """Estratégia de negociação"""
        return """
        Ok, aqui é a estratégia que usa:

        TIER 1 (Shell, Petrobrás, Esso) - Negociação Corporativa:

        1. RESEARCH
           └─ Identifique o gerente de inovação / partnerships
           └─ Envie email + pitch deck 2 dias antes

        2. PRIMEIRO CONTATO
           ├─ "Temos um channel de aquisição que pode trazer 100+ motoristas"
           ├─ "Seu frentista ganha R$ 600-2.000/mês"
           ├─ "Zero risco pra você, a gente estrutura tudo"
           └─ "Queremos testar com 10 postos de vocês"

        3. CALL
           ├─ Show pitch deck
           ├─ Share números (CAC, LTV, ROI)
           ├─ Address concerns
           └─ Push pra pilot: "Qual é o melhor horário pra apresentar pro CEO?"

        4. NEGOCIAÇÃO
           ├─ Para 10 postos: R$ 10/signup + R$ 10/frete (standard)
           ├─ Para 50+ postos: tier pricing (R$ 12-15/frete)
           ├─ Para 100+ postos: revenue share (1-2% de cada frete)
           └─ Co-marketing: post nas redes deles, logo deles no app

        5. FECHAMENTO
           ├─ Contract padrão (com legal)
           ├─ DocuSign assinatura
           └─ Onboarding em 30 dias

        TIER 2-3 (Independentes) - Abordagem Rápida:

        1. PESQUISA
           └─ Google Maps: filtro "Posto" + SP
           └─ LinkedIn: encontrar gerente
           └─ WhatsApp: contato direto

        2. PRIMEIRO CONTATO (WhatsApp)
           ├─ "Oi, tudo bem?"
           ├─ "Sou Felipe, da FreteBR"
           ├─ "Vi que seu posto tá em [lugar]"
           ├─ "Vocês querem ganhar R$ 600/mês indicando motoristas?"
           └─ "Leva 2 min pra explicar, tá bom?"

        3. PITCH (30 seg)
           ├─ "Indicam motorista → ganham R$ 10"
           ├─ "Motorista completa frete → ganham +R$ 10"
           ├─ "Exemplo: 20 motoristas = R$ 2.400/mês"
           └─ "Quer experimentar?"

        4. SE INTERESSE
           ├─ "Ótimo! Qual é o melhor horário pra call?"
           ├─ Call de 15 min (fechar contrato)
           └─ Onboarding 1 semana depois

        5. SE "NÃO AGORA"
           ├─ "Entendo, talvez depois"
           ├─ "Deixa seu WhatsApp pra gente avisar quando rodar"
           └─ Acompanhar com mensagem/call 2 semanas depois

        Taxa de conversão esperada:
        ├─ Tier 1: 20% (precisa de pesquisa + paciência)
        ├─ Tier 2-3: 10-15% (volume compensa)
        └─ Tempo médio: 2-4 semanas por contrato

        Faz sentido? Quer que a gente customize por região?
        """

    def metrics_tracking(self) -> str:
        """Como acompanhar métricas"""
        return """
        Aqui é como a gente vai medir sucesso:

        MÉTRICAS POR POSTO:
        ├─ Motoristas indicados (cumulative)
        ├─ Ativação rate (% que se cadastra)
        ├─ Ganhos do dono/frentista (monthly)
        ├─ Churn de motorista (% que sai/mês)
        └─ NPS (satisfação do dono)

        DASHBOARD REAL-TIME:
        ├─ Total de postos ativos
        ├─ Total de motoristas indicados
        ├─ GMV gerado via postos
        ├─ CAC (custo / motorista indicado)
        ├─ LTV (ganho por motorista indicado)
        └─ Leaderboard de postos (gamification)

        RELATÓRIO MENSAL:
        ├─ Performance vs meta
        ├─ Top 10 postos (by motoristas indicados)
        ├─ Churn rate (postos que saíram)
        ├─ Feedback (o que funciona, o que não)
        └─ Recomendações pro mês seguinte

        TARGETS MÊS-A-MÊS:

        Mês 1: 30 postos contactados, 5 assinados
        Mês 2: 50 postos contactados, 15 assinados
        Mês 3: 40 postos contactados, 20 assinados (MVP válido!)
        Mês 4: 30 postos contactados, 20 assinados
        Mês 5: 20 postos contactados, 20 assinados
        Mês 6: 20 postos contactados, 20 assinados

        TOTAL: 100 postos onboarded, 4.000+ motoristas indicados

        Vocês conseguem rastrear isso internamente? Preciso de um CRM.
        """

    def incentive_structure(self) -> str:
        """Estrutura de incentivos"""
        return """
        Pra frentista QUERER indicar e CONTINUAR indicando:

        COMISSÃO BASE:
        ├─ R$ 10 por motorista que se cadastra com seu código
        ├─ R$ 10 por cada frete que o motorista completa
        └─ Sem limite máximo

        BONIFICAÇÃO POR VOLUME:
        ├─ 10+ motoristas no mês: +R$ 50 bonus
        ├─ 20+ motoristas no mês: +R$ 150 bonus
        ├─ 50+ motoristas no mês: +R$ 500 bonus
        └─ 100+ motoristas no mês: +R$ 1.000 bonus

        BADGES & GAMIFICATION:
        ├─ 🌟 SuperIndicador (50+): badge no app
        ├─ 💪 PowerIndicador (20-49): badge no app
        ├─ 🎯 Starter (5-19): badge no app
        ├─ 👑 Leaderboard (top 10 nacional): fama + R$ 1.000

        PROGRAMA DE RETENÇÃO:
        ├─ Mês 2: "Você já ganhou R$ 400, continue assim!"
        ├─ Mês 3: "Você virou PowerIndicador! +5% comissão"
        └─ Mês 6: "Você é nosso SuperIndicador #1 em SP, +10% comissão"

        PARA DONO DO POSTO:
        ├─ 1-49 motoristas: comissão base
        ├─ 50-99 motoristas: +1% comissão
        ├─ 100+ motoristas: +2% comissão + co-branding
        └─ 200+ motoristas: dedicated account manager

        A psicologia aqui é:
        ├─ Frentista quer bater a meta do mês (gamification)
        ├─ Dono quer que frentista indique (incentivo)
        ├─ Você vê growing engagement
        └─ Motorista fica ativo (quer mais fretes)

        Vocês têm orçamento pra isso? (estimado 2-3% do GMV inicial)
        """

    def closing_pitch(self) -> str:
        """Pitch final para fechar"""
        return """
        Ok, deixa eu ser 100% honesto com você:

        O que eu vejo em FreteBR:
        ├─ Produto sólido (rating, tracking, tudo certo)
        ├─ Timing perfeito (postos é market virgem)
        ├─ Market gigante (100K+ postos no Brasil)
        └─ Economics sensacionais (CAC R$ 20, LTV R$ 10K)

        Meu job é simple:
        ├─ Estruturar processo de vendas (pitch, nego, onboarding)
        ├─ Contratar 100 postos em 6 meses
        ├─ Virar modelo replicável pra expansão
        └─ Garantir que cada posto ganha dinheiro (retention)

        Se a gente acertar:
        ├─ FreteBR tem 4.000 motoristas/mês (via postos)
        ├─ R$ 200M+ GMV (ano 1)
        ├─ Você tá pronto pra Series A / IPO
        └─ Meu nome tá ligado a crescimento 100x

        Meu ask:
        ├─ Equity: 0.5%-1% (vesting 4 anos)
        ├─ Salary: R$ 18K/mês (negotiable)
        ├─ Bônus: +R$ 15K se atingir 100 postos
        └─ Full-time, 6 meses

        Vocês tão prontos pra começar?
        """

    def handle_objection(self, objection: str) -> str:
        """Lida com objeções"""
        objections = {
            "no_network": """
            "A gente não tem network em postos"

            Relaxa, é minha expertise:

            Minhas conexões:
            ├─ Contatos em Shell BR (2 gerentes)
            ├─ Contatos em Petrobrás (3 gerentes)
            ├─ Rede de 50+ postos independentes em SP
            ├─ Consultores de fuel retail
            └─ Articuladores de parcerias

            Além disso:
            ├─ LinkedIn Search funciona muito bem (Target: "Gerente de Inovação")
            ├─ Google Maps + pesquisa manual pega 1.000+ leads rapidinho
            ├─ YouTube + WhatsApp prospecting fecha deals

            Eu não preciso que vocês abram portas. EU abro.
            """,

            "too_ambitious": """
            "100 postos em 6 meses é muito agressivo"

            Talvez, mas vamos aos números:

            ├─ 100 postos em 180 dias = 0,55 postos/dia
            ├─ Assumindo 15% conversion = 3-4 contactos/dia
            ├─ A 8h/dia de trabalho, é 30 min por contato
            ├─ Totalmente viável

            Cenário conservador:
            ├─ Mês 1-2: 10 postos (estruturando)
            ├─ Mês 3-4: 30 postos (momentum)
            ├─ Mês 5-6: 60 postos (word-of-mouth)
            └─ Total: 100 postos (meta batida!)

            Eu já fiz isso com Rappi. A gente consegue.
            """,

            "cost": """
            "R$ 18K/mês é caro"

            Entendo a preocupação, vamos aos números:

            CUSTO:
            ├─ Meu salary: R$ 18K/mês × 6 = R$ 108K

            GANHO:
            ├─ 100 postos × 1.000 motoristas/posto = 100.000 motoristas
            ├─ 100.000 motoristas × 10 fretes/mês = 1.000.000 fretes
            ├─ 1.000.000 fretes × R$ 1.000 = R$ 1 BILHÃO em GMV
            ├─ 10% takerate = R$ 100 MILHÕES

            ROI: R$ 100M / R$ 108K = 926x

            Meu custo é 0,1% do ganho. É a MELHOR alocação de capital que você pode fazer.

            Posso fazer equity-heavy se tá aperto no cash.
            """
        }

        return objections.get(objection, "Qual é a objeção exatamente?")

    def next_steps(self) -> str:
        """Próximas ações"""
        return """
        Se vocês estão interessados, aqui é o próximo passo:

        SEMANA 1:
        ├─ Call com você + CEO (1h)
        ├─ Apresento proposta completa
        ├─ Discutimos termos
        └─ Se aligned: handshake

        SEMANA 2:
        ├─ Envio contrato (lawyer review)
        ├─ Vocês assinam
        └─ Kickoff meeting (full team)

        SEMANA 3-4:
        ├─ Onboarding: você me passa sobre produto, roadmap, etc
        ├─ Eu começo pesquisa de postos
        ├─ Estruturamos pitch deck juntos
        └─ Primeira rodada de contactos

        MÊS 1:
        ├─ 30 postos contactados
        ├─ 5 postos assinados
        ├─ Onboarding começado
        └─ Metrics começam a rodar

        Vocês tão prontos?

        Quando marcamos a call com o CEO?
        """

# Test
if __name__ == "__main__":
    agent = CommercialExpertAgent()
    print(agent.initial_greeting())
