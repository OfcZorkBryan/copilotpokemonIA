# V3 Recognition Implementation Plan

> Execução nesta sessão: superpowers:executing-plans, com testes antes das alterações e verificação antes de concluir.

**Goal:** estender a V2 com identificação conservadora de telas e candidatos OCR sem alterar dados salvos.

**Architecture:** função pura recognition.recognize(text) produz um dicionário JSON. /api/ocr acrescenta recognition ao contrato existente; a interface exibe candidatos e revisão obrigatória.

**Tech Stack:** Python 3.10+, biblioteca padrão, JavaScript existente, Tesseract opcional.

**Spec:** docs/v3-design.md.

## Global Constraints

- Preservar chave pocket-autopilot-v1, reserva e backups.
- Não executar ações no jogo.
- Sem capturas reais, não declarar V3 validada no jogo nem avançar à V4.

## Review Focus

- Rótulos em menus e missões não devem ser confundidos com saldo.
- Números ilegíveis ou conflitantes devem permanecer ausentes.
- Conteúdo OCR deve ser escapado na apresentação.
- OCR indisponível deve manter o fluxo V2.
- Analisar uma captura não deve modificar inventário, missões ou recursos.

## Task 1: base reproduzível no Windows

- [ ] Registrar teste original com falha.
- [ ] Adaptar o executável ADB simulado para usar sys.executable em subprocesso, sem alterar o conector de produção.
- [ ] Executar os seis testes e o smoke JavaScript.

## Task 2: reconhecimento e integração

Arquivos: recognition.py, tests/test_recognition.py, tests/test_server.py, app.py.

Interface: recognize(text: str) -> dict, com screen, evidence, candidates, warnings e requires_review. candidates contém resources (dict), cards (list) e missions (list). screen é collection, missions, resources ou unknown.

- [ ] Escrever testes de identificação PT/EN, números 0 e milhares, conflito, recompensas, tela desconhecida, cartas e missões; executá-los e observar falha por funcionalidade ausente.
- [ ] Implementar regras do design e executar testes do parser.
- [ ] Escrever teste HTTP: OCR simulado acrescenta candidatos, OCR indisponível e erro continuam explícitos; observar falha e integrar reconhecimento sem quebrar campos existentes.
- [ ] Executar suíte completa.

## Task 3: apresentação e entrega

Arquivos: index.html, tests/ui_smoke_node.js, README.md, docs/test-results.md.

- [ ] Adicionar testes JavaScript para apresentação dos candidatos, escape HTML e ausência de mutação do estado; observar falha.
- [ ] Exibir rótulos, evidências, avisos e candidatos em português, sem botão de aplicação automática.
- [ ] Executar suíte Python e smoke JavaScript completos.
- [ ] Registrar limitações reais, criar ZIP, conferir integridade e registrar commits locais. Publicação GitHub depende de conexão funcional.
