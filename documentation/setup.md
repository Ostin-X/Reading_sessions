## Getting Started
### **Clone the Project from GitLab:**

-   Copy the repository URL from GitLab.
-   Open a terminal and navigate to the directory where you want to save the project.
-   Execute the command:

    `git clone <repository_URL>`.

### **Run the Project in Docker using docker-compose:**

-   Make sure you have Docker and docker-compose installed.
-   Navigate to the directory containing the `docker-compose.yml` file.
-   All necessary files, like .env, are included. Do not use it this way with sensitive data
-   Execute:

    `docker-compose build`

    `docker-compose up`

Now your project should be up and running inside a Docker container. Make sure your repository files and settings are up-to-date and aligned with these steps.

## For local run and testing 

### **Install Poetry:**

To install Poetry, you can use the [official Poetry installer](https://python-poetry.org/docs/#installing-with-the-official-installer). Follow the instructions provided in the official documentation.

### **Install Project Dependencies:**

Run:

`poetry install`

### **Setup Postgres:**

- Create PostgreSQL DB on your local device and add needed data to .env.local file