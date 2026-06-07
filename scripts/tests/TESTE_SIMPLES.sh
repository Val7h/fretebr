#!/bin/bash

echo "==============================================="
echo "TESTE RÁPIDO - FRETEBR"
echo "==============================================="
echo ""

# 1. Health check
echo "✅ Verificando backend..."
curl -s http://localhost:8001/health | grep -q "ok" && echo "✅ Backend online" || echo "❌ Backend offline"

# 2. Signup Shipper
echo ""
echo "✅ Criando Shipper..."
SHIPPER=$(curl -s -X POST "http://localhost:8001/api/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{"email":"shipper_'$(date +%s)'@test.com","password":"teste123","tipo":"shipper","nome":"João"}')
SHIPPER_TOKEN=$(echo "$SHIPPER" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
[ -n "$SHIPPER_TOKEN" ] && echo "✅ Shipper criado" || echo "❌ Erro no shipper"

# 3. Signup Motorista
echo "✅ Criando Motorista..."
MOTORISTA=$(curl -s -X POST "http://localhost:8001/api/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{"email":"motorista_'$(date +%s)'@test.com","password":"teste123","tipo":"motorista","nome":"Carlos"}')
MOTORISTA_TOKEN=$(echo "$MOTORISTA" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
[ -n "$MOTORISTA_TOKEN" ] && echo "✅ Motorista criado" || echo "❌ Erro no motorista"

# 4. Postar Frete
echo "✅ Postando frete..."
FRETE=$(curl -s -X POST "http://localhost:8001/api/fretes" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $SHIPPER_TOKEN" \
  -d '{"origem":"São Paulo","destino":"Rio","peso_kg":500,"valor_r":1000,"descricao":"Test"}')
FRETE_ID=$(echo "$FRETE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
[ -n "$FRETE_ID" ] && echo "✅ Frete criado (ID: $FRETE_ID)" || echo "❌ Erro no frete"

# 5. Fazer Proposta
echo "✅ Motorista fazendo proposta..."
PROPOSTA=$(curl -s -X POST "http://localhost:8001/api/matches/?frete_id=$FRETE_ID&valor_proposta=950&mensagem=Entrego%20em%202%20dias" \
  -H "Authorization: Bearer $MOTORISTA_TOKEN")
MATCH_ID=$(echo "$PROPOSTA" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
[ -n "$MATCH_ID" ] && echo "✅ Proposta criada (Match ID: $MATCH_ID)" || echo "❌ Erro na proposta"

# 6. Aceitar Proposta
echo "✅ Shipper aceitando proposta..."
ACCEPT=$(curl -s -X PUT "http://localhost:8001/api/matches/$MATCH_ID/accept" \
  -H "Authorization: Bearer $SHIPPER_TOKEN")
echo "$ACCEPT" | grep -q "aceito" && echo "✅ Proposta aceita" || echo "❌ Erro ao aceitar"

# 7. Enviar Mensagem
echo "✅ Enviando mensagem no chat..."
MSG=$(curl -s -X POST "http://localhost:8001/api/messages/match/$MATCH_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $MOTORISTA_TOKEN" \
  -d '{"conteudo":"Olá! Confirmo entrega."}')
echo "$MSG" | grep -q "conteudo" && echo "✅ Mensagem enviada" || echo "❌ Erro na mensagem"

# 8. Ler Mensagens
echo "✅ Lendo mensagens..."
MSGS=$(curl -s -X GET "http://localhost:8001/api/messages/match/$MATCH_ID" \
  -H "Authorization: Bearer $SHIPPER_TOKEN")
echo "$MSGS" | grep -q "mensagens" && echo "✅ Mensagens carregadas" || echo "❌ Erro ao ler mensagens"

# 9. Rating
echo "✅ Criando rating..."
RATING=$(curl -s -X POST "http://localhost:8001/api/ratings/motorista" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $SHIPPER_TOKEN" \
  -d '{"rated_user_id":2,"stars":5,"review_text":"Ótimo!","match_id":'$MATCH_ID'}')
echo "$RATING" | grep -q "stars" && echo "✅ Rating criado" || echo "❌ Erro no rating"

# 10. Notificações
echo "✅ Consultando notificações..."
NOTIF=$(curl -s -X GET "http://localhost:8001/api/notifications" \
  -H "Authorization: Bearer $MOTORISTA_TOKEN")
echo "$NOTIF" | grep -q "notificacoes" && echo "✅ Notificações funcionam" || echo "❌ Erro nas notificações"

# 11. Transações
echo "✅ Consultando transações..."
TRANS=$(curl -s -X GET "http://localhost:8001/api/transactions" \
  -H "Authorization: Bearer $MOTORISTA_TOKEN")
echo "$TRANS" | grep -q "transacoes" && echo "✅ Transações funcionam" || echo "❌ Erro nas transações"

echo ""
echo "==============================================="
echo "✅ TESTES CONCLUÍDOS!"
echo "==============================================="
echo ""
echo "🌐 Frontend: http://localhost:3009"
echo "📡 Backend: http://localhost:8001"
echo ""
