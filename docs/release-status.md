# Estado integrado — assistente V5 preview

Data local: 1º de novembro de 2026, America/Sao_Paulo.

## Entrega técnica

49 testes Python aprovados: 15 do reconhecimento, 5 com OCR real sintético, 12 do planejador, 11 do servidor e 6 do diagnóstico. Três scripts Node aprovados: apresentação, observação assíncrona e comparação de decks. Os modelos OCR e o executável são locais, sem envio de imagens a serviços externos.

| Etapa | Implementado e verificado | Validação real pendente |
|---|---|---|
| V1 | Inventário, reserva, backup e planejamento herdados preservados | Conferência dos dados da conta |
| V2 | Captura real de Android via ADB | Nenhuma para a captura da tela inicial testada |
| V3 | OCR e classificação com casos sintéticos; tela real desconhecida rejeitada | Coleção, missões e recursos reais do jogo |
| V4 | Ciclo automático captura→OCR→sugestões; reserva e estado protegidos | Sugestões confrontadas com missões reais |
| V5 | Ranking automático por coleção/custo; referências documentadas de arquétipos | Listas, custos e probabilidades atuais conferidos no jogo |
| V6 | Diagnóstico integrado e monitoramento real do Android | Jogo instalado/aberto e cenários reais ponta a ponta |

Não foi declarada conclusão da versão final. O produto implementa automação de observação e planejamento; não implementa coleta, abertura de pacotes, gasto de recursos, navegação ou partidas dentro do jogo.

## Evidência de Android real

O Android Engine MSI iniciou após aprovação manual do usuário. Captura via adb_bridge.py funcionou. A imagem da tela inicial foi processada por Tesseract real e classificada como unknown, com candidatos vazios, como esperado.

No aplicativo servido na porta local 8767, o monitor foi ativado pelo botão. A interface registrou quatro capturas automáticas sucessivas, com horários UTC no nome: 02:07:22, 02:07:37, 02:07:52 e 02:08:07 em 2026-11-02 (23:07–23:08 de 2026-11-01 no fuso local). Cada ciclo percorreu captura, OCR e sugestões; a tela inicial não foi confundida com uma tela de jogo. O botão Parar foi acionado e a interface confirmou Monitoramento pausado. Os campos de recursos permaneceram em zero e a reserva em 12, iguais ao início deste teste em origem de navegador separada.

Isso é teste real de integração com Android, não teste dentro do Pokémon TCG Pocket. Capturas permanecem ignoradas pelo Git e não foram publicadas no repositório.

## Instalação e controle do jogo

Não se constatou o jogo aberto na tela inicial. As tentativas de abrir Aplicativos do sistema pela entrada normal não produziram mudança visível, e a tentativa de toque pelo ADB retornou error: closed. O ADB incluído é versão 1.0.36; consultas e captura por exec-out funcionaram, enquanto outros comandos retornaram closed. A causa completa da limitação de entrada não foi estabelecida. Nenhuma configuração de proteção, acesso ADB, conta, senha, verificação ou root foi alterada. Nenhum APK alternativo foi instalado.

Será necessário disponibilizar o jogo pela loja oficial ou fornecer capturas reais antes de validar as telas positivas e os cenários finais. Autorização no chat não equivale à instalação bem-sucedida nem comprova compatibilidade do jogo.

## Revisões e regressões

O módulo V4 recebeu revisão independente e correções verificadas por testes vermelhos/ verdes para: captura antiga sob prévia nova após falha de importação, resposta OCR tardia aplicada a outra imagem e botão Parar indisponível durante processamento. Ranking/meta e diagnóstico receberam revisões separadas sem novos problemas concretos.

Os dados manuais não são substituídos por OCR. O gasto automático permanece zero, mesmo acima da reserva. Mudanças em recursos/tarefas invalidam sugestões anteriores. Falta de dependências quando OCR real é explicitamente exigido produz falha, em vez de sucesso com testes ignorados.

## Verificação remota

V4 publicada no commit f6aeff3e9da835a62355d9a09cb11a67f27e59d9, com GitHub Actions aprovado:
https://github.com/OfcZorkBryan/copilotpokemonIA/actions/runs/41374785751

Os resultados da publicação V5 serão confirmados após o envio, sem presumir aprovação pela mera existência do workflow.
