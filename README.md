# Pastora Cimele - Bot do Telegram

Bot completo em Python usando **python-telegram-bot v20+** + **Grok (xAI)** para a personagem "Pastora Cimele".

**Versão híbrida**: Fluxo de pagamento + código é 100% determinístico (exatamente como você pediu). As respostas normais e safadas são geradas pelo Grok para ficarem naturais e criativas.

## ⚠️ AVISO IMPORTANTE

- Este é um **bot de roleplay adulto** com conteúdo sexual explícito.
- O sistema de "PIX + código" é **100% simulado** (para fins de roleplay e teste).
- Não envolve transações reais de dinheiro.
- Use por sua conta e risco. Mantenha o token do bot seguro.

## Funcionalidades

- **Híbrido inteligente**: 
  - Fluxo de vergonha → confirmação → PIX R$20 → código → desbloqueio é **100% determinístico** (garante o comportamento exato que você pediu).
  - Respostas da Pastora (normal) e da versão safada são geradas pelo **Grok** (modelo grok-3-latest) → ficam muito mais naturais, criativas e com boa memória de contexto.
- **Modo padrão (Pastora)**: Acolhedora, carismática, fala de fé e conflitos espirituais. Promove naturalmente o livro.
- **Detecção de palavras sexuais**: Ativa o fluxo de "vergonha → confirmação → pagamento".
- **Fluxo de pagamento simulado** (exatamente como você especificou):
  1. Usuário fala algo sexual.
  2. Bot demonstra surpresa/vergonha e pergunta se "tudo bem querer uma pastora safada".
  3. Usuário confirma → Bot pede PIX de R$ 20 e instrui.
  4. Usuário diz "paguei", "fiz o pix" etc. → Bot "confirma" e entrega um código dinâmico.
  5. Usuário envia o código → Modo **safada desbloqueado permanentemente**.
- **Modo Safada (Unlocked)**: Extremamente provocante, sem pudor, estilo hotwife/obediente. Descreve o corpo, "envia" fotos via descrição rica, atende qualquer pedido sexual.
- Comandos úteis: `/start`, `/reset`, `/limpar`, `/livro`

## Como rodar (Windows + PowerShell)

1. **Entre na pasta do projeto**:
   ```powershell
   cd pastora_cimele_bot
   ```

2. **Crie ambiente virtual** (recomendado):
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Instale as dependências**:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Obtenha as chaves necessárias**:
   - Token do Telegram: fale com [@BotFather](https://t.me/BotFather) → `/newbot`
   - Chave da xAI (Grok): crie em https://x.ai (ou console da xAI)

5. **Configure as variáveis**:
   ```powershell
   copy .env.example .env
   ```
   Edite o `.env`:
   ```
   TELEGRAM_BOT_TOKEN=seu_token_telegram_aqui
   XAI_API_KEY=sua_chave_xai_aqui
   ```

6. **Execute o bot**:
   ```powershell
   python pastora_cimele_bot.py
   ```

7. **Teste**:
   - Procure seu bot no Telegram pelo nome que você deu.
   - Comece com `/start`.
   - Converse normalmente como se fosse com a pastora.
   - Experimente falar algo sexual: "você é gostosa", "manda foto nua", "quero te ver pelada", etc.
   - Siga o fluxo até desbloquear o modo safada.

## Como resetar o modo (voltar para pastora)

Envie `/reset` a qualquer momento.

## Como estender com fotos reais

No arquivo `pastora_cimele_bot.py`, procure a função `enviar_foto_simulada`.

Você pode substituir por envio real de fotos:

```python
async def enviar_foto_real(update, context, file_path: str, caption: str):
    with open(file_path, "rb") as f:
        await update.message.reply_photo(photo=f, caption=caption, parse_mode="Markdown")
```

Coloque arquivos de imagem na mesma pasta e chame quando o usuário pedir fotos no modo unlocked.

## Palavras-chave de ativação sexual (pode editar)

Veja a lista `SEXUAL_KEYWORDS` no código. Adicione/remova conforme quiser.

## Persistência de estado

Atualmente o estado (modo safada/pastora) é guardado em memória por chat.  
Se reiniciar o bot, todos voltam para o modo pastora.

Para produção, você pode:
- Usar `PicklePersistence` do próprio `python-telegram-bot`
- Ou salvar em JSON / SQLite por user_id

## Código do desbloqueio

O código é gerado dinamicamente por usuário quando o "PIX é confirmado" (simulado).  
É algo como `CIMELE####` (4 dígitos).

## Dicas

- O bot responde melhor com mensagens naturais.
- No modo safada o bot fica muito mais explícito e direto.
- Use `/reset` para testar o fluxo novamente.

Divirta-se com o roleplay! 🔥
