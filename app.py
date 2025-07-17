from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import mercadopago
import datetime
from flask import render_template

app = Flask(__name__)
CORS(app, origins=["https://instaturbo.vercel.app"])

# Configuração do Mercado Pago
sdk = mercadopago.SDK('APP_USR-8369192826034467-062805-d94db51d5c00a042fa3f2c2a3b952c2b-1481851807')

# Configuração do banco de dados
db_config = {
    'host': '@metro.proxy.rlwy.net:',
    'user': 'root',
    'password': 'EGfXRIrSvUSjGIPVvKfyTuDlESMdSanE',
    'database': 'railway'
    'port': 12996
}


@app.route('/sucesso')
def sucesso():
    return render_template('sucesso.html')

@app.route('/erro')
def erro():
    return render_template('erro.html')

@app.route('/pendente')
def pendente():
    return render_template('pendente.html')

@app.route('/criar_pagamento', methods=['POST'])
def criar_pagamento():
    data = request.json
    rede_social = data.get('rede_social')
    tipo = data.get('tipo')
    quantidade = data.get('quantidade')
    link_perfil = data.get('link_perfil')

    if not (rede_social and tipo and quantidade and link_perfil):
        return jsonify({'error': 'Dados incompletos.'}), 400

    # Definir o valor unitário conforme o tipo
    precos = {
        'Seguidores': 0.01,
        'Curtidas': 0.15,
        'Visualizações': 0.10
    }

    valor_unitario = precos.get(tipo)
    if valor_unitario is None:
        return jsonify({'error': 'Tipo inválido.'}), 400

    valor_total = quantidade * valor_unitario

    descricao = (f"Compra no site https://instaturbo.vercel.app/ | "
                 f"Rede Social: {rede_social} | Tipo: {tipo} | Quantidade: {quantidade} | "
                 f"Valor Unitário: R${valor_unitario:.2f} | Valor Total: R${valor_total:.2f} | "
                 f"Link/@: {link_perfil} | Obrigado por comprar com a gente! Volte sempre.")

    preference_data = {
        "items": [
            {
                "title": descricao,
                "quantity": 1,
                "unit_price": float(valor_total)
            }
        ],
        # Você pode ajustar métodos de pagamento aqui, se quiser:
        # "payment_methods": {
        #     "excluded_payment_types": [{"id": "ticket"}],  # Excluir boleto, por exemplo
        #     "installments": 12
        # },
        "back_urls": {
            "success": "127.0.0.1:5500/sucesso.html",
            "failure": "127.0.0.1:5500/erro.html",
            "pending": "127.0.0.1:5500/erro.html"
        },
        "auto_return": "approved"
    }

    try:
        payment_response = sdk.preference().create(preference_data)
        payment = payment_response["response"]

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO pagamentos (valor_total, valor_unitario, rede_social, tipo, quantidade, link_perfil)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (valor_total, valor_unitario, rede_social, tipo, quantidade, link_perfil))
        conn.commit()

    except Exception as e:
        return jsonify({'error': 'Erro ao processar pagamento.', 'details': str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

    init_point = payment.get("init_point", "")
    return jsonify({'init_point': init_point})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
