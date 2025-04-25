# 📚 Hashtag-Based Paper Search Engine

This is the **Final Project for the 2025 Spring course "Information Storage & Retrieval"**.

We built a **hashtag-based academic paper search engine** that helps users efficiently explore and filter research papers through topic tags.

## 🎥 Project Introduction Videos

1. 🎬 **90-Second Motivation Overview**  
   👉 A brief explanation of why we built this system  
   🔗 [Watch here](https://youtu.be/20ruPgQmZak)

2. 🎬 **Full System Architecture & Demo**  
   👉 Demonstrates the user interface, system functionality, and technical architecture  
   🔗 [Watch here](https://youtu.be/7iP4rp73Pgo)


## 🚀 Download This Repo and Start Using It!
Clone the repository to get started:

```bash
git clone https://github.com/XuMingSheng/PaperHive.git
```

## 🔐 API Key Setup (OpenAI)

The following scripts and service require access to the **OpenAI API**:

- `scripts/1_paper_parser.py`  
- `scripts/3_get_hash_tag_description.py`  
- `scripts/4_generate_embedded.py`  
- `backend/services/pdf_service.py`

Please **replace or configure your OpenAI API key** before running these files.
   Replace the placeholder with your API key:
   ```python
   openai.api_key = "your-api-key-here"
   ```

## ⚙️ Environment Setup

To properly run the backend and frontend, please make sure the environment is configured correctly.

Create a `.env` file inside the `frontend/` directory and add the following environment variables:

```VITE_API_URL=http://localhost:8000```

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

## 🛠️ Data Preparation

To prepare the necessary dataset, please execute the scripts in the `scripts/` folder in the following order:

1. `1_paper_parser.py`  
2. `2_filter_hash_tag.py`  
3. `3_get_hash_tag_description.py`  
4. `4_generate_embedded.py`

Sample outputs are shown in the `sample_data/` folder.

---

## 📂 Output Files (All JSON Format)

1. **Paper Description (`papers.json`)**  
   Contains metadata about each paper:
   ```json
   {
     "id": "paper_001",
     "title": "Understanding Neural Networks",
     "authors": ["Alice Smith", "Bob Johnson"],
     "citation": 120,
     "year": 2023,
     "abstract": "This paper explores...",
     "hashtags": ["Deep Learning", "Neural Networks"]
   }


2. **Hashtag Description (`hashtags.json`)**  
   Description text for each hashtag:
   ```json
   {
   "Deep Learning": "A subset of machine learning focused on neural networks with many layers.",
   "Information Retrieval": "The process of obtaining relevant information from a large repository."
   }

3. **Hashtag Embeddings (`hashtag_embeddings.json`)**
   Embedding vectors for each hashtag:
   ```json
   {
     "Deep Learning": [0.12, 0.34, 0.56, ...],
     "Information Retrieval": [0.78, 0.90, 0.12, ...]
   }
   ```

## 🗂️ Load Data into Database

After preparing your dataset (see previous section), you can upload the data into the Elasticsearch database by running the provided script.

1. **Make sure your backend environment is set up and running** (e.g., Elasticsearch service is live).
2. **Place your processed JSON data** (paper descriptions, hashtag descriptions, and embedding vectors) into the appropriate path so they can be accessed by the script.  
   > 🔧 *The script expects the data files to be accessible via relative paths defined in `backend/scripts/upload_papers_and_hashtags.py`. Please adjust the data locations accordingly.*
3. **Navigate to the root directory** of the project.
4. **Run the following script**:

```bash
$PYTHONPATH=./backend python backend/scripts/upload_papers_and_hashtags.py
```
Ensure you run the script from the correct working directory to avoid issues with relative file paths.
If successful, you should see logs indicating progress and completion of data upload.
Once finished, your database is ready — you can now start using the system!
