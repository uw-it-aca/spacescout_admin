""" Copyright 2012, 2013 UW Information Technology, University of Washington

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
from spacescout_admin.spot import Image

def post_spot_images(data):
    """ Takes in a dict of {spot_id: [list_of_urls,]} and POSTs each in turn
        to the server. Returns a tuple of (spot_id, spot_image_id, original_url).
    """
    output = []

    for (spot_id, urls) in data.items():
        for url in urls:
            img = Image(spot_id)
            response = img.post(url, 'dummy_description', 'cstimmel')
            output.append((spot_id, response['id'], url))

    return output
