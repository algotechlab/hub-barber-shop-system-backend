<h1 align="center">Backend BARBERSHOPDG</h1>


#### Como configurar o projeto ⚙️


**Inicializando o ENV**:

```bash
# created file .env 
PORT_FLASK=5000
DEBUG = True or False
DOCS_DEV=''
SQLALCHEMY_DATABASE_URI=''

AUTHENTICATION_API_KEY=""
URL_INSTANCE_EVOLUTION= ""
EVOLUTION_APIKEY = ""
URL_WEBAPP = ""
```


**Instalando dependências**:
```bash
# install requirements 
pip install -r requirements.txt
```

**Configuração do backend**:

```bash
# exportando as variáveis de ambiente de config para coletar ao banco de dados
export FLASK_ENV=development
```

**Inicializando o servidor**:
```bash
# run server
python3 manage.py 
```





### Configurando o bot de atendimento

**Evolution api**: De acordo com api da `evolution-api` é necessário rodar o `docker-compose.yml`, onde temos a imagem mais atualizada com `atendai/evolution-api:latest`, e isso evita bugs, deixando nossas instâncias configuradas da forma correta.


**Event Webhook**: É necessário cadastrar a rotda do backend no `webhook` da `evolution-api`, estamos utilizando o `framework`: `flask-restx`, então está congigurado na rota:

```bash
# url server
http://localhost:5000
```

De acordo com á rota do servidor é necessário coloca o `ip:`, no manager do `evolution-api`


