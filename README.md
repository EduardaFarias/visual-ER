# 📊 visual-ER
Este projeto automatiza a criação de Diagramas Entidade-Relacionamento (DER) visuais a partir de strings JSON. Ele processa a definição das tabelas e gera arquivos ```.png``` e ```.svg``` utilizando o motor do Graphviz.


## 🛠️ Pré-requisitos
Antes de iniciar, você precisa ter duas coisas instaladas na sua máquina:

Python (versão 3.8 ou superior)

Graphviz (O software de renderização)

📥 Download do Graphviz
O script depende do executável dot do Graphviz. Instale-o através do link abaixo de acordo com seu sistema operacional:

[🔗 Baixar Graphviz (Windows, Linux, Mac)](https://graphviz.org/download/)

⚠️ Importante para usuários Windows: Durante a instalação, marque a opção "Add Graphviz to the system PATH for all users" (Adicionar ao PATH). Sem isso, o Python não conseguirá encontrar o comando dot.

## 🚀 Instalação (Primeira vez)
Siga os passos abaixo para configurar o ambiente virtual e instalar as dependências do projeto.

No seu terminal (dentro da pasta do projeto), execute:

### 1. Cria o ambiente virtual (.venv)
```python -m venv .venv```

### 2. Ativa o ambiente virtual (Windows)
```.\.venv\Scripts\activate```

# (Se estiver no Linux/Mac use: source .venv/bin/activate)

### 3. Instala a biblioteca ERDot (opcional, se for usar o gerador externo)
```pip install ERDot```

### 4. (Opcional) Instala a lib python do graphviz se necessário
```pip install graphviz```

### ✅ Verificando a instalação
Para garantir que tudo foi instalado corretamente e o PATH está configurado, rode os comandos de teste:

### Verifica se o ERDot foi instalado no Python
```erdot --help```

### Verifica se o software Graphviz está acessível pelo sistema
```dot -v```
Se o comando dot -v der erro, reinicie o seu terminal ou computador após instalar o Graphviz.

### ▶️ Como Usar (No dia a dia)
Sempre que for trabalhar no projeto, você só precisa ativar o ambiente e rodar o script.

Ative o ambiente:

```.\.venv\Scripts\activate```
Edite o Input: Abra o arquivo ```script.py``` e cole sua string JSON na variável ERD_INPUT.

Execute o script:

```python erd_full_pipeline.py```
Verifique o resultado: Os diagramas gerados estarão na pasta: 📂 output/