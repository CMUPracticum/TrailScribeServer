# Copyright (c) 2014, TrailScribe Team.
# This content is released under the MIT License. See the file named LICENSE for details.
# Stdlib imports
import json
from datetime import datetime
from pytz import timezone

# Core Django imports
from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.utils.timezone import utc

# Imports from app
from sync_center.models import Map, KML
from trailscribe import settings
from sync_center import util


def map_list(request):
    maps = Map.objects.all()
    for map in maps:
        map.filename = request.build_absolute_uri(settings.MEDIA_URL + 'map/' + map.filename)

    return HttpResponse(serializers.serialize('json', maps), content_type = "application/json")

def kml_list(request):
    kmls = KML.objects.all()
    for kml in kmls:
        kml.filename = request.build_absolute_uri(settings.MEDIA_URL + 'kml/' + kml.filename)

    return HttpResponse(serializers.serialize('json', kmls), content_type = "application/json")

@csrf_exempt
def sync_data(request):
    if request.method == 'POST':
        request_data = json.loads(request.body)

        # Get the map information on the device
        request_maps = request_data['maps']

	# Pass map information to util.py, which will return the IDs of maps need to be downloaded
        map_id_list = util.get_update_id_list('map', request_maps)

	# Use to list of IDs to get complete information of maps
        maps = Map.objects.filter(id__in = map_id_list)

        # Create the download URL
        for map in maps:
            map.filename = request.build_absolute_uri(settings.MEDIA_URL + 'map/' + map.filename)


        # Get the KML information on the device
        request_kmls = request_data['kmls']

	# Pass map information to util.py, which will return the IDs of KMLs need to be downloaded
        kml_id_list = util.get_update_id_list('kml', request_kmls)

	# Use to list of IDs to get complete information of KMLs
        kmls = KML.objects.filter(id__in = kml_id_list)

        # Create the download URL
        for kml in kmls:
            kml.filename = request.build_absolute_uri(settings.MEDIA_URL + 'kml/' + kml.filename)


        # Put all the model instances need to be updated in a list. Return the result as a JSON file.
        response = []
        for map in maps:
            response.append(map)

        for kml in kmls:
            response.append(kml)

        return HttpResponse(serializers.serialize('json', response), content_type = "application/json")
