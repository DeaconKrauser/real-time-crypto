import schedule
import time
import pymysql.cursors
import requests 
import json
import time
from datetime import date, datetime
from pytz import timezone
from requisicao import response
from bs4 import BeautifulSoup

# CONEXÃO COM O BANCO DE DADOS
con = pymysql.connect(
    host='35.247.240.81',
    port=3308, 
    user='criptocoin',
    db='criptos_coins',
    password='75ckQeI9IW', 
    cursorclass=pymysql.cursors.DictCursor
    )

# FUNÇÃO GRAVA BANCO DE DADOS
def BdiceDB():
    # prepare to cursor method .cursor()
    with con.cursor() as c:
        # consult create
        sql = "select * from coins;"
        c.execute(sql)
        res = c.fetchone()
        url_coin = res['url']
        
        # VERIFICA SE A CONEXÃO FOI REALIZADA COM SUCESSO
        html = requests.get(url_coin)
        if html.status_code == 200:
            print('Requisição bem sucedida!')
            content = html.text
        soup = BeautifulSoup(content, 'html.parser')
        
        # hora_tp = time.time()
        # hora_comum_utc = datetime.fromtimestamp(hora_tp, tz=timezone('UTC'))
        # hora_atual = datetime.fromtimestamp(hora_tp, tz=timezone('America/Sao_Paulo'))
        
        # REMOVE TEXT HTML (BAIXO | ALTO)
        soup.find('span', attrs={'class': 'highLowLabel___2bI-G'}).decompose()
        soup.find('span', attrs={'class': 'highLowLabel___2bI-G'}).decompose()
        
        # VALOR DA COTAÇÃO
        valor = soup.select_one('.priceValue___11gHJ ').text
        # VALOR DA PORCENTAGEM
        porcentagem = soup.select_one('.sc-15yy2pl-0').text
        # VALOR DA ALTA
        alta = soup.select_one('.SjVBR').text
        # VALOR DA BAIXA
        baixa = soup.select_one('.lipEFG').text

        data = datetime.now()
        data_convertida = time.strftime("%H:%M:%S %d/%m/%y")
        data_final = str(data_convertida)
        
        # COTAÇÃO ALTA PARA VERIFICAÇÃO
        cotacao_alta = '0.50'
        # COTAÇÃO BAIXA PARA VERIFICAÇÃO
        cotacao_baixa = '0.17'

        # MENSAGEM A SER EXIBIDA FORMATADA
        message = (f'Cotação: {valor}\nPorcentagem: {porcentagem}\nAlta: {alta}\nBaixa: {baixa}\nHorario da cotação: {data_final}')
        
        # INSERÇÃO DE VALOR NO BANCO DE DADOS
        c.execute(f'''insert into `criptos_coins`.`dados_coins` (`cotacao`, `porcentagem`, `alta`, `baixa`, `data_cotacao`) values ('{valor}', '{porcentagem}', '{alta}', '{baixa}', '{data_final}');''')
        con.commit()
            
        # SELECIONA O TOKEN PARA ENVIAR DISPARO/ALERTA NO TELEGRAM
        sql_token = "SELECT * FROM token"
        c.execute(sql_token)
        res = c.fetchone()
        token = res['id_token']
        
        # CONDIÇÃO DO VALOR MAIOR OU IGUAL COTAÇÃO ALTA
        if valor >= cotacao_alta:
                url_base = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={-515279731}&text={message}'
                resultado = requests.get(url_base)
                print(resultado.json())
        # CONDIÇÃO DO VALOR MENOR OU IGUAL COTAÇÃO BAIXA
        elif valor <= cotacao_baixa:
            url_base = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={-515279731}&text={message}'
            resultado = requests.get(url_base)
            print(resultado.json())
            
        # FECHA A CONEXÃO
    con.close()
BdiceDB()       
# # TEMPO DE EXECUÇÃO DE CADA TAREFA DE REQUISIÇÃO
# schedule.every(10).seconds.do(job)

# # LAÇO PARA EXECUTAR TAREFA DE REQUISIÇÃO
# while True:
#     schedule.run_pending()
#     time.sleep(1)