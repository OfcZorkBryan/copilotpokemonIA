# Continuação autônoma — assistente de leitura e planejamento

O usuário reiterou que deseja desenvolvimento contínuo, identificação automática de oportunidades de ampulhetas e testes a cada marco. A validação real da V3 segue pendente: abriu o inicializador MSI, mas o atalho Engine exige outra aprovação do Windows. Não há Android autorizado no ADB.

Decisão: desenvolver módulos independentes enquanto esse ambiente estiver indisponível, validando-os tecnicamente sem declarar qualquer etapa validada no jogo. A regra anterior do projeto de não iniciar nenhum código V4 sem capturas reais era uma decisão de execução; é refinada aqui para permitir módulos offline em preview. A liberação final continua dependendo de evidências reais.

## Marco A — planejamento automático sem ações na conta

Arquivos: planner.py, app.py, tests/test_planner.py, tests/test_server.py.
Interface build_plan(state: dict, observation: dict | None) -> dict. A entrada state é o registro manual local; observation é uma leitura não confirmada. Não mesclar as duas fontes, nem modificar nenhuma entrada. Reserva desconhecida usa padrão 12 do projeto; saldo desconhecido permanece desconhecido. Números exigem inteiros não negativos e limites do painel. Gasto automático é sempre zero. Progresso OCR concluído gera sugestão de conferir resgate, sem afirmar que a recompensa existe ou foi recebida.

- [ ] Escrever e executar testes: tipos inválidos, reserva maior que saldo, saldo desconhecido, pacotes gratuitos, missões lidas, dados conflitantes e preservação de estado.
- [ ] Implementar função pura e integrar /api/ocr e /api/plan, com validação de entradas.
- [ ] Executar suíte Python completa, com OCR real sintético.

## Marco B — ciclo de observação integrado

Arquivos: index.html, tests/ui_observer_node.js, .github/workflows/tests.yml.
O monitor autorizado captura uma nova imagem, executa OCR e organiza sugestões automaticamente. Só trabalha na aba visível e durante ativação explícita. Não reanalisa captura antiga se a captura atual falhar. Não produz toque, gasto ou resgate. O painel mostra origem e necessidade de revisão das sugestões, e não salva OCR como saldo.

- [ ] Testes JS assíncronos antes da alteração: sequência captura→OCR, falha de captura, concorrência, aba oculta e ausência de mutação do estado.
- [ ] Implementar ciclo de observação e painel de sugestões, preservando backup e chave localStorage.
- [ ] Executar Python e Node completos; revisar, publicar e acompanhar CI.

## Limites

Nenhuma automação de farming, compras, partidas, cadastro, autenticação ou bypass de proteções. A coleta de recursos dentro do jogo permanece manual ou por recursos oficiais permitidos. Identificação e planejamento podem ser automáticos; recomendações não equivalem a ações executadas.
