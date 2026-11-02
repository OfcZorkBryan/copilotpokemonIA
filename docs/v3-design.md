# V3 — primeiro marco de reconhecimento

Continuação da V2 importada do ZIP SHA256 F95763A8C2EF830BCCF9478807D52995D257AC3F0FA9DA814435763CB073C7C1. A cópia original permanece em work/v2-original. Nenhum backup pessoal veio no ZIP.

Usar o OCR opcional existente, com regras conservadoras de texto, é a extensão escolhida para este marco. Um classificador treinado exigiria capturas rotuladas que ainda não foram fornecidas. Coordenadas fixas seriam frágeis sem conhecer resolução e versão do jogo.

Identificar cabeçalhos de coleção, missões e recursos nas três primeiras linhas não vazias. Devolver desconhecida quando houver conflito, ausência de cabeçalho ou texto insuficiente. Extrair somente pares explícitos de rótulo e quantidade e progressos de missão. Toda leitura é candidata e exige revisão. Não converter nomes de cartas ou variantes em entradas do inventário automaticamente.

Não modificar localStorage, a chave pocket-autopilot-v1, reservas ou formato do backup. Não enviar comandos novos ao Android. Sem gastos, resgates ou partidas automatizadas. Dados de decks herdados são históricos, não revalidados neste marco.

O marco técnico exige testes do parser, da integração HTTP e da apresentação, incluindo entradas desconhecidas, valores ambíguos e preservação dos saldos. Validação visual no jogo exige capturas reais rotuladas; aprovação técnica com dados sintéticos não libera a V4.

