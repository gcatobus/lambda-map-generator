# Dockerized AWS Lambda Map Generator

## Overview
This project provides an **AWS Lambda function**, packaged as a **Docker container**, that generates a **map with markers** based on latitude and longitude coordinates. It processes input JSON data, plots markers on a U.S. state map, and returns the result as a **base64-encoded image**.

## Features
- **Runs on AWS Lambda** – Serverless execution with minimal infrastructure management
- **Dockerized** – Easily deploy as a containerized function
- **Geospatial Data Processing** – Uses **GeoPandas** to manipulate shapefiles
- **Customizable Map Styling** – Adjusts state positions for better visualization
- **Base64 Image Output** – Returns a map image directly in the API response

## Tech Stack
- **Python** (GeoPandas, Matplotlib, Pandas, FastAPI, Magnum)
- **Docker** (Containerized AWS Lambda function)
- **AWS Lambda** (Serverless execution)

## Project Structure
```
📂 project-root/
 ├── Dockerfile           # Defines the AWS Lambda container
 ├── main.py              # Main script for api routes
 ├── map.py               # Main script for map generation
 ├── requirements.txt     # Python dependencies
 ├── image/               # Custom map marker images
 ├── shape/               # U.S. state boundaries (GeoJSON/Shapefile)
 ├── README.md            # Documentation
```

## Installation & Setup

### 1. Clone the Repository
```sh
git clone https://github.com/gcatobus/lambda-map-generator.git
cd lambda-map-generator
```

### 2. Build & Run the Docker Container Locally
```sh
docker build -t lambda-map-generator .
docker run -p 9000:8080 lambda-map-generator
```

### 3. Test Locally with cURL
Send a sample request to the Lambda function running in the container:
```sh
curl -X POST "http://localhost:9000/generate-map" -H "Content-Type: application/json" -d '{"marker_data": [{"lat": 34.05, "lng": -118.25}], "icon_data": {"image_url": ""}}'
```
The response will contain a **base64-encoded PNG image**.

### 4. Deploy to AWS Lambda
1. **Authenticate with AWS CLI**
   ```sh
   aws configure
   ```
2. **Create an ECR Repository** (if not already created)
   ```sh
   aws ecr create-repository --repository-name lambda-map-generator
   ```
3. **Tag & Push the Image to AWS ECR**
   ```sh
   docker tag lambda-map-generator:latest <aws_account_id>.dkr.ecr.<region>.amazonaws.com/lambda-map-generator:latest
   aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.<region>.amazonaws.com
   docker push <aws_account_id>.dkr.ecr.<region>.amazonaws.com/lambda-map-generator:latest
   ```
4. **Deploy to AWS Lambda**
   ```sh
   aws lambda create-function --function-name lambda-map-generator --package-type Image --code ImageUri=<aws_account_id>.dkr.ecr.<region>.amazonaws.com/lambda-maps:latest --role <IAM_role_ARN>
   ```

## Usage

### API Request Format
```json
{
    "marker_data": [
      {"lat": 34.0522, "lng": -118.2437},
      {"lat": 40.7128, "lng": -74.0060}
    ],
   "icon_data": {
      "image_url": ""
   }
}
```

### Response Format
```json
{
  "image": "<base64_encoded_png>"
}
```
To view the image, decode it from base64.

## Customization
- Modify `fill_color`, `marker_color`, or other **styling options**
- Replace the **state shapefile** for different map projections
- Adjust the **Dockerfile** for specific AWS Lambda settings

## License
This project is licensed under the **GNU General Public License v3.0 (GPLv3)**.

You are free to use, modify, and distribute this software under the terms of the GPLv3 license. However, any modifications or derivative works **must also be released under GPLv3**.

For the full license text, see the [LICENSE](./LICENSE) file or visit:  
[https://www.gnu.org/licenses/gpl-3.0.en.html](https://www.gnu.org/licenses/gpl-3.0.en.html).