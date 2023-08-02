import httpx
import os

async def get_photo():
    '''
    Calls Nasa api and tries to get data
    '''
    url = 'https://api.nasa.gov/planetary/apod'
    parameters = {
        'api_key':os.getenv('nasakey')
    }
    async with httpx.AsyncClient() as client:#init async api call with httpx
        resp = await client.get(url,params=parameters,timeout=30)
        if resp.status_code==200:
            data = resp.json()
            return data['title'],data['url'],data['explanation']
        else:
            return None


