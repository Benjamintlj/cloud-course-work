from fastapi import Depends, HTTPException
from fastapi.responses import Response
import requests
import os
from .auth_route_dependency import authenticate_request


def image_mgr(app, lambda_client):
    @app.get('/image')
    async def get_image(location: str, user_id=Depends(authenticate_request)):
        api_key = os.getenv('IMAGE_API_KEY')

        # Get the photo_id
        url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={location}&inputtype=textquery&fields=photos&key={api_key}"
        response = requests.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Could not fetch location data")

        photo_id = response.json().get('candidates', [{}])[0].get('photos', [{}])[0].get('photo_reference')
        if not photo_id:
            raise HTTPException(status_code=404, detail="No photo available for the location")

        # Get the actual photo
        photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photoreference={photo_id}&key={api_key}"
        image = requests.get(photo_url)
        if image.status_code != 200:
            raise HTTPException(status_code=image.status_code, detail="Failed to fetch photo")

        return Response(content=image.content, media_type=image.headers['Content-Type'])
