# Pocket AutoPilot — V3 preview

Assistente local para Pokémon TCG Pocket: planejamento de coleção e recursos, reserva de ampulhetas e reconhecimento revisável de telas por OCR. Continuação da V2 original; não executa ações na conta.

## Estado desta entrega

- V2 recuperada do ZIP original e preservada no histórico Git.
- V3: identifica cabeçalhos de coleção, missões e recursos em português/inglês e apresenta quantidades explícitas como candidatos para revisão.
- Saldos, reserva, inventário e backups não são atualizados automaticamente pela leitura.
- Textos ambíguos ou desconhecidos permanecem sem interpretação; nomes/variantes de cartas não são vinculados ao inventário.
- 23 testes Python e smoke JavaScript executados neste marco. Veja `docs/test-results.md`.
- **Ainda sem validação com capturas reais do jogo ou Android. Não é a versão final do projeto. V4 não iniciada.**

## Executar e verificar

Requer Python 3.10+. Execute `iniciar-windows.bat` e abra `http://127.0.0.1:8765`.
Na aba **Leitor visual**, importe PNG, analise com Tesseract opcional e confira o painel **Reconhecimento V3**. Sem Tesseract, visualização e planejamento continuam disponíveis, mas não há reconhecimento da imagem.

Para verificar sem Android ou OCR instalado, na pasta do projeto:

```text
py -3 -m unittest discover -s tests -v
node tests/ui_smoke_node.js
```

Node é necessário apenas para o teste JavaScript. Os testes usam transcrições OCR sintéticas e ADB simulado; não representam testes no jogo. O teste HTTP do reconhecimento substitui apenas a resposta OCR.

Antes de migrar, exporte seu backup JSON pela V2. Mantenha a mesma origem do navegador para preservar seus dados; `file://` e `http://127.0.0.1:8765` têm armazenamentos distintos. O projeto mantém a chave `pocket-autopilot-v1`. Guarde o ZIP original e seus backups fora da pasta `captures`, que mantém somente as 30 imagens mais recentes.

As listas e estatísticas de decks abaixo são dados históricos herdados da V2, sem revalidação nesta entrega. Não devem ser tratadas como meta atual.

## Documentação original da V2

O conteúdo a seguir documenta a versão importada.

Ferramenta **local e independente**, em português, para acompanhar Pokémon TCG Pocket e planejar uso de pacotes e ampulhetas. Não é afiliada à Pokémon e não controla sua conta.

## O que mudou em relação à V1

- Preservados: inventário de cartas, comparação de 3 decks, recomendações de pacotes, reserva de ampulhetas, checklist de missões, backup JSON.
- Novo: ranking adicional de pacotes considerando a chance publicada e o custo de troca das cartas que faltam. **É uma heurística**, não uma probabilidade de terminar o deck.
- Novo: servidor local no Python, sem dependências Python obrigatórias.
- Novo: aba **Leitor visual**, para capturar imagens do Android com ADB ou importar PNG do celular.
- Novo: OCR de textos em português/inglês quando o programa gratuito Tesseract OCR estiver instalado.
- Novo: monitoramento de tela a cada 15 segundos enquanto a aba estiver visível e o usuário mantiver o monitoramento ligado.
- Novo: histórico das 30 capturas mais recentes, com armazenamento exclusivamente local.
- Novo: 6 testes automatizados do backend e teste básico de interface JavaScript com Node.js (opcional).

**Limites reais:** a ferramenta não joga partidas, não toca na tela, não coleta recompensas dentro da conta, não identifica sozinho as cartas da imagem e não abre pacotes. O OCR devolve texto para você conferir. Não há promessa de vitória contra qualquer deck, nem de obter cartas específicas em determinado número de pacotes.

## Instalação simples (Windows)

Requisitos: Windows 10/11, **Python 3.10 ou superior**, navegador Chrome ou Edge.

1. Extraia o ZIP do projeto.
2. Dê duplo clique em `iniciar-windows.bat` (ou no terminal use `py -3 app.py --open`).
3. Se o navegador não abrir automaticamente, acesse `http://127.0.0.1:8765`.
4. Use a aba **Decks e cartas** para atualizar o inventário e comparar decks.
5. Use **Recursos e dados** para definir uma reserva mínima de ampulhetas e registrar os saldos reais.
6. Para capturas, abra **Leitor visual** e escolha importação PNG ou Android conectado.
7. Mantenha a janela de comandos aberta enquanto usar o leitor visual. Para encerrar, pressione `Ctrl+C`.

**Se vier da V1:** abra primeiro a V1 e use `Recursos e dados > Exportar backup JSON`. Em seguida, abra a V2 pelo endereço local e importe esse JSON na mesma aba. Dados no `file://` e em `http://127.0.0.1:8765` usam armazenamentos distintos; sem essa migração, o inventário antigo pode não aparecer. Não exclua a V1 antes de fazer backup.

