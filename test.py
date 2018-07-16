#!/usr/bin/env python
from datetime import datetime, timedelta
import unittest
from app import create_app, db
from app.models.exchange import ExchangeRate, Exchange
from config import Config
import json


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://dbuser:dbpassword@192.168.99.100/foreign_currency'


class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_post_exchange_api(self):
        data_dict = {
                        "date": "2018-07-11",
                        "from_currency": "JPY",
                        "to_currency": "IDR",
                        "rate": 120.1
                    }
        data = json.dumps(data_dict)
        rsp = self.client.post('/api/exchange-rate', data=data)
        self.assertEqual(rsp.status_code, 201)
        self.assertDictEqual(data_dict, json.loads(rsp.data))

    def test_track_exchange(self):
        ec = Exchange(from_currency='EUR', to_currency='USD')
        db.session.add(ec)
        db.session.commit()

        self.assertTrue(ec.is_tracked)
        ec.untrack()
        self.assertFalse(ec.is_tracked)
        ec.track()
        self.assertTrue(ec.is_tracked)

    def test_track_exchange_api(self):
        ec = Exchange(from_currency='EUR', to_currency='USD')
        db.session.add(ec)
        db.session.commit()

        ec_body = json.dumps({'from_currency': 'EUR', 'to_currency': 'USD'})
        self.assertTrue(ec.is_tracked)

        rsp = self.client.put('/api/exchange/untrack', data=ec_body)

        self.assertEqual(json.loads(rsp.data)['message'], 'success')
        self.assertFalse(ec.is_tracked)

        rsp = self.client.put('/api/exchange/track', data=ec_body)

        self.assertEqual(json.loads(rsp.data)['message'], 'success')
        self.assertTrue(ec.is_tracked)

    def test_exchange_list(self):
        ec1 = Exchange(from_currency='EUR', to_currency='USD')
        ec2 = Exchange(from_currency='USD', to_currency='JPY')
        date_fmt = '%Y-%m-%d'
        ecr1 = ExchangeRate(exchange=ec1, date=datetime.strptime('2018-07-13', date_fmt), rate=1.168)
        ecr2 = ExchangeRate(exchange=ec2, date=datetime.strptime('2018-07-13', date_fmt), rate=112.379)

        self.assertEqual(ExchangeRate.query.all(), [])

        db.session.add(ecr1)
        db.session.add(ecr2)
        db.session.commit()

        self.assertEqual(len(ExchangeRate.query.all()), 2)

        query_by_tracked = Exchange.query.join(ExchangeRate,
                                    ExchangeRate.exchange_id == Exchange.id, isouter=True)\
                            .filter(Exchange.is_tracked == True)

        self.assertEqual(len(query_by_tracked.all()), 2)

        ec1.untrack()
        db.session.commit()

        self.assertEqual(len(query_by_tracked.all()), 1)

        ec2.untrack()
        db.session.commit()

        self.assertEqual(len(query_by_tracked.all()), 0)

        ec1.untrack()
        ec2.untrack()
        db.session.commit()

        self.assertEqual(len(query_by_tracked.all()), 0)

        ec1.track()
        ec2.track()
        db.session.commit()

        self.assertEqual(len(query_by_tracked.all()), 2)

    def test_exchange_list_api(self):
        to_dict = lambda r: json.loads(r.data)

        rsp = self.client.get('/api/exchange-rates/2018-07-13')
        self.assertEqual(len(to_dict(rsp)['items']), 0)

        ec1 = Exchange(from_currency='EUR', to_currency='USD')
        ec2 = Exchange(from_currency='USD', to_currency='JPY')
        ec3 = Exchange(from_currency='JPY', to_currency='IDR')

        db.session.add(ec1)
        db.session.add(ec2)
        db.session.add(ec3)
        db.session.commit()

        rsp = self.client.get('/api/exchange-rates/2018-07-13')
        dict_rsp = to_dict(rsp)
        self.assertEqual(len(dict_rsp), 3)
        self.assertTrue(all(r['rate'] == 'insufficient data' for r in dict_rsp['items']))

        date_fmt = '%Y-%m-%d'
        ecr1 = ExchangeRate(exchange=ec1, date=datetime.strptime('2018-07-13', date_fmt), rate=1.168)
        ecr2 = ExchangeRate(exchange=ec2, date=datetime.strptime('2018-07-13', date_fmt), rate=112.379)

        db.session.add(ecr1)
        db.session.add(ecr2)
        db.session.commit()

        rsp = self.client.get('/api/exchange-rates/2018-07-13')
        dict_rsp = to_dict(rsp)
        self.assertEqual(len(dict_rsp), 3)
        exchange_without_rate = [r for r in dict_rsp['items'] if r['rate'] == 'insufficient data']
        self.assertEqual(len(exchange_without_rate), 1)
        self.assertTrue(all([exchange_without_rate[0]['from_currency'] == 'JPY',
                             exchange_without_rate[0]['to_currency'] == 'IDR']))

        ecr1_item = [r for r in dict_rsp['items'] if r['from_currency'] == 'EUR' and r['to_currency'] == 'USD'][0]
        self.assertEqual(ecr1_item['average'], 1.168)

        ecr4 = ExchangeRate(exchange=ec1, date=datetime.strptime('2018-07-12', date_fmt), rate=1.01)
        ecr5 = ExchangeRate(exchange=ec1, date=datetime.strptime('2018-07-11', date_fmt), rate=0.92)
        ecr6 = ExchangeRate(exchange=ec1, date=datetime.strptime('2018-07-10', date_fmt), rate=1.23)

        db.session.add(ecr4)
        db.session.add(ecr5)
        db.session.add(ecr6)
        db.session.commit()

        rsp = self.client.get('/api/exchange-rates/2018-07-13')
        dict_rsp = to_dict(rsp)

        ecr1_item = [r for r in dict_rsp['items'] if r['from_currency'] == 'EUR' and r['to_currency'] == 'USD'][0]
        self.assertAlmostEqual(ecr1_item['average'], (1.168 + 1.01 + 0.92 + 1.23) / float(4))

if __name__ == '__main__':
    unittest.main(verbosity=2)
