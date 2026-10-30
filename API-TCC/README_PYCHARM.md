# Clínica PSICO API — abertura no PyCharm

## 1. Abrir o projeto
1. Extraia esta pasta para um local fácil, por exemplo `C:\Projetos\API-TCC`.
2. No PyCharm, escolha **File > Open** e selecione a pasta `API-TCC` (a pasta que contém `main.py`).
3. Se o PyCharm perguntar, crie um ambiente virtual (`.venv`) para o projeto.

## 2. Instalar dependências
Abra o terminal integrado do PyCharm, confirme que está na pasta que contém `main.py` e execute:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 3. Configurar MySQL
1. Inicie o MySQL.
2. Abra o arquivo `Banco` no MySQL Workbench e execute o SQL para criar o banco `teste_api`.
3. Copie `.env.example` para um novo arquivo chamado `.env` na mesma pasta de `main.py`.
4. Edite `.env` com o usuário e a senha reais do seu MySQL. Gere também uma `SECRET_KEY` longa e aleatória. Não compartilhe o arquivo `.env`.

Exemplo de configuração local (substitua os valores):

```env
DB_USER=root
DB_PASSWORD=sua_senha_mysql
DB_HOST=localhost
DB_PORT=3306
DB_NAME=teste_api
SECRET_KEY=coloque_uma_chave_longa_e_aleatoria
FRONTEND_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000
```

## 4. Executar a API
No terminal do PyCharm:

```bash
python -m uvicorn main:app --reload
```

Deixe esse terminal aberto. Acesse:
- API: http://127.0.0.1:8000/
- Documentação/teste: http://127.0.0.1:8000/docs
- Verificação: http://127.0.0.1:8000/health

## 5. Observações
- Esta API usa MySQL e a configuração do `.env` precisa estar correta antes de iniciar.
- As tabelas atuais são criadas automaticamente ao iniciar a API.
- As rotas de usuários estão implementadas. `routers/produtos.py` está vazio e os módulos de pacientes, agenda, prontuários, financeiro e planos ainda precisam ser desenvolvidos para completar o sistema Clínica PSICO.
- Se aparecer erro, copie a mensagem completa do terminal do PyCharm para diagnosticar.
