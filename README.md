# instagram-milico-bot

Automação de 2 posts diários no Instagram [@milicomoralizado](https://www.instagram.com/milicomoralizado/):

- **09h (BRT)** — frase motivacional para concurseiros de carreiras policiais.
- **19h (BRT)** — questão de concurso (Direito Penal, Direito Constitucional, Processo Penal e Legislação da PMBA).

O conteúdo vem de um banco curado (`data/questoes.json`, `data/frases.json`), renderizado sobre uma arte fixa (`assets/template_*.png`) com [Pillow](https://python-pillow.org/), e publicado via **Instagram Graph API** (rota oficial, dentro dos Termos de Uso). O agendamento roda no **GitHub Actions**, sem depender de nenhum computador ligado.

## Checklist de setup (só você consegue fazer isso)

### 1. Converter a conta para Business

No app do Instagram → Configurações → Conta → Mudar para conta profissional → **Empresa** (categoria "Educação" ou similar). Aceite a criação/vínculo de uma Página do Facebook quando for solicitado.

### 2. Criar o App na Meta

1. Acesse [developers.facebook.com](https://developers.facebook.com/apps) → **Meus Apps → Criar App** → tipo "Negócios".
2. No painel do app, adicione o produto **Instagram Graph API** (Adicionar Produto → Instagram → Configurar).
3. Em **Funções do App → Funções → Testadores do Instagram**, adicione @milicomoralizado como testador (isso permite publicar em modo de desenvolvimento, sem precisar passar pelo App Review, já que é uso próprio).
4. Aceite o convite de testador dentro do próprio app do Instagram (Configurações → Apps e sites → Convites de testador).

### 3. Gerar o token de acesso

1. Abra o [Graph API Explorer](https://developers.facebook.com/tools/explorer), selecione o seu App.
2. Em "Permissions", marque: `instagram_basic`, `instagram_content_publish`, `instagram_manage_comments`, `pages_show_list`, `pages_read_engagement`, `business_management`.
3. Clique em "Generate Access Token" e autorize.
4. Troque o token de curta duração por um de longa duração (60 dias), rodando localmente (substitua `APP_ID`, `APP_SECRET` e `SHORT_TOKEN`):

   ```bash
   curl -i -X GET "https://graph.facebook.com/v21.0/oauth/access_token?grant_type=fb_exchange_token&client_id=APP_ID&client_secret=APP_SECRET&fb_exchange_token=SHORT_TOKEN"
   ```

   O `access_token` retornado é o que vai no secret `IG_ACCESS_TOKEN`.

   > **Manutenção:** esse token expira em ~60 dias. Repita esse passo antes de expirar (a Meta permite renovar antes do vencimento pelo mesmo endpoint). Quando o v1 estiver rodando estável, podemos automatizar esse refresh dentro do próprio workflow.

### 4. Descobrir o IG_USER_ID

```bash
curl -i -X GET "https://graph.facebook.com/v21.0/me/accounts?access_token=SEU_TOKEN"
```

Pegue o `id` da Página retornada, depois:

```bash
curl -i -X GET "https://graph.facebook.com/v21.0/PAGE_ID?fields=instagram_business_account&access_token=SEU_TOKEN"
```

O `instagram_business_account.id` retornado é o `IG_USER_ID`.

### 5. Criar o repositório no GitHub e subir o projeto

Crie um repositório **público** vazio (precisa ser público para o `raw.githubusercontent.com` servir as imagens sem autenticação — nenhum segredo fica versionado, tokens ficam só em Secrets). Me passe a URL para eu configurar o remote e dar push.

### 6. Cadastrar os Secrets

No repositório: **Settings → Secrets and variables → Actions → New repository secret**:

- `IG_USER_ID`
- `IG_ACCESS_TOKEN`

### 7. Testar antes de confiar no cron

Vá em **Actions**, escolha o workflow "Post frase motivacional" ou "Post questao do dia", clique em **Run workflow** (gatilho manual `workflow_dispatch`) e confirme que o post apareceu de verdade no Instagram.

## Como funciona por dentro

```
scripts/render_frase.py      -> escolhe a proxima frase do banco (sem avancar o indice), desenha sobre assets/template_frase.png, salva em output/ + um .meta.json com a legenda
scripts/render_questao.py    -> mesma logica para questoes, incluindo o comentario com o gabarito
scripts/publish_post.py      -> monta a URL publica (raw.githubusercontent.com), publica via Graph API, comenta o gabarito (se houver) e so ENTAO avanca o indice em data/state.json
scripts/instagram_api.py     -> funcoes de publish/comment na Graph API
scripts/state.py             -> leitura/escrita de data/state.json (rotacao dos bancos)
```

Os dois workflows (`.github/workflows/post-frase.yml` e `post-questao.yml`) fazem: renderizar → commitar a imagem → publicar → commitar o novo índice de rotação. Se a publicação falhar, o índice não avança (o mesmo conteúdo é tentado de novo no próximo dia).

## Repondo o banco de conteúdo

Quando `data/questoes.json` ou `data/frases.json` começar a se aproximar do fim (60 itens cada, dá pra uns 2 meses sem repetir), é só pedir pra gerar um novo lote no mesmo formato — os índices em `data/state.json` voltam ao 0 automaticamente quando o banco acaba (rotação circular).

## Rodando localmente para testar

```bash
pip install -r requirements.txt
cd scripts
python render_frase.py --date teste --index 0     # gera output/frase_teste.png
python render_questao.py --date teste --index 0   # gera output/questao_teste.png
```

`publish_post.py` só funciona dentro do GitHub Actions (depende de `GITHUB_REPOSITORY` para montar a URL pública) ou localmente exportando `GITHUB_REPOSITORY=owner/repo`, `GITHUB_REF_NAME=main`, `IG_USER_ID` e `IG_ACCESS_TOKEN` manualmente.
