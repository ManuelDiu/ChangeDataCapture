import datetime
import random

import faker
import psycopg2

fake = faker.Faker()


def generate_transaction():
    user = fake.simple_profile()

    return {
        'transaction_id': fake.uuid4(),
        'userId': user['username'],
        # Cambiado 'timestamp' para usar directamente datetime.datetime.now()
        'timestamp': datetime.datetime.now(),
        'amount': round(random.uniform(10, 1000), 2),
        'currency': random.choice(['UYU', 'USD', 'EUR']),
        'city': fake.city(),
        'country': fake.country(),
        'merchantName': fake.company(),
        'paymentMethod': random.choice(['credit_card', 'debit_card', 'bank_transfer']),
        'ipAddress': fake.ipv4(),
        'voucherCode': random.choice(['', 'DISCOUNT10', '']),
        'affiliateId': fake.uuid4()
    }


def create_table(conn):
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id VARCHAR(255) PRIMARY KEY,
            userId VARCHAR(255),
            timestamp TIMESTAMP,
            amount DECIMAL,
            currency VARCHAR(3),
            city VARCHAR(255),
            country VARCHAR(255),
            merchantName VARCHAR(255),
            paymentMethod VARCHAR(255),
            ipAddress VARCHAR(255),
            voucherCode VARCHAR(255),
            affiliateId VARCHAR(255)
        )
        """
    )

    cursor.close()
    conn.commit()


if __name__ == '__main__':
    conn = psycopg2.connect(
        host='localhost',
        database='financial_db',
        user='postgres',
        password='postgres',
        port=5432
    )

    create_table(conn)

    transaction = generate_transaction()
    cur = conn.cursor()
    print(transaction)

    cur.execute(
        """
        INSERT INTO transactions (transaction_id, userId, timestamp, amount, currency, city, country, merchantName, paymentMethod, ipAddress, voucherCode, affiliateId)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (transaction['transaction_id'], transaction['userId'], transaction['timestamp'], transaction['amount'],
              transaction['currency'], transaction['city'], transaction['country'], transaction['merchantName'],
              transaction['paymentMethod'], transaction['ipAddress'], transaction['voucherCode'],
              transaction['affiliateId'])
    )

    conn.commit()  # Asegurarse de confirmar la transacción
    cur.close()
    conn.close()
