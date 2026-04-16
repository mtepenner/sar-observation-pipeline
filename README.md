# 🌍 SAR Observation Pipeline

A distributed, high-performance data processing and visualization pipeline for Synthetic Aperture Radar (SAR) imagery. This system automates the ingestion of Sentinel-1 radar data, performs rigorous radiometric calibration and change detection, and serves the computed metrics as dynamic vector tiles to an interactive WebGL mapping dashboard.

## 📑 Table of Contents
- [Features](#-features)
- [Architecture](#-architecture)
- [Technologies Used](#-technologies-used)
- [Installation](#-installation)
- [Usage](#-usage)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Features
* **Automated Data Ingestion:** Uses Apache Airflow to schedule and pull raw Sentinel-1 GRD/SLC data from the Alaska Satellite Facility (ASF) API.
* **Advanced Radar Processing:** Performs radiometric calibration, Lee/Frost speckle filtering, and terrain correction over a digital elevation model (DEM).
* **Automated Change Detection:** Computes temporal differences (e.g., deforestation, ice shelf collapse) and vectorizes raster changes into searchable polygons.
* **High-Performance Spatial API:** A FastAPI backend that serves dynamic Mapbox Vector Tiles (MVT) and handles complex temporal time-series queries against a PostGIS database.
* **WebGL Visualization Dashboard:** A React and TypeScript frontend utilizing DeckGL to render millions of polygons seamlessly, complete with a time-scrubber for historical animation.

## 🏗️ Architecture
The pipeline is divided into four highly specialized microservices:
1. **Data Extractor (Python/Airflow):** The heavy-compute engine utilizing Dask for distributed raster processing and vectorization.
2. **Spatial API (Python/FastAPI):** The high-speed query backend equipped with connection pooling for the spatial database.
3. **Map Frontend (React/TypeScript):** The interactive operations center for geospatial visualization and metric analysis.
4. **Infrastructure:** Orchestrated via Kubernetes (or Docker Compose locally) utilizing PostGIS for spatial math and MinIO for S3-compatible raw raster storage.

## 🛠️ Technologies Used
* **Data Processing:** Python, Apache Airflow, Dask, Rasterio, GeoPandas, Xarray
* **API Backend:** FastAPI, Asyncpg, SQLAlchemy
* **Frontend UI:** React, TypeScript, Deck.gl, MapLibre-gl
* **Database & Storage:** PostgreSQL with PostGIS, MinIO
* **Deployment:** Docker, Docker Compose, Kubernetes, Helm

## 💻 Installation

### Prerequisites
* Docker and Docker Compose installed.
* Ensure you have adequate local storage for raw SAR data ingestion.

### Setup Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/mtepenner/sar-observation-pipeline.git
   cd sar-observation-pipeline
   ```
2. Spin up the entire infrastructure (PostGIS, MinIO, Airflow, FastAPI, and React) locally using Docker Compose:
   ```bash
   docker-compose up --build -d
   ```
   *(Alternatively, use `make` shortcuts for triggering specific pipeline DAGs and container builds.)*

## 🎮 Usage
Once the cluster is running and the Airflow DAG has ingested initial data:
1. Open your browser and navigate to the Map Frontend (typically `http://localhost:3000`).
2. Use the **TimeSlider** component at the bottom of the screen to animate historical geographical changes.
3. Pan and zoom across the **DeckGL Map**; the frontend will automatically fetch and cache spatial vector tiles for your viewport.
4. Review the **Analysis Sidebar** to see computed metrics (e.g., "Sq Km of Deforestation") corresponding to your current map view.

## 🤝 Contributing
Contributions to the spatial analytics and processing efficiency are highly encouraged. Please ensure that any changes to the SAR math filters or change detection algorithms pass the unit tests defined in `.github/workflows/test-pipeline.yml`.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/NewSpeckleFilter`)
3. Commit your Changes (`git commit -m 'Add support for enhanced Frost filtering'`)
4. Push to the Branch (`git push origin feature/NewSpeckleFilter`)
5. Open a Pull Request

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.
