# Relatório verificável — V3 preview

Data local: 1º de novembro de 2026, America/Sao_Paulo.

Atualização posterior nesta mesma data: publicado em OfcZorkBryan/copilotpokemonIA; 28 testes Python aprovados, incluindo cinco com OCR real sobre imagens sintéticas. Veja `ocr-validation.md` e o log atualizado `verification.txt`. Os resultados abaixo registram a primeira entrega de 23 testes; indisponibilidades do ambiente nessa primeira inspeção foram parcialmente resolvidas depois.

## Origem e preservação

ZIP recebido: pocket-autopilot-v2 (1).zip, 25929 bytes.
SHA256: F95763A8C2EF830BCCF9478807D52995D257AC3F0FA9DA814435763CB073C7C1.
Commit original V2: 24ca855. Desenvolvimento em feat/v3-recognition.
ZIP de origem não modificado. Nenhum backup pessoal ou captura real veio no arquivo. A chave localStorage, reserva e formato JSON da V2 foram mantidos.

## Base V2 reproduzida

- Python unittest: 6 testes, 5 aprovados e 1 falha em test_fake_adb_capture.
- Causa: subprocesso tentava executar diretamente um script .py por shebang, incompatível com CreateProcess no Windows.
- Correção no teste: executar o simulador usando sys.executable, mantendo subprocesso real e sem alterar adb_bridge.py de produção.
- Smoke JavaScript original: aprovado.

## Marco técnico V3

Comandos na raiz do projeto:

```text
python -m unittest discover -s tests -v
node tests/ui_smoke_node.js
```

Executados com Python 3.12 e Node 24.19.0 disponíveis no ambiente de trabalho.

- 23 testes Python aprovados: 15 do parser e 8 do servidor HTTP.
- Smoke JavaScript aprovado: painel, decks, inventário, leitor visual, recursos e apresentação V3.
- Conteúdo OCR escapado; comparação de estado e armazenamento confirmou ausência de alteração ao renderizar candidatos, incluindo reserva e ampulhetas.
- Testes de tela desconhecida, cabeçalhos conflitantes, PT/EN, zero, milhares, números ilegíveis/negativos, duplicatas, progresso de missões e separação entre recompensa e saldo.
- Teste HTTP real de reconhecimento com resposta OCR substituída por fixture. Disponibilidade e falha de OCR verificadas com simulação controlada.
- ADB simulado executa um processo local e devolve PNG mínimo. Não é um emulador nem um dispositivo Android.
- Aplicativo iniciado em 127.0.0.1:8765 e aberto em navegador real. Aba Leitor visual e captura de tela da interface inspecionadas: painel carregou e informou ADB ausente, com captura/monitoramento desabilitados. Não foi uma análise de imagem do jogo.

## Revisão de código

Uma revisão independente identificou dois problemas: progresso conflitante em missões repetidas e conversão de número com 4500 dígitos. Ambos foram reproduzidos em testes que falharam antes da correção. O parser agora omite conflitos, remove duplicatas idênticas e limita o número antes de convertê-lo. A suíte completa passou após a correção.

## O que não foi validado

- OCR real de imagens: não executado; Tesseract não foi encontrado no PATH nem no local padrão consultado.
- Capturas reais de coleção, missões ou recursos: não fornecidas.
- Android ou emulador real: nenhum conectado ou utilizado nesta sessão. Não foi localizado emulador nas entradas de instalação consultadas; isso não demonstra ausência em outras pastas.
- Testes dentro do jogo, resgates, gastos e partidas: não executados.
- Precisão estatística do reconhecimento: não medida. As regras não oferecem probabilidade calibrada.
- Dados atuais do meta e termos do jogo: não revalidados neste marco. Nenhuma automação de ações foi adicionada.

## Próximo portão de validação

Fornecer capturas PNG reais rotuladas das três telas, sem dados pessoais quando possível, ou disponibilizar o emulador autorizado. Comparar a saída com os valores visíveis, incluir também telas desconhecidas e casos ambíguos, registrar erros e corrigir antes de considerar V3 validada. Não avançar à V4 com base somente nos testes sintéticos.

## Repositório remoto

Repositório Git local criado. Publicação destinada a OfcZorkBryan/pocket-autopilot. A sessão do navegador inicialmente estava em trabalhoszorkinhas; o usuário escolheu OfcZorkBryan e fará a troca do login. Não publicar na outra conta. A conexão GitHub disponível não possui criação de repositório.
