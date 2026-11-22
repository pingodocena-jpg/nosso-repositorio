# Vídeos curtos sobre GTA 6 (MoneyPrinterTurbo)

Quatro vídeos verticais (9:16, 1080×1920, cerca de 50 a 65 s) em português, com narração, legendas e música de fundo, gerados com o [MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo).

| # | Vídeo | Roteiro |
|---|---|---|
| 1 | Funcionalidades: as 5 que mais chamam atenção | `roteiros/01-funcionalidades.json` |
| 2 | Diferenciais: o que GTA 6 tem de diferente | `roteiros/02-diferenciais.json` |
| 3 | GTA 5 vs GTA 6: o que mudou em 13 anos | `roteiros/03-gta5-vs-gta6.json` |
| 4 | Reclamações até agora | `roteiros/04-reclamacoes.json` |

Os MP4 finais ficam em `videos/`.

## Como foi feito

1. **Pesquisa** na web em 22/11/2026, três dias depois do lançamento (19/11/2026). As fontes estão no fim deste arquivo.
2. **Roteiros**: escritos à mão a partir da pesquisa e enviados ao MoneyPrinterTurbo com `--video-script`. Por isso não foi preciso configurar nenhum LLM.
3. **Imagens**: cartões no estilo neon com pôr do sol (`tools/make_cards.py`). A arte é original e não usa nenhuma imagem, logo ou trecho da Rockstar, para evitar problemas de direitos autorais.
4. **Sincronia**: `tools/build.py` usa os tempos de cada palavra do Edge TTS para saber quando cada cartão começa. Cada cartão vira um clipe com a duração exata do trecho narrado.
5. **MoneyPrinterTurbo** (`--video-source local`, ordem `sequential`) junta tudo: narração com a voz `pt-BR-AntonioNeural`, legendas, música de fundo e renderização final.

### Como gerar de novo

```bash
git clone https://github.com/harry0703/MoneyPrinterTurbo.git mpt
cd mpt && uv venv .venv -p 3.12 && uv pip install -r requirements.txt && cp config.example.toml config.toml && cd ..
mpt/.venv/bin/python tools/build.py mpt ./work            # todos
mpt/.venv/bin/python tools/build.py mpt ./work 04-reclamacoes   # só um
```

Por padrão a legenda aparece em blocos curtos (`word_by_word` com animação `pop_spring`). Para legendas por frase, rode com `SUB_MODE=sentence`.

`tools/run_mpt.py` só existe por causa deste ambiente de nuvem: ele faz o Edge TTS usar o proxy HTTPS e o certificado dele. Rodando no seu computador, dá para chamar `python cli.py` do MoneyPrinterTurbo direto.

**Para usar vídeos de banco de imagens** no lugar dos cartões, coloque uma chave gratuita do Pexels em `pexels_api_keys` no `config.toml` e troque `--video-source local` por `--video-source pexels`. Só que o Pexels não tem imagens do GTA: ele traz cenas genéricas de Miami, praia e carros.

## Resumo da pesquisa (até 22/11/2026)

**Lançamento**
- Saiu em 19/11/2026 para PS5 e Xbox Series X|S.
- PC ainda sem data oficial (fontes anônimas falam em 1º tri de 2027).
- GTA Online ainda sem data.
- Preço no Brasil: R$ 449,90 (Standard) e R$ 549,90 (Ultimate).

**Crítica e vendas**
- 99 no Metacritic, empatado com Ocarina of Time.
- A Take-Two divulgou US$ 3,79 bi em vendas no primeiro dia. A Sensor Tower estima um número menor, a partir de US$ 2,36 bi.

**Funcionalidades confirmadas**
- Cenário em Leonida (Vice City) com Jason e Lucia, e troca de personagem no meio da missão.
- Medidor de relacionamento e múltiplos finais.
- Perfil criminal, que pode chegar a "Irredimível".
- Inimigos podem ser neutralizados sem morrer.
- Celular com app estilo Instagram.
- Minigame para roubar carro.
- Mais de 600 lojas, fauna e caça.
- Mais de 600 mil animações (GTA V tinha cerca de 55 mil).

**Reclamações**
- 30 fps em todos os consoles, inclusive no PS5 Pro.
- Bugs e crashes no lançamento.
- Sem PC e sem online.
- Preço.
- Ritmo lento: a nota dos usuários no Metacritic ficou em 5,6, com suspeita de review bombing.
- Demissão de 34 funcionários e o processo do sindicato, ainda sem decisão.

**Cuidados**
- Os números de vendas são da própria Take-Two.
- A nota dos usuários muda o tempo todo.
- Lucia é a primeira protagonista mulher **da série principal desde a era 3D**. GTA 1 e GTA 2 já tinham personagens femininas para escolher.

### Fontes
- Vice: lançamento e trailer (15/10/2026), PC e online (20/11/2026), resumo das reviews (18/11/2026)
- VGC: review (18/11/2026) e tribunal do sindicato
- Kotaku: review (18/11/2026) e 30 fps no PS5 Pro
- GamesRadar: 30 fps no PS5 Pro
- Forbes: vendas do primeiro dia (20/11/2026)
- LatinTimes: bugs e queda da PSN (19/11/2026)
- Yahoo: nota dos usuários no Metacritic (21/11/2026)
- Exame e TV Sim Brasil: preços no Brasil
- GameSpot e Sportskeeda: tamanho do mapa
- LevelUp: protagonistas mulheres na franquia
- Fortune (20/11/2026) e TechRadar: sindicato e demissões
