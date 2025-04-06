# How to Locally Run the Applicatiion

Clone the repo: 

```bash
git clone https://github.com/XuMingSheng/PaperHive.git
```

## Running Locally by Docker

Please check you have Docker deamon running on your machine. If not, install it following https://docs.docker.com/engine/install/.

* **mac**: Open the application Docker Desktop by `open -a docker`.

### Run Server

```bash
./scripts/run_app.py
```

It builds the images for the app and database, create a named volume to store the data, and start running containers from the images.

Go to `http://localhost:3000` to view the app locally.

#### Backend URLs

* `http://localhost:8000/docs`: Swagger UI — interactive API docs
* `http://localhost:8000/redoc`: ReDoc — clean, structured API reference
* `http://127.0.0.1:8000/openapi.json`: Raw OpenAPI spec (JSON format)
 

If errors occur, you can view the log by
```bash
docker-compose logs
```
- To view the log of the backend:
    ```bash
    docker-compose logs frontend
    ```
- To view the log of the backend:
    ```bash
    docker-compose logs backend
    ```
- To view the log of the database:
    ```bash
    docker-compose logs es
    ``` 

<!-- ### Run Tests -->

<!-- #### Rspec
```
./script/run_test_rspec [rspec_args]
```

#### Cucumber
```
./script/run_test_cucumber [cucumber_args]
``` -->

### Tear Down
Use this to remove the containers.
```bash
docker-compose down [-v] [--rmi all]
```
- `-v`: remove the nameed volumes for db data.
- `--rmi`: remove the images built by docker-compose.


### Other Commands

If you want to run other commands in the docker containter, you can use 


```bash
docker-compose -f docker-compose.yml run <container_id_or_name> "<cmd>"
```

<!-- **Example**: for migrating database

```bash
docker-compose -f docker-compose.yml run eventnxt "rails db:migrate" -->