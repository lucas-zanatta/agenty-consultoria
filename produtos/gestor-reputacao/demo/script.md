# Script de Demo — Gestor de Reputação Automático
## Duração: 5 minutos | Formato: call com vídeo ou presencial

---

## Preparação (antes da call)

- [ ] Servidor rodando: `uvicorn src.main:app --host 0.0.0.0 --port 8000` + `MOCK_MODE=true`
- [ ] Abrir Google Maps do prospect em outra aba
- [ ] Ter o e-mail de aprovação visível (Gmail em outra aba)
- [ ] Certificar que o servidor de demo responde em `/health`

---

## Roteiro

### Abertura (30 segundos)

*Compartilhar tela com o Google Maps do prospect aberto.*

**Fala:**
> "Abri aqui o seu perfil no Google Maps. Olha essa avaliação de [RATING] estrelas — está sem resposta há [X] semanas. Enquanto a gente conversa, qualquer pessoa que pesquisar [nome do negócio] vai ver isso aqui. Eu quero te mostrar o que a Agenty faz com isso em dois minutos."

**Objetivo:** mostrar o problema real, não hipotético. O prospect se vê na tela.

---

### Demo ao vivo — parte 1: resposta automática (90 segundos)

*Abrir terminal com o servidor rodando. Mostrar o endpoint `/health`.*

**Fala:**
> "Esse é o sistema rodando. Agora vou simular o que acontece quando uma avaliação 5 estrelas chega no seu Google."

*Disparar manualmente um ciclo ou mostrar o log rodando com MOCK_MODE.*

*Mostrar no log:*
```
[INFO] Processando avaliacao de Ana Paula Souza (5 estrelas)
[INFO] Auto-respondido: Ana Paula Souza (5 estrelas)
```

**Fala:**
> "Viu? Em segundos. A resposta foi direto para o Google, personalizada com o nome da avaliadora, no tom que você escolheu. Sem você tocar em nada."

---

### Demo ao vivo — parte 2: aprovação de negativa (90 segundos)

*Mostrar no log a avaliação de 2 estrelas (Carlos Mendes, mock).*

```
[INFO] Processando avaliacao de Carlos Mendes (2 estrelas)
[INFO] Rascunho enviado para aprovacao: Carlos Mendes (2 estrelas)
```

*Abrir o e-mail de aprovação recebido.*

**Fala:**
> "Essa aqui era uma avaliação negativa. O sistema não publicou nada sozinho — me mandou esse e-mail com a resposta sugerida. Olha: tem o texto da avaliação, a resposta que o Claude gerou, e um botão. Se você aprovar, clica aqui..."

*Clicar no botão de aprovação — mostrar a página de confirmação.*

**Fala:**
> "Publicado. Isso acontece em até 2 horas depois da avaliação chegar. Nenhum cliente negativo fica sem resposta."

---

### ROI e diferencial (60 segundos)

**Fala:**
> "Resumindo: avaliações positivas são respondidas automaticamente no seu tom. Negativas, você controla — recebe o rascunho, lê, aprova com um clique. O Google vê que você está presente, o ranking sobe, e quem pesquisa vê um negócio que se importa com os clientes."

*Mostrar rapidamente o Google Maps de um concorrente que responde bem.*

> "Negócios que respondem bem aparecem mais no Maps. É esse o jogo."

---

### Fechamento (30 segundos)

**Fala:**
> "A implementação fica pronta em até 48 horas. Você me passa o acesso ao Google Meu Negócio, a gente define o tom de voz, e o sistema começa a rodar. R$ 3.000 para configurar, R$ 150 por mês depois. Cancela quando quiser, via WhatsApp comigo. Faz sentido para você?"

---

## Objeções comuns

**"Meus clientes vão perceber que é robô?"**
> "As respostas são específicas — mencionam o nome do avaliador e um detalhe do texto. É exatamente como você escreveria se tivesse tempo. Você mesmo vai ler antes de aprovar as negativas."

**"E se a resposta automática for errada?"**
> "Você define as regras. Posso subir o limite para 5 estrelas e colocar tudo em aprovação no início. A gente vai calibrando juntos até você confiar."

**"Preciso de quanto tempo pra configurar?"**
> "Você me manda dois dados: o acesso ao Google e qual e-mail quer receber as aprovações. O resto é comigo. Em 48h está rodando."

**"Posso cancelar?"**
> "Qualquer hora, via WhatsApp, sem burocracia."

---

## Números para mencionar (com fonte)

- O Google usa taxa de resposta a avaliações como sinal de ranking local
- Negócios que respondem são vistos como 1,7x mais confiáveis pelos consumidores
- 63% das pessoas leem avaliações antes de visitar um negócio local
- Avaliação negativa sem resposta fica visível no Maps por tempo indefinido

---

*Agenty — Sua empresa fatura mais com IA.*
