# Import libraries
from fastapi import FastAPI, Request, HTTPException
from mangum import Mangum

# Initialize FastAPI app
app = FastAPI()

@app.get("/")
async def home():
    return {"message": "Hello from Lambda Map Generator!"}

@app.post("/generate-map")
async def generate_map(request: Request):
    # Import libraries
    from map import create_markers, load_map
    import matplotlib.pyplot as plt
    from matplotlib.offsetbox import OffsetImage, AnnotationBbox
    import base64
    import io
    import traceback

    # AWS API Gateway sends `body` as a string, so we need to parse it
    body_json = await request.json()

    # Extract marker data manually
    marker_data = body_json.get("marker_data", [])
    icon_data = body_json.get("icon_data", {})
    image_url = icon_data.get("image_url")

    # Check if the marker data was provided
    if not marker_data:
        # Raise a 400 error to the call application
        raise HTTPException(status_code=400, detail="No marker data provided")

    try:
        # Load the map
        states = load_map()

        # Create the markers
        gdf_markers = create_markers(marker_data, states.crs)

        # Determine if an image URL was passed in
        if not image_url:
            # Load custom Google Maps-style pin image
            pin_icon = plt.imread("image/map-icon.png")

        else:
            # Import the library
            import requests

            # Create a file-like object from the url
            image_data = requests.get(image_url).content
            image_file = io.BytesIO(image_data)

            # Load custom Google Maps-style pin image
            pin_icon = plt.imread(image_file)

        # Define colors
        fill_color = "#D9C06F"
        edge_color = "#ffffff"

        # Create the plot
        fig, ax = plt.subplots(figsize=(29, 19))
        states.plot(edgecolor=edge_color, color=fill_color, linewidth=1, ax=ax)

        # Plot marker images
        for x, y in zip(gdf_markers.geometry.x, gdf_markers.geometry.y):
            im = OffsetImage(pin_icon, zoom=144/ax.figure.dpi)
            im.image.axes = ax
            ab = AnnotationBbox(im, (x, y), frameon=False, pad=0.0)
            ax.add_artist(ab)

        plt.axis("off")

        # Convert plot to base64 image
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format="png", bbox_inches="tight")
        plt.close()
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.read()).decode("utf-8")

        # Return the map image
        return {"image": img_base64}

    except Exception as e:
        # Log full traceback
        error_details = traceback.format_exc()

        # Return full error message in response
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)} - Traceback: {error_details}")

###############################################################################
#   Handler for AWS Lambda                                                    #
###############################################################################
handler = Mangum(app)

###############################################################################
#   Run the self contained application                                        #
###############################################################################
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)