# Marco de observação e planejamento V4 preview

Data: 1º de novembro de 2026, America/Sao_Paulo.

## Resultado técnico

42 testes Python aprovados: 15 de reconhecimento, 5 com Tesseract real sobre PNGs sintéticos, 12 do planejador e 10 do servidor. Dois scripts Node verificam apresentação e ciclo assíncrono. Não há teste dentro do jogo nesta sessão.

Novo fluxo: monitor ativado → captura nova → OCR → sugestões. Ele pausa em aba oculta, não sobrepõe operações e não analisa imagem anterior após erro de captura. Parar durante captura evita iniciar OCR depois; parar durante OCR interrompe ciclos futuros, enquanto a análise já iniciada pode terminar.

Plano: separa recursos/tarefas registrados de observações não confirmadas, destaca missões potencialmente concluídas e protege a reserva. Nenhum gasto ou resgate é executado. Valores inválidos recebem erro HTTP400. Alterar recursos ou tarefas invalida as sugestões exibidas anteriormente.

## Revisão e correções

Revisão independente identificou dois problemas reproduzidos em testes Node que falharam antes da correção:

- Importação falha mantinha captura antiga sob prévia nova. Agora qualquer nova importação invalida o arquivo anterior imediatamente; não é possível analisar a prévia não importada como se fosse a imagem antiga.
- Botão Parar ficava desabilitado durante captura/OCR. Agora fica habilitado quando o monitor está ativo, inclusive durante processamento. O teste verifica o estado real do botão gerado, além da função de parada.

Também foi reproduzida e corrigida a aplicação tardia de OCR quando a captura muda durante a análise. A resposta só é exibida se corresponder à imagem atual. Estado salvo, inventário, recursos e reserva permanecem iguais durante observação automática nos testes.

## Ambiente real

A aprovação do usuário abriu o inicializador MSI App Player. O atalho instalado MSI App Player Engine contém --instance Pie64; foi aberto pelo Explorador. Isso acionou outra solicitação de permissão Windows (processo consent detectado). Não houve intervenção nessa solicitação. ADB continua sem dispositivos, sem mudança nas configurações de segurança. Instalação do jogo e capturas reais seguem pendentes.

## Progressão

Este módulo independente foi desenvolvido em preview para continuar trabalho útil enquanto o ambiente real está pendente. Aprovação técnica local não é aprovação do bot no jogo. A versão final com validação real não foi declarada concluída.
