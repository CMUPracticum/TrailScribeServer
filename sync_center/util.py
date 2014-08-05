# Copyright (c) 2014, TrailScribe Team.
# This content is released under the MIT License. See the file named LICENSE for details.
# Stdlib imports
from datetime import datetime
from pytz import timezone

# Core Django imports
from django.utils.timezone import utc

# Imports from app
from sync_center.models import Map, KML


# Based on the information in the request, determine the list of KML or map that 
# TrailScribe client needs to download. Will return a list of IDs to the view.
def get_update_id_list(model_name, req_data):
    db_data = None

    if model_name == 'map':
        db_data = Map.objects.all()
    elif model_name == 'kml':
        db_data = KML.objects.all()

    id_list = []

    # Iterate through each record in the table
    for data in db_data:
        id_str = str(data.id)

        # If the ID is not in the request data, the client needs to download it.
        if id_str not in req_data.keys():
            id_list.append(data.id)
	# If the ID is in the request, compare the last update time. If the time 
	# on server is newer, the client also needs to download it.
        else:
            req_last_modified = datetime.strptime(
	        req_data[id_str]['last_modified'], 
		'%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=utc)

            if data.last_modified > req_last_modified:
                id_list.append(data.id)

    return id_list
