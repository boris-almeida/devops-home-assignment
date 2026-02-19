# Tech 42 – DevOps Engineer Home Assignment

This repository contains a small FastAPI application and schema. Your task is to containerize it, implement caching and user-read endpoints, then deploy it to AWS using Terraform, Helm, and EKS with Aurora RDS and ElastiCache.

**Expected effort:** We expect this assignment to take about 1–2 days depending on your experience.

---

## Requirements (what we expect you to demonstrate)

- [ ] **Programming** – Implement or extend application logic (cache layer, API endpoints).
- [ ] **Containers** – Docker image(s) for the app, used in EKS.
- [ ] **AWS knowledge and best practices** – We expect your solution to reflect AWS knowledge and best practices (security, networking, IAM, resource sizing, and operational habits).

---

## Tools you must use

| Area         | Tool / topic     | What we look for |
| ------------ | ---------------- | ---------------- |
| **Kubernetes** | EKS              | Cluster and workloads running the app. |
|               | Ingress or Gateway | External access to the app (approach is up to you). |
|               | Secret management | How you provide DB and cache credentials to the app (we will review your approach). |
|               | Helm             | Application deployed via Helm chart(s). |
| **IaC**      | Terraform        | All AWS and EKS resources defined in Terraform. |
|               | RDS              | Aurora (PostgreSQL) for the database. |
|               | VPC              | VPC, subnets, and networking for EKS, RDS, ElastiCache. |
|               | EKS              | EKS cluster and node group(s) provisioned with Terraform. |
| **Source control** | Public GitHub repo | Clean history, clear use of branches (e.g. `main`, `develop`, feature branches). |

---

## Tasks

### 1. Run locally with Docker Compose

To test changes locally, use the provided `docker-compose.yml`. It runs Postgres, Redis, and the API (Acme Corp on port 8000).

**Prerequisites:** Docker and Docker Compose.

From the repository root:

```bash
docker compose up --build
```

Once the services are healthy:

- **API** – http://localhost:8000 (API docs: http://localhost:8000/docs)

Stop with `Ctrl+C` or `docker compose down`.

### 2. Docker container for the application

- [ ] Add or finalize a **Dockerfile** that builds and runs the FastAPI app.
- [ ] The container should read configuration from **environment variables**; do not hardcode secrets.
- [ ] Document how to build and run the image locally.

### 3. Application behavior and caching

- [ ] The app must **write to an Aurora RDS (PostgreSQL) database** and **cache responses in ElastiCache (Redis)**.
- [ ] It must **display the company name** from the `COMPANY_NAME` environment variable in the API.
- [ ] Implement **two read paths with caching (if needed)**: **user by ID** and **all users**. Read from the database, store in cache, and serve from cache when valid. Use the existing `users` table and schema.

### 4. Infrastructure as Code (Terraform)

- [ ] Use **Terraform** to manage **VPC** (subnets, security groups, networking for EKS, RDS, ElastiCache), **Aurora RDS** (PostgreSQL), **ElastiCache** (Redis), and **EKS** (cluster, node group(s), IAM as needed). Use a structure that is easy to follow.

### 5. Helm chart for deployment

- [ ] Provide a **Helm chart** that deploys the application to EKS (Deployment(s), Service(s), HPA if applicable, configuration via values). **Secret management**: database and Redis credentials must not be hardcoded or stored in plain text in manifests or values. How you provide them (e.g. AWS Secrets Manager, Parameter Store, or another approach) is up to you—we will assess your solution.

### 6. Ingress or Gateway

- [ ] Expose the application so it is reachable from outside the cluster. Use **Kubernetes Ingress** or **Gateway API**—implementation is up to you. You must be able to reach the app and see the `COMPANY_NAME` in the response.

### 7. Git and GitHub

- [ ] Use a **public GitHub repository** for the assignment. Show clear use of branches and meaningful commit history.

### 8. Jupyter notebook for API testing

- [ ] Provide a **Jupyter notebook** that uses HTTP requests to test all API steps: create user, get user by ID, get all users. The notebook should be runnable and document each step.

---

## Reference

### Repository structure (starter)

```
├── code/                 # FastAPI application
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── sql/
│   └── schema.sql        # PostgreSQL schema (users)
├── docker-compose.yml    # Local run (Postgres + Redis + app)
└── README.md             # This file
```

You will add (for example):

- [ ] `terraform/` – Terraform modules and root config for VPC, RDS, ElastiCache, EKS.
- [ ] `helm/` or `charts/` – Helm chart(s) for the application.

See **Task 1** for how to run the application locally with Docker Compose.

### AWS resources and cost

Use the **smallest viable sizes** for this assignment to avoid unnecessary cost. We only need the stack to run so you can demonstrate it, not to handle production load.

- [ ] **EKS** – Small node instance type (e.g. `t3.small`), **one single node**. Tear down the cluster when you are done.
- [ ] **Aurora (PostgreSQL)** – Small instance class (e.g. `db.t3.medium` or Aurora Serverless v2 with minimum capacity). Single instance is enough.
- [ ] **ElastiCache (Redis)** – Small node type (e.g. `cache.t3.micro` or `cache.t4g.micro`), single node.
- [ ] **Remember to destroy** all Terraform-managed resources (e.g. `terraform destroy`) and delete any ECR images when you finish, so you are not charged after the assignment.

**Approximate cost** (us-east-1, on-demand, with ALB for Ingress): ~**$0.25–0.30 per hour**, or ~**$6–8 per day** (EKS control plane ~$0.10/hr, one t3.small node ~$0.02/hr, Aurora db.t3.medium ~$0.08/hr, ElastiCache cache.t3.micro ~$0.02/hr, ALB ~$0.03/hr, plus storage). Prices vary by region and over time; run only as long as needed and destroy when done.

### Environment variables

**API service**

| Variable           | Description                              | Default (in code) | Example            |
| ------------------ | ---------------------------------------- | ------------------ | ------------------ |
| `COMPANY_NAME`     | Company name shown in API title/description | `My Company`       | `Acme Corp`         |
| `POSTGRES_HOST`    | PostgreSQL (Aurora) hostname             | `localhost`        | RDS endpoint       |
| `POSTGRES_DB`      | PostgreSQL database name                 | `mydb`             | `db1`              |
| `POSTGRES_USER`    | PostgreSQL username                      | `postgres`         | —                  |
| `POSTGRES_PASSWORD`| PostgreSQL password                      | `postgres`         | —                  |
| `REDIS_HOST`       | Redis (ElastiCache) hostname             | `localhost`        | ElastiCache endpoint |
| `REDIS_PORT`       | Redis port                               | `6379`             | `6379`             |

In EKS, credentials must not be hardcoded; how you supply them is part of the assignment.

**Postgres (Aurora / local)**

| Variable           | Description          | Example    |
| ------------------ | -------------------- | ---------- |
| `POSTGRES_USER`    | PostgreSQL user      | `postgres` |
| `POSTGRES_PASSWORD`| PostgreSQL password  | —          |
| `POSTGRES_DB`      | Database name        | `db1`      |

---

## Deliverables

- [ ] **Terraform code** – That deploys the cluster and AWS resources.
- [ ] **Helm chart** – To deploy the application in the cluster.
- [ ] **Jupyter notebook** – HTTP requests to test all API steps (create user, get user by ID, get all users). Runnable and documented.
- [ ] **Public GitHub repo** – Link in your submission; ensure it's accessible and branches are used as described above.

---

Good luck.
