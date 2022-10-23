import datetime as dt


def format_db_fields(raw_fields):
    formatted_fields = {}
    for each_field in raw_fields:
        if 'new_' == each_field[:4]:
            formatted_fields[each_field[4:]] = raw_fields[each_field] \
                if 'dt_' + each_field[4:] not in raw_fields \
                else dt.datetime.strptime(raw_fields[each_field], '%Y-%m-%dT%H:%M').strftime("%Y-%m-%d %H:%M:%S")
    return formatted_fields
