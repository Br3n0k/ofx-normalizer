# OFX Normalizer

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey.svg)](README.md)

Um normalizador de arquivos OFX moderno e cross-platform para compatibilidade com Microsoft Money e outros softwares de finanças pessoais legados.

## 🚀 Características Principais

- **Interface Dupla**: CLI para automação e GUI para uso interativo
- **Cross-Platform**: Funciona no Windows e Linux/Unix
- **Arquitetura Modular**: Estrutura MVC bem organizada
- **Detecção Automática**: Escolhe automaticamente a interface apropriada
- **Compatibilidade Total**: Testado com Microsoft Money e OFX 1.02/2.0

## 📁 Estrutura do Projeto

```
src/
├── normalizer/     # Lógica de normalização (Model)
├── helpers/        # Controle de fluxo (Controller)  
├── config/         # Configurações da aplicação
└── views/          # Interfaces de usuário (View)
```

## 🛠️ Instalação

### Pré-requisitos
- Python 3.8+
- CustomTkinter (para interface gráfica no Windows)

### Instalação das dependências
```bash
pip install customtkinter
```

## 📖 Como Usar

### Interface CLI (Linha de Comando)
```bash
# Normalizar um arquivo específico
python main.py "caminho/para/arquivo.ofx"

# Exemplo prático
python main.py "FEVEREIRO_ITAU.ofx"
```

### Interface GUI (Gráfica)
```bash
# Abrir interface gráfica (apenas no Windows)
python main.py
```

## ⚙️ Funcionalidades de Normalização

### 🔧 Correções Automáticas
- **Codificação**: Converte para CP1252 com `CHARSET:1252` e `ENCODING:USASCII`
- **Quebras de linha**: Força CRLF para compatibilidade Windows
- **Datas**: Remove sufixos de timezone mantendo formato `yyyymmddhhmmss`
- **Caracteres de controle**: Remove caracteres ASCII problemáticos
- **Blocos de transação**: Reorganiza `<NAME>` antes de `<MEMO>`

### 🛡️ Proteções de Integridade
- **Valores preservados**: Mantém intactos valores, FITID e sinais
- **Remoção segura**: Remove apenas blocos `<BALLIST>` completos
- **Validação**: Preserva `<BANKTRANLIST>` e dados essenciais

## 🖥️ Compatibilidade de Sistema

| Sistema | CLI | GUI | Status |
|---------|-----|-----|--------|
| Windows | ✅ | ✅ | Totalmente suportado |
| Linux   | ✅ | ❌ | CLI disponível |
| macOS   | ✅ | ❌ | CLI disponível |

## 📋 Exemplos de Uso

### Processamento em Lote (CLI)
```bash
# Processar múltiplos arquivos
for file in *.ofx; do python main.py "$file"; done
```

### Integração com Scripts
```python
from src.normalizer import Normalizer

normalizer = Normalizer()
result = normalizer.normalize_file("arquivo.ofx")
```

## 🔧 Configuração

O arquivo de configuração permite personalizar:
- Limite máximo para campo `<NAME>` (padrão: 32 caracteres)
- Codificação de saída
- Comportamento de tratamento de erros

## 🧪 Validação

Para melhores resultados:
1. Valide o arquivo de saída com OFX Analyzer/Formatter
2. Verifique se não há erros de parsing
3. Confirme totais e unicidade antes de importar

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Abra uma issue descrevendo o problema/melhoria
2. Faça fork do projeto
3. Crie uma branch para sua feature
4. Submeta um Pull Request

### Diretrizes
- Mantenha mudanças conservadoras e focadas em compatibilidade
- Adicione testes quando aplicável
- Siga os padrões de código existentes

## 🗺️ Roadmap

- [ ] Opções CLI avançadas (configurações personalizáveis)
- [ ] Heurísticas específicas por banco (Itaú, Nubank, Sicoob, etc.)
- [ ] Suporte a múltiplos formatos de saída
- [ ] Interface web opcional
- [ ] Testes automatizados abrangentes

## 📄 Licença

MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👨‍💻 Desenvolvimento

**Desenvolvido por**: [Brendown Ferreira (Br3n0k)](https://github.com/Br3n0k)  
**Empresa**: NokTech  
**Versão**: 2.0.0

### Links Úteis
- [Código Fonte](https://github.com/Br3n0k/ofx-normalizer)
- [Issues](https://github.com/Br3n0k/ofx-normalizer/issues)
- [Releases](https://github.com/Br3n0k/ofx-normalizer/releases)

## 🙏 Agradecimentos

- Comunidade open-source por manter workflows de finanças legados
- Usuários que testaram e forneceram feedback
- Contribuidores do projeto

---

**💡 Dica**: Para uso corporativo ou integração em sistemas maiores, considere usar a API modular através dos módulos em `src/`.