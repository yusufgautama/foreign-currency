from app.api import bp
from flask import jsonify, request, url_for

from app.api.errors import bad_request
from app.models.exchange import ExchangeRate, Exchange
from functools import partial
from datetime import datetime, timedelta
from app import db
from app.utils.common import validate_date
from sqlalchemy.sql import case


def exchange_rates_fmt(context, items):
    fmt_items = []
    start_date, end_date = context['start_date'], context['end_date']
    for id, date, from_currency, to_currency, rate in items:
        avg_rate = ExchangeRate.query.with_entities(db.func.avg(ExchangeRate.rate))\
            .filter((ExchangeRate.exchange_id == id)
                    & ((ExchangeRate.date >= start_date) & (ExchangeRate.date <= end_date)))\
            .group_by(ExchangeRate.exchange_id).first()
        exchange_rate = {'from_currency': from_currency,
                         'to_currency': to_currency,
                         'rate': rate or "insufficient data",
                         'average': avg_rate[0] if avg_rate else None}
        fmt_items.append(exchange_rate)
    return fmt_items


@bp.route('/exchange-rates/<dt>', methods=['GET'])
def get_exchange_rates(dt):
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    # initialize date and build query
    avg_range = 7
    dt_fmt = '%Y-%m-%d'
    try:
        dt_time = datetime.strptime(dt, dt_fmt)
    except Exception as e:
        return bad_request('Invalid date format')
    start_date = (dt_time - timedelta(days=avg_range - 1)).strftime(dt_fmt)
    end_date = dt_time.strftime(dt_fmt)
    context = dict(start_date=start_date,
                   end_date=end_date)
    subq = (Exchange.query.join(ExchangeRate, ExchangeRate.exchange_id == Exchange.id, isouter=True)
            .with_entities(Exchange.id,
                           case([(ExchangeRate.date != dt, None)],
                                else_=ExchangeRate.date).label('date'),
                           Exchange.from_currency,
                           Exchange.to_currency,
                           ExchangeRate.rate)
            .filter(Exchange.is_tracked == True)
            .group_by(Exchange.id,
                      case([(ExchangeRate.date != dt, None)],
                           else_=ExchangeRate.date),
                      ExchangeRate.rate)).subquery()
    query = db.session.query(subq.c.id,
                             db.func.max(subq.c.date),
                             subq.c.from_currency,
                             subq.c.to_currency,
                             subq.c.rate).group_by(subq.c.id, subq.c.from_currency, subq.c.to_currency, subq.c.rate)
    # build response with pagination
    data = Exchange.to_collection_dict(query, page, per_page, 'api.get_exchange_rates', dt=dt,
                                       formatter=partial(exchange_rates_fmt, context))
    return jsonify(data)


@bp.route('/exchange-rate', methods=['POST'])
def add_exchange_rate():
    data = request.get_json(force=True) or {}
    if any(field not in data for field in ['date', 'from_currency', 'to_currency', 'rate']):
        return bad_request('some field is missing, please check your request')
    if not validate_date(data['date'], '%Y-%m-%d'):
        return bad_request('invalid date format, please use %Y-%m-%d format')
    exchange = Exchange.query.filter_by(from_currency=data['from_currency'],
                                        to_currency=data['to_currency']).first()
    exc_rate = ExchangeRate()
    if exchange and ExchangeRate.query.filter_by(date=data['date'],
                                                 exchange_id=exchange.id).first():
        return bad_request('exchange-rate for date %s already exists' % data['date'])
    elif exchange:
        exc_rate.from_dict(data)
        exc_rate.exchange = exchange
    else:
        new_exchange = Exchange()
        new_exchange.from_dict(data)
        exc_rate.from_dict(data)
        exc_rate.exchange = new_exchange
    db.session.add(exc_rate)
    db.session.commit()
    response = jsonify(exc_rate.to_dict())
    response.status_code = 201
    return response


@bp.route('/exchange/track', methods=['PUT'])
def track_exchange():
    data = request.get_json(force=True) or {}
    if any(field not in data for field in ['from_currency', 'to_currency']):
        return bad_request('some field is missing, please check your request')
    exchange = Exchange.query.filter_by(from_currency=data['from_currency'],
                                        to_currency=data['to_currency']).first()
    if exchange and exchange.status != 1:
        exchange.track()
        db.session.commit()
    elif not exchange:
        exchange = Exchange()
        exchange.from_dict(data)
        db.session.add(exchange)
        db.session.commit()
    return jsonify({'message': 'success'})


@bp.route('/exchange/untrack', methods=['PUT'])
def untrack_exchange():
    data = request.get_json(force=True) or {}
    if any(field not in data for field in ['from_currency', 'to_currency']):
        return bad_request('some field is missing, please check your request')
    exchange = Exchange.query.filter_by(from_currency=data['from_currency'],
                                        to_currency=data['to_currency']).first()
    if exchange and exchange.status == 1:
        exchange.untrack()
        db.session.commit()
    elif not exchange:
        return bad_request('exchange %s to %s is not exist' % (data['from_currency'], data['to_currency']))
    return jsonify({'message': 'success'})
