### Schema

![alt text](https://github.com/yusufgautama/foreign-currency/blob/master/doc/foreign_db.PNG)

For this project, it doesn't need to create a complex table schema.

A basic one to many relationship can do the job, actually it can be achieved by using one table only.

But to get rid of redudancy, we need to separate the exchange and the exchange rate which is a periodical log.

Can also make it simple and clean using SQL Alchemy.

```
class Exchange(PaginatedAPIMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_currency = db.Column(db.String(12), index=True, nullable=False)
    to_currency = db.Column(db.String(12), index=True, nullable=False)
    status = db.Column(db.Integer, default=1, nullable=False)
    exchange_rates = db.relationship('ExchangeRate', backref='exchange', lazy=True)
```

So this relationship can be bidirectional because it has back reference, and we can specify the querying strategy to lazy for efficiency.