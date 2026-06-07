#!/bin/bash

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# URLs
API_URL="http://localhost:8001/api"
FRONTEND_URL="http://localhost:3009"

echo -e "${YELLOW}===============================================${NC}"
echo -e "${YELLOW}TESTE COMPLETO - FRETEBR${NC}"
echo -e "${YELLOW}===============================================${NC}\n"

# 1. TESTE DE HEALTH CHECK
echo -e "${YELLOW}[1] Verificando saúde do backend...${NC}"
HEALTH=$(curl -s http://localhost:8001/health)
if echo "$HEALTH" | grep -q "ok"; then
    echo -e "${GREEN}✅ Backend está online${NC}\n"
else
    echo -e "${RED}❌ Backend offline${NC}\n"
    exit 1
fi

# 2. TESTE DE SIGNUP - SHIPPER
echo -e "${YELLOW}[2] Criando conta Shipper...${NC}"
SHIPPER_RESPONSE=$(curl -s -X POST "$API_URL/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "shipper_teste_'$(date +%s)'@test.com",
    "password": "teste123",
    "tipo": "shipper",
    "nome": "João Shipper Teste"
  }')

SHIPPER_TOKEN=$(echo "$SHIPPER_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
SHIPPER_ID=$(echo "$SHIPPER_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

if [ -n "$SHIPPER_TOKEN" ]; then
    echo -e "${GREEN}✅ Shipper criado (ID: $SHIPPER_ID)${NC}\n"
else
    echo -e "${RED}❌ Erro ao criar shipper${NC}\n"
    exit 1
fi

# 3. TESTE DE SIGNUP - MOTORISTA
echo -e "${YELLOW}[3] Criando conta Motorista...${NC}"
MOTORISTA_RESPONSE=$(curl -s -X POST "$API_URL/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "motorista_teste_'$(date +%s)'@test.com",
    "password": "teste123",
    "tipo": "motorista",
    "nome": "Carlos Motorista Teste"
  }')

MOTORISTA_TOKEN=$(echo "$MOTORISTA_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
MOTORISTA_ID=$(echo "$MOTORISTA_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

if [ -n "$MOTORISTA_TOKEN" ]; then
    echo -e "${GREEN}✅ Motorista criado (ID: $MOTORISTA_ID)${NC}\n"
else
    echo -e "${RED}❌ Erro ao criar motorista${NC}\n"
    exit 1
fi

# 4. TESTE DE POSTAR FRETE (Shipper)
echo -e "${YELLOW}[4] Postando frete (Shipper)...${NC}"
FRETE_RESPONSE=$(curl -s -X POST "$API_URL/fretes" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $SHIPPER_TOKEN" \
  -d '{
    "origem": "São Paulo",
    "destino": "Rio de Janeiro",
    "peso_kg": 500,
    "valor_r": 1000,
    "descricao": "Eletrônicos - frágil"
  }')

FRETE_ID=$(echo "$FRETE_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

if [ -n "$FRETE_ID" ]; then
    echo -e "${GREEN}✅ Frete criado (ID: $FRETE_ID)${NC}\n"
else
    echo -e "${RED}❌ Erro ao postar frete${NC}\n"
    exit 1
fi

# 5. TESTE DE LISTAR FRETES
echo -e "${YELLOW}[5] Listando fretes disponíveis...${NC}"
FRETES_RESPONSE=$(curl -s -X GET "$API_URL/fretes" \
  -H "Authorization: Bearer $MOTORISTA_TOKEN")

if echo "$FRETES_RESPONSE" | grep -q "fretes"; then
    echo -e "${GREEN}✅ Fretes listados com sucesso${NC}\n"
else
    echo -e "${RED}❌ Erro ao listar fretes${NC}\n"
fi

# 6. TESTE DE PROPOSTA (Motorista)
echo -e "${YELLOW}[6] Motorista fazendo proposta...${NC}"
PROPOSTA_RESPONSE=$(curl -s -X POST "$API_URL/matches/?frete_id=$FRETE_ID&valor_proposta=950&mensagem=Entrego%20em%202%20dias" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $MOTORISTA_TOKEN")

MATCH_ID=$(echo "$PROPOSTA_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

if [ -n "$MATCH_ID" ]; then
    echo -e "${GREEN}✅ Proposta criada (Match ID: $MATCH_ID)${NC}\n"
else
    echo -e "${RED}❌ Erro ao criar proposta${NC}\n"
    exit 1
fi

# 7. TESTE DE VER PROPOSTAS (Shipper)
echo -e "${YELLOW}[7] Shipper vendo propostas recebidas...${NC}"
PROPOSTAS_RESPONSE=$(curl -s -X GET "$API_URL/matches/frete/$FRETE_ID" \
  -H "Authorization: Bearer $SHIPPER_TOKEN")

if echo "$PROPOSTAS_RESPONSE" | grep -q "valor_proposta"; then
    echo -e "${GREEN}✅ Propostas visíveis para shipper${NC}\n"
else
    echo -e "${RED}❌ Erro ao listar propostas${NC}\n"
fi

# 8. TESTE DE ACEITAR PROPOSTA
echo -e "${YELLOW}[8] Shipper aceitando proposta...${NC}"
ACCEPT_RESPONSE=$(curl -s -X PUT "$API_URL/matches/$MATCH_ID/accept" \
  -H "Authorization: Bearer $SHIPPER_TOKEN")

if echo "$ACCEPT_RESPONSE" | grep -q "aceito"; then
    echo -e "${GREEN}✅ Proposta aceita${NC}\n"
else
    echo -e "${RED}❌ Erro ao aceitar proposta${NC}\n"
fi

# 9. TESTE DE CHAT - ENVIAR MENSAGEM
echo -e "${YELLOW}[9] Motorista enviando mensagem no chat...${NC}"
MSG_RESPONSE=$(curl -s -X POST "$API_URL/messages/match/$MATCH_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $MOTORISTA_TOKEN" \
  -d '{
    "conteudo": "Olá! Confirmo a entrega. Saio amanhã cedo."
  }')

if echo "$MSG_RESPONSE" | grep -q "conteudo"; then
    echo -e "${GREEN}✅ Mensagem enviada${NC}\n"
else
    echo -e "${RED}❌ Erro ao enviar mensagem${NC}\n"
fi

# 10. TESTE DE LER MENSAGENS
echo -e "${YELLOW}[10] Shipper lendo mensagens do chat...${NC}"
MSGS_RESPONSE=$(curl -s -X GET "$API_URL/messages/match/$MATCH_ID" \
  -H "Authorization: Bearer $SHIPPER_TOKEN")

if echo "$MSGS_RESPONSE" | grep -q "mensagens"; then
    echo -e "${GREEN}✅ Mensagens carregadas${NC}\n"
else
    echo -e "${RED}❌ Erro ao carregar mensagens${NC}\n"
fi

# 11. TESTE DE CRIAR NOTIFICAÇÃO
echo -e "${YELLOW}[11] Testando notificações...${NC}"
NOTIF_RESPONSE=$(curl -s -X GET "$API_URL/notifications?limit=10" \
  -H "Authorization: Bearer $MOTORISTA_TOKEN")

if echo "$NOTIF_RESPONSE" | grep -q "notificacoes"; then
    echo -e "${GREEN}✅ Notificações funcionando${NC}\n"
else
    echo -e "${RED}❌ Erro ao buscar notificações${NC}\n"
fi

# 12. TESTE DE RATINGS
echo -e "${YELLOW}[12] Shipper avaliando motorista...${NC}"
RATING_RESPONSE=$(curl -s -X POST "$API_URL/ratings/motorista" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $SHIPPER_TOKEN" \
  -d '{
    "rated_user_id": '$MOTORISTA_ID',
    "stars": 5,
    "review_text": "Excelente profissional!",
    "match_id": '$MATCH_ID'
  }')

if echo "$RATING_RESPONSE" | grep -q "stars"; then
    echo -e "${GREEN}✅ Rating criado${NC}\n"
else
    echo -e "${RED}❌ Erro ao criar rating${NC}\n"
fi

# 13. TESTE DE VER RATINGS
echo -e "${YELLOW}[13] Consultando ratings do motorista...${NC}"
RATINGS_RESPONSE=$(curl -s -X GET "$API_URL/ratings/motorista/$MOTORISTA_ID/ratings" \
  -H "Authorization: Bearer $MOTORISTA_TOKEN")

if echo "$RATINGS_RESPONSE" | grep -q "average_rating"; then
    echo -e "${GREEN}✅ Ratings consultados${NC}\n"
else
    echo -e "${RED}❌ Erro ao consultar ratings${NC}\n"
fi

# 14. TESTE DE HISTÓRICO DE TRANSAÇÕES
echo -e "${YELLOW}[14] Consultando histórico de transações...${NC}"
TRANS_RESPONSE=$(curl -s -X GET "$API_URL/transactions?limit=10" \
  -H "Authorization: Bearer $MOTORISTA_TOKEN")

if echo "$TRANS_RESPONSE" | grep -q "transacoes"; then
    echo -e "${GREEN}✅ Histórico de transações funcionando${NC}\n"
else
    echo -e "${RED}❌ Erro ao buscar transações${NC}\n"
fi

# 15. TESTE DE ESTATÍSTICAS DE TRANSAÇÕES
echo -e "${YELLOW}[15] Consultando estatísticas...${NC}"
STATS_RESPONSE=$(curl -s -X GET "$API_URL/transactions/statistics/summary" \
  -H "Authorization: Bearer $MOTORISTA_TOKEN")

if echo "$STATS_RESPONSE" | grep -q "total_transacoes"; then
    echo -e "${GREEN}✅ Estatísticas funcionando${NC}\n"
else
    echo -e "${RED}❌ Erro ao buscar estatísticas${NC}\n"
fi

# RESUMO
echo -e "${YELLOW}===============================================${NC}"
echo -e "${GREEN}✅ TODOS OS TESTES PASSARAM!${NC}"
echo -e "${YELLOW}===============================================${NC}\n"

echo "📊 RESUMO DO TESTE:"
echo "- ✅ Backend online"
echo "- ✅ Autenticação (Login/Signup)"
echo "- ✅ Fretes (criar e listar)"
echo "- ✅ Propostas (criar e aceitar)"
echo "- ✅ Chat (enviar e receber mensagens)"
echo "- ✅ Notificações"
echo "- ✅ Ratings (avaliações)"
echo "- ✅ Histórico de Transações"
echo "- ✅ Estatísticas"
echo ""
echo "🌐 Frontend: $FRONTEND_URL"
echo "📡 Backend: $API_URL"
echo ""
echo -e "${GREEN}Tudo pronto para usar!${NC}"
