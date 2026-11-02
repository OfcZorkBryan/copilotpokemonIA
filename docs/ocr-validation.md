# V3 — OCR real e publicação

Data: 1º de novembro de 2026 (America/Sao_Paulo).

## Repositório

Destino confirmado: https://github.com/OfcZorkBryan/copilotpokemonIA.
O repositório estava vazio; a V3 foi publicada e o conteúdo foi comparado com a cópia local por git fetch/diff. O histórico local preserva o commit original da V2. Não foram publicados backups pessoais nem capturas do usuário.

## Ferramentas

Tesseract 5.5.3.20260724 extraído em diretório novo de trabalho, sem executar o instalador, alterar PATH global ou instalar serviços.

- Fonte Windows recomendada pela documentação oficial: https://github.com/UB-Mannheim/tesseract/wiki.
- Binário obtido na release oficial https://github.com/tesseract-ocr/tesseract/releases/tag/5.5.3.
- SHA256 do instalador conferido com o digest da release: bee9e3434bd94fd65387d9be28cd467a41f61b1275383b55b0f59a1331270ae4.
- Modelos por/eng: tessdata_fast no commit 87416418657359cb625c412a48b6e1d6d41c29bd, fonte https://github.com/tesseract-ocr/tessdata_fast.
- eng SHA256: 7d4322bd2a7749724879683fc3912cb542f19906c83bcc1a52132556427170b2.
- por SHA256: c4932b937207a9514b7514d518b931a99938c02a28a5a5a553f8599ed58b7deb.

## Erro encontrado e corrigido

No Windows, subprocess.run(text=True) decodificava a saída UTF-8 do Tesseract usando a página de código local. O resultado continha Miss\u00c3\u00b5es em lugar de Missões, impedindo identificar a tela. Diagnóstico registrou esses pontos de código. Dois testes reais falharam antes da correção. Agora a decodificação UTF-8 é explícita.

O OCR também confundiu o dígito zero com O em um saldo sintético. Esse valor não é corrigido por suposição: permanece ausente. Um teste adicional verifica que não surge saldo não zero.

## Evidências locais

Executar na raiz, com Tesseract no PATH, por/eng instalados e Pillow disponível:

```powershell
$env:POCKET_TEST_REAL_OCR='1'
python -m unittest discover -s tests -v
node tests/ui_smoke_node.js
```

Resultado: 28 testes Python passaram, sem skips nessa execução; smoke JavaScript passou. Cinco testes percorrem PNG sintético gerado por Pillow → importação HTTP → Tesseract real → reconhecimento, sem substituir os subprocessos OCR. Os casos são coleção, missões, recursos, tela desconhecida e zero ambíguo. Isso não mede a precisão nas telas reais do Pokémon TCG Pocket.

## Ambiente Android

Localizado MSI App Player em C:/Program Files/BlueStacks_msi5, com executável de assinatura válida. A tentativa de abertura exibiu uma solicitação de permissão do Windows; não foi aceita automaticamente. HD-Adb devices não listou Androids. A configuração consultada informa acesso ADB desativado; não foi alterada. Não foram instalados jogo, APK, conta ou ferramentas de bypass.

Para testes no jogo, falta disponibilizar o emulador em execução ou capturas reais. Não há validação de coleção/missões/recursos reais nem fundamento para liberar V4. As restrições de somente leitura continuam em vigor. Termos oficiais consultados: https://www.pokemon.com/uk/legal/terms-of-use.
