# instagram-milico-bot

Automação de 2 posts diários no Instagram [@milicomoralizado](https://www.instagram.com/milicomoralizado/):

- **09h (BRT)** — frase motivacional para concurseiros de carreiras policiais.
- **19h (BRT)** — questão de concurso (Direito Penal, Direito Constitucional, Processo Penal e Legislação da PMBA).

O conteúdo vem de um banco curado (`data/questoes.json`, `data/frases.json`), renderizado sobre uma arte fixa (`assets/template_*.png`) com [Pillow](https://python-pillow.org/), e publicado via **Instagram API with Instagram Login** (rota oficial, dentro dos Termos de Uso — não exige Página do Facebook, funciona direto com conta Criador ou Empresa). O agendamento roda no **GitHub Actions**, sem depender de nenhum computador ligado.

## Checklist de setup (só você consegue fazer isso)

### 1. Conta profissional

Sua conta já é **Criador (Creator)** — isso é suficiente, não precisa virar Empresa nem vincular Página do Facebook (a "Instagram API with Instagram Login" funciona direto com conta Criador).

### 2. Criar o App na Meta

1. Acesse [developers.facebook.com](https://developers.facebook.com/apps) → **Meus Apps → Criar App** → tipo **Negócios**.
2. No painel do app, adicione o produto **Instagram API with Instagram Login** (Adicionar Produto → procure "Instagram" → Configurar).
3. Dentro do produto, vá em **API setup with Instagram login** → siga o passo de adicionar sua conta @milicomoralizado como conta de teste/autorizada (ele te dá um link para logar com o Instagram e autorizar o app — usa o login do próprio Instagram, sem Facebook).

### 3. Gerar o token de acesso e pegar o IG_USER_ID

Ainda na página **Instagram → API setup with Instagram login** do painel do app, tem uma seção "Generate access token" — clique em **Generate token** para a conta @milicomoralizado já conectada. Isso gera um token válido por 60 dias.

Com esse token, confirme o ID da conta:

```bash
curl -i -X GET "https://graph.instagram.com/v25.0/me?fields=user_id,username&access_token=SEU_TOKEN"
```

O `user_id` retornado é o `IG_USER_ID`. O token gerado é o `IG_ACCESS_TOKEN`.

> **Manutenção:** esse token expira em ~60 dias. Repita esse passo antes de expirar. Quando o v1 estiver rodando estável, podemos automatizar esse refresh dentro do próprio workflow.

### 4. Permissões de publicação

Na mesma tela, garanta que o escopo **`instagram_business_content_publish`** (e `instagram_business_basic`) esteja marcado/autorizado — sem isso o token não consegue publicar.

### 5. Repositório no GitHub

✅ Já feito: [github.com/Nandofv22/milicomoralizado](https://github.com/Nandofv22/milicomoralizado) (público, necessário para o `raw.githubusercontent.com` servir as imagens sem autenticação — nenhum segredo fica versionado, tokens ficam só em Secrets).

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