## Se joga no celular, sem emulador

1. Faça uma captura de tela **PNG** no celular.
2. Transfira a imagem para o PC (máximo 4 MB por captura).
3. Com o servidor aberto, use **Leitor visual > Importar captura PNG**.
4. Se o OCR opcional estiver instalado, clique **Analisar texto da captura (OCR)**.
5. Confirme os números visualmente e registre-os manualmente em **Recursos e dados**.

Não precisa de ADB nessa modalidade. O app não envia imagens para serviços externos.

## Se usa Android ou emulador no PC

1. Instale as **Android SDK Platform Tools** oficiais, disponibilizando `adb` no `PATH` do Windows.
2. Abra o emulador ou conecte um Android de sua confiança com a depuração USB autorizada.
3. Execute no terminal `adb devices`. O status deve aparecer como `device`.
4. Abra a aba **Leitor visual**, pressione **Atualizar conexão**, selecione o dispositivo e clique **Capturar tela agora**.
5. O monitoramento periódico só começa se você clicar **Monitorar a cada 15 s**; não é ativado automaticamente.

Se quiser executar a ponte isoladamente:

```powershell
py -3 adb_bridge.py info
py -3 adb_bridge.py devices
py -3 adb_bridge.py screenshot --out captures/minha-tela.png
```

A ponte ADB executa apenas comandos para **identificar dispositivos e capturar screenshots**. Não há comandos ADB de toque, gesto, instalação, alteração do app ou acesso aos servidores do jogo. Desative a depuração USB quando não precisar dela.

## OCR opcional

Instale separadamente o aplicativo **Tesseract OCR** e deixe `tesseract` acessível no `PATH` do Windows. Para maior qualidade em telas brasileiras, adicione dados de idioma `por` e, opcionalmente, `eng`. Reinicie o servidor e clique em **Analisar texto da captura**. Sem Tesseract, você continua podendo importar e visualizar imagens.

O OCR pode confundir textos, cartas, quantidade de ampulhetas e números. **Nunca trate os resultados como uma coleta automática verificada.**

## Política de recursos

- Use primeiro pacotes liberados pela recarga normal, se forem úteis ao deck escolhido.
- Preserve o valor configurado como **reserva mínima de ampulhetas**.
- Evite gastar ampulhetas em busca de cartas que aparecem como promocionais ou obtidas pela loja.
- Dados de chances e decks refletem o levantamento original da V1 em 01/11/2026; novas coleções e o meta exigem revisão.
- Não automatize gastos com dinheiro, Pokéouro, pontos ou ampulhetas com base em OCR.
- O indicador de valor de pacotes não avalia todos os caminhos de aquisição e **não calcula o número mínimo esperado de pacotes**.

## Arquivos

| Arquivo | Finalidade |
|---|---|
| `iniciar-windows.bat` | Abrir o servidor local e o navegador no Windows |
| `app.py` | Servidor HTTP limitado ao próprio PC, importação PNG, ADB e OCR |
| `index.html` | Interface local, inventário, análise de decks, leitor visual |
| `adb_bridge.py` | Captura de tela ADB somente leitura |
| `tests/test_server.py` | Testes de API usando um Android simulado |
| `tests/ui_smoke_node.js` | Teste da interface e cálculos sem navegador real |
| `captures/` | Screenshots locais; o programa mantém no máximo 30 |

### Testes

No terminal dentro da pasta:

```powershell
py -3 -m unittest discover -s tests -v
```

Node.js é opcional para testar a lógica do navegador:

```powershell
node tests/ui_smoke_node.js
```

Os testes automáticos não substituem a verificação com um Android real, porque idioma, resolução e interface do jogo variam.

## Segurança e privacidade

- O servidor atende **somente 127.0.0.1**, não abre uma interface pública na rede.
- Não solicita senha ou token da conta.
- Imagens ficam apenas na pasta `captures/` do seu PC e são apagadas conforme entram novas capturas além do limite de 30. As imagens antigas que você queira preservar devem ser copiadas antes.
- O inventário e os saldos ficam salvos no `localStorage` do navegador; exporte backups JSON regularmente.
- O modo de monitoramento de screenshots exige ativação manual e ignora a aba em segundo plano.
- Não substitui autorização e regras aplicáveis do serviço. Consulte os termos da plataforma antes de qualquer automação futura de ações no jogo.

## Fontes históricas (listas da V1, 01/11/2026)

- https://tcgpocketmeta.com/budget-decks
- https://tcgpocketmeta.com/pack-advisor
- https://tcgpocketmeta.com/decks/umbreon-mega-sableye-ex
- https://tcgpocketmeta.com/decks/umbreon-hydreigon
- https://tcgpocketmeta.com/decks/mega-manectric-ex-heliolisk
- https://www.pokemon.com/uk/pokemon-video-games/pokemon-trading-card-game-pocket
- https://www.pokemon.com/uk/legal/terms-of-use
