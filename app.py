from flask import Flask, render_template, request, redirect, url_for
import psycopg2

app = Flask(__name__)

DATABASE = {
    'dbname': 'Patrimonios',
    'user': 'postgres',
    'password': '15121516Ab',
    'host': 'localhost',
    'port': '5432',
}

def create_table():
    with psycopg2.connect(**DATABASE) as conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS patrimonios (
                    id SERIAL PRIMARY KEY,
                    patrimonio TEXT NOT NULL,
                    equipamento TEXT NOT NULL,
                    configuracoes TEXT,
                    numero_serie TEXT,
                    responsavel TEXT,
                    localizacao_empresa TEXT,
                    informacoes_adicionais TEXT,
                    data_entrega DATE,
                    data_devolucao DATE
                )
            ''')
            conn.commit()
        except psycopg2.Error as e:
            print(f"Erro ao criar a tabela: {e}")
            conn.rollback()
        else:
            conn.commit()

# Chama a função apenas uma vez durante a inicialização
create_table()

@app.route('/')
def index():
    search_query = request.args.get('search', '')
    search_field = request.args.get('search_field', 'patrimonio')  # Padrão para 'patrimonio' se não especificado

    with psycopg2.connect(**DATABASE) as conn:
        try:
            cursor = conn.cursor()
            if search_query:
                # Ajuste a consulta SQL com base no campo de busca selecionado
                cursor.execute(f'SELECT * FROM patrimonios WHERE {search_field} ILIKE %s', ('%' + search_query + '%',))
            else:
                cursor.execute('SELECT * FROM patrimonios')

            patrimonios = cursor.fetchall()
        except psycopg2.Error as e:
            print(f"Erro ao recuperar dados do banco de dados: {e}")
            patrimonios = []

    return render_template('index.html', patrimonios=patrimonios)

@app.route('/cadastro')
def cadastro():
    with psycopg2.connect(**DATABASE) as conn:
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM patrimonios')
            patrimonios = cursor.fetchall()
        except psycopg2.Error as e:
            print(f"Erro ao recuperar dados do banco de dados: {e}")
            patrimonios = []
    return render_template('cadastro.html', patrimonios=patrimonios)

@app.route('/adicionar', methods=['POST'])
def adicionar():
    patrimonio = request.form['patrimonio']
    equipamento = request.form['equipamento']
    configuracoes = request.form.get('configuracoes', '')
    numero_serie = request.form.get('numero_serie', '')
    responsavel = request.form.get('responsavel', '')
    localizacao_empresa = request.form.get('localizacao_empresa', '')
    informacoes_adicionais = request.form.get('informacoes_adicionais', '')
    data_entrega = request.form.get('data_entrega', None)

    with psycopg2.connect(**DATABASE) as conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO patrimonios (
                    patrimonio, equipamento, configuracoes, numero_serie,
                    responsavel, localizacao_empresa, informacoes_adicionais,
                    data_entrega
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                patrimonio, equipamento, configuracoes, numero_serie,
                responsavel, localizacao_empresa, informacoes_adicionais,
                data_entrega
            ))
            conn.commit()
        except psycopg2.Error as e:
            print(f"Erro ao adicionar patrimônio: {e}")
            conn.rollback()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
