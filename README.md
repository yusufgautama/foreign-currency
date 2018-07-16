# Foreign Currency
Simple API to track exchange rates. Build with Flask using python 3.6, use Postgres and alembic for migration.

### Installing

Simply clone this repository and build it with docker:

```
docker-compose build
```
```
docker-compose up -d
```
```
docker-compose app python manage.py recreate_db
```

Sometimes postgres had a slow booting up, retry if needed.

## Running

Kindly follow the [API documentation](https://github.com/yusufgautama/foreign-currency/blob/master/doc/API.md).

## Testing

```
python -m unittest test
```

## Reference

Quick explanation about database and design can be found [here](https://github.com/yusufgautama/foreign-currency/blob/master/doc/DB.md).

## Authors

* **Yusuf Pradana Gautama** - [yusufgautama](https://github.com/yusufgautama)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details