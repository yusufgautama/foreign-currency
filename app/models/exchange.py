from flask import url_for
from sqlalchemy import case
from sqlalchemy.ext.hybrid import hybrid_property

from app import db
from datetime import datetime


class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, formatter=None, **kwargs):
        resources = query.paginate(page, per_page, False)
        items = resources.items
        data = {
            'items': [item.to_dict() for item in resources.items] if not formatter else formatter(items),
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page,
                                **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page,
                                **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                                **kwargs) if resources.has_prev else None
            }
        }
        return data


class Exchange(PaginatedAPIMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_currency = db.Column(db.String(12), index=True, nullable=False)
    to_currency = db.Column(db.String(12), index=True, nullable=False)
    status = db.Column(db.Integer, default=1, nullable=False)
    exchange_rates = db.relationship('ExchangeRate', backref='exchange', lazy=True)

    @hybrid_property
    def is_tracked(self):
        return True if self.status == 1 else False

    @is_tracked.expression
    def is_tracked(cls):
        return case([(cls.status == 1, True)], else_ = False)

    def untrack(self):
        if self.status != 0:
            self.status = 0

    def track(self):
        if self.status != 1:
            self.status = 1

    def to_dict(self):
        data = {
            'from_currency': self.from_currency,
            'to_currency': self.to_currency,
            'status': self.status
        }
        return data

    def from_dict(self, data):
        for field in ['from_currency', 'to_currency']:
            if field in data:
                setattr(self, field, data[field])

    def __repr__(self):
        return "<Exchange {}-{}>".format(self.from_currency, self.to_currency)


class ExchangeRate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exchange_id = db.Column(db.Integer, db.ForeignKey('exchange.id'), nullable=False)
    rate = db.Column(db.Float, nullable=False, default=0.0)
    date = db.Column(db.Date, default=datetime.utcnow)

    def to_dict(self):
        data = {
            'date': self.date.strftime('%Y-%m-%d'),
            'from_currency': self.exchange.from_currency,
            'to_currency': self.exchange.to_currency,
            'rate': self.rate
        }
        return data

    def from_dict(self, data):
        self.rate = data['rate']
        self.date = datetime.strptime(data['date'], '%Y-%m-%d')

    def __repr__(self):
        return "<ExchangeRates {}-{} {}>".format(self.exchange.from_currency, self.exchange.to_currency, self.date)