**Add Exchange Rate**
----


* **URL**

  `/api/exchange-rate`

* **Method:**

  `POST`

* **Data Params**

    ```json
    {"date": "2018-07-13", "from_currency": "USD", "to_currency": "JPY", "rate": 121.0}
    ```

* **Headers**

    `Content-Type` : `application/json`

* **Success Response:**

  * **Code:** 201 `Resource created`<br />
    **Content:**
    ```json
    {"date": "2018-07-13", "from_currency": "USD", "to_currency": "JPY", "rate": 121.0}
    ```

* **Error Response:**

  * **Code:** 400 Bad Request <br />
    **Content:**
    ```json
    { "error" : "Bad Request" ,
      "message": "some field is missing, please check your request"}
    ```

* **Sample Call:**

  `curl -d '{"date": "2018-07-13", "from_currency": "USD", "to_currency": "JPY", "rate": 121.0}' -H "Content-Type: application/json" -X POST http://192.168.99.100:5000/api/exchange-rate`


**Exchange Rate List**
----


* **URL**

  `/api/exchange-rates/{date}`

  date format: `%Y-%m-%d`

* **Method:**

  `GET`

*  **URL Params**

   **Optional:**

   - pagination

     `page=[numeric]&per_page=[numeric]`


* **Headers**

    `Accept` : `application/json`

* **Success Response:**

  * **Code:** 200 <br />
    **Content:**
    ```json
    {
    "_links": {
        "next": null,
        "prev": null,
        "self": "/api/exchange-rates/2018-07-12?page=1&per_page=10"
    },
    "_meta": {
        "page": 1,
        "per_page": 10,
        "total_items": 0,
        "total_pages": 0
    },
    "items": [
        {
            "from_currency": "USD",
            "to_currency": "JPY",
            "rate": 121.0,
            "average": 119.1
        }
    ]
    }
    ```

* **Error Response:**

  * **Code:** 400 Bad Request <br />
    **Content:**
     ```json
    { "error" : "Bad Request" ,
      "message": "Invalid date format"}
    ```

* **Sample Call:**

  `curl -H "Accept: application/json" -X GET http://192.168.99.100:5000/api/exchange-rates/2018-07-13`

**Track/Untrack Exchange**
----


* **URL**

  `/api/exchange/{action}`

  action = `track/untrack`

* **Method:**

  `PUT`

* **Data Params**

    ```json
    {"from_currency": "USD", "to_currency": "JPY"}
    ```

* **Headers**

    `Content-Type` : `application/json`

* **Success Response:**

  * **Code:** 201 `Resource created`<br />
    **Content:**
    ```json
    {"message": "success"}
    ```

* **Error Response:**

  * **Code:** 400 Bad Request <br />
    **Content:**
    ```json
    { "error" : "Bad Request" ,
      "message": "some field is missing, please check your request"}
    ```

* **Sample Call:**

  `curl -d '{"from_currency": "USD", "to_currency": "JPY"}' -H "Content-Type: application/json" -X PUT http://192.168.99.100:5000/api/exchange/track`