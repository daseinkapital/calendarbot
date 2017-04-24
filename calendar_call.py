import sys

from oauth2client import client
from googleapiclient import sample_tools
from datetime import datetime, timedelta


def StripEventName(message):
    if message.lower().startswith('where'):
        indexed = message.rfind('the')
        event = message[indexed+4:]
        if '?' in event:
            event = event[:len(event)-1]
        return event, 'where'
    elif message.lower().find('next') != -1:
        return 'next', 'when'
    elif message.lower().startswith('when'):
        indexed = message.rfind('the')
        event = message[indexed+4:]
        if '?' in event:
            event = event[:len(event)-1]
        return event, 'when'
    elif message.lower().startswith('what'):
        if 'today' in message.lower():
            time = datetime.now().isoformat('T')
            begin = time[:11]+'00:00:00-00:00'
            end = time[:11]+'23:59:59-00:00'
            return begin, end
        elif 'tomorrow' in message.lower():
            time = datetime.now() + timedelta(days=1)
            time = time.isoformat('T')
            begin = time[:11]+'00:00:00-00:00'
            end = time[:11]+'23:59:59-00:00'
            return begin, end
        elif 'this week' in message.lower():
            time = datetime.now()
            begin = time - timedelta(days=time.weekday()+1)
            end = begin + timedelta(days=6)
            begin = begin.isoformat('T')
            end = end.isoformat('T')
            begin = begin[:11]+'00:00:00-00:00'
            end = end[:11]+'23:59:59-00:00'
            return begin, end

def Split(eventName):
    return eventName.split()

def ParseMore(Date):
    Date = Date['dateTime']
    year, month, day = int(Date[:4]), int(Date[5:7]), int(Date[8:10])
    time_hr, time_min = int(Date[11:13]), int(Date[14:16])
    dt = datetime(year,month,day,time_hr,time_min)
    StrDate = dt.strftime('%a %b %d').lstrip().replace(" 0", " ")
    StrTime = dt.strftime('%I:%M %p')
    if StrTime[0] == '0':
        StrTime = StrTime[1:]
    return StrDate, StrTime

def ParseEvent(start, end):
    start_date, start_time = ParseMore(start)
    end_date, end_time = ParseMore(end)
    if start_date != end_date:
        return (start_date, end_date, start_time, end_time)
    else:
        return (start_date, start_time, end_time)

def TroubleshootFindEvent(events, eventName, service):
    if len(events['items']) > 1:
        package = []
        for event in events['items']:
            package.append(event['summary'])
        response = "More than one event matched your request. Please use more exact wording. Did you mean:\n"
        for name in package:
            response += " - " + name + "/n"
        return response
    elif len(events['items']) == 0:
        eventSplit = Split(eventName)
        if eventSplit != eventName:
            options = []
            for newName in eventSplit:
                try:
                    page_token = None
                    while True:
                        events = service.events().list(calendarId='virginiatechiie@gmail.com',
                                                     pageToken=page_token,
                                                     timeMin=datetime.now().isoformat('T') + '-00:00',
                                                     orderBy='startTime',
                                                     singleEvents=True,
                                                     q=newName
                                                    ).execute()
                        if len(events['items']) >= 1:
                            for event in events:
                                options.append(event['summary'])
                        page_token = events.get('nextPageToken')
                        if not page_token:
                            break

                    if len(options) >= 1:
                        response = "No events with that name were found so I tried some close matches. "
                        response += "Is one of these the event you were looking for:\n"
                        for name in options:
                            response += " - " + name + "\n"
                        return response
                    elif len(options) == 0:
                        return "I'm sorry, but I could not find any event matching that name."

                except client.AccessTokenRefreshError:
                    print('Something went wrong :( Contact drewbaer@vt.edu (Andrew Samuelson) for more help.')


def CalendarResponse(first, second, message):
    service, flags = sample_tools.init(
        sys.argv, 'calendar', 'v3', __doc__, __file__,
        scope='https://www.googleapis.com/auth/calendar.readonly')

    if (second == 'where'):
        eventName = first
        try:
            page_token = None
            while True:
                events = service.events().list(calendarId='virginiatechiie@gmail.com',
                                             pageToken=page_token,
                                             timeMin=datetime.now().isoformat('T') + '-00:00',
                                             orderBy='startTime',
                                             singleEvents=True,
                                             q=eventName
                                            ).execute()
                if len(events['items']) == 1:
                    event = events['items']
                    event = event[0]
                    if 'location' in event:
                        name, location = event['summary'], event['location']
                        return "The {0} will be held in {1}".format(name, location)
                    else:
                        name = event['summary']
                        return "I'm sorry, we don't currently have a location for {0}.".format(name)
                else:
                    return TroubleshootFindEvent(events, eventName,service)                                
                page_token = events.get('nextPageToken')
                if not page_token:
                    break

        except client.AccessTokenRefreshError:
            print('Something went wrong :( Contact drewbaer@vt.edu (Andrew Samuelson) for more help.')




    elif (second == 'when'):
        if first == 'next':
            try:
                page_token = None
                while True:
                    events = service.events().list(calendarId='virginiatechiie@gmail.com',
                                                 pageToken=page_token,
                                                 maxResults=1,
                                                 timeMin=datetime.now().isoformat('T') + '-00:00',
                                                 orderBy='startTime',
                                                 singleEvents=True,
                                                ).execute()
                    event = events['items']
                    event = event[0]
                    if 'location' in event:
                        name, start, end, location = event['summary'], event['start'], event['end'], event['location']
                        data = ParseEvent(start, end)
                        if len(data) == 3:
                            Date, start_time, end_time = data
                            response = "Our next event is {0} on {1} in {2}, beginning at {3} and ending at {4}.\n".format(name, Date, location, start_time, end_time)
                        elif len(data) == 4:
                            start_date, end_date, start_time, end_time = data
                            response = "Our next event is {0} in {1}, beginning {2} at {3} and ending {4} at {5}.\n".format(name, location, start_date, start_time, end_date, end_time)
                    else:
                        name, start, end = event['summary'], event['start'], event['end']
                        data = ParseEvent(start, end)
                        if len(data) == 3:
                            Date, start_time, end_time = data
                            response = "Our next event is {0} on {1}, beginning at {2} and ending at {3}.".format(name, Date, start_time, end_time)
                        elif len(data) == 4:
                            start_date, end_date, start_time, end_time = data
                            response = "Our next event is {0} beginning {1} at {2} and ending {3} at {4}.".format(name, start_date, start_time, end_date, end_time)
                    return response

                    page_token = events.get('nextPageToken')
                    if not page_token:
                        break

            except client.AccessTokenRefreshError:
                print('Something went wrong :( Contact drewbaer@vt.edu (Andrew Samuelson) for more help.')

        else:
            eventName = first
            try:
                page_token = None
                while True:
                    events = service.events().list(calendarId='virginiatechiie@gmail.com',
                                                 pageToken=page_token,
                                                 timeMin=datetime.now().isoformat('T') + '-00:00',
                                                 orderBy='startTime',
                                                 singleEvents=True,
                                                 q=eventName
                                                ).execute()
                    if len(events['items']) == 1:
                        response = ''
                        event = events['items']
                        event = event[0]
                        name, start, end = event['summary'], event['start'], event['end']
                        data = ParseEvent(start, end)
                        if len(data) == 3:
                            Date, start_time, end_time = data
                            response += "We are having {0} on {1}, beginning at {2} and ending at {3}.".format(name, Date, start_time, end_time)
                        elif len(data) == 4:
                            start_date, end_date, start_time, end_time = data
                            response += "We are having {0} beginning {1} at {2} and ending {3} at {4}.".format(name, start_date, start_time, end_date, end_time)
                        return response
                    else:
                        return TroubleshootFindEvent(events, eventName, service)                                
                    page_token = events.get('nextPageToken')
                    if not page_token:
                        break
            except client.AccessTokenRefreshError:
                print('Something went wrong :( Contact drewbaer@vt.edu (Andrew Samuelson) for more help.')

            
    elif (len(second) == 25):
        begin, end = first, second
        try:
            page_token=None
            while True:
                events = service.events().list(calendarId='virginiatechiie@gmail.com',
                                              pageToken=page_token,
                                              timeMin=begin,
                                              timeMax=end,
                                              orderBy='startTime',
                                              singleEvents=True
                                              ).execute()
                if len(events) >= 1:
                    package = []
                    for event in events['items']:
                        if 'location' in event:
                            package.append((event['summary'], event['start'], event['end'], event['location']))
                        else:
                            package.append((event['summary'], event['start'], event['end']))
                    if 'this week' in message:
                        begin = {'dateTime':begin}
                        end = {'dateTime':end}
                        data = ParseEvent(begin, end)
                        begin, end, scrap1, scrap2 = data
                        response = 'We are having the following events this week ({0} - {1}):\n\n'.format(begin, end)
                        for event in package:
                            if len(event) == 4:
                                name, start, end, location = event
                                data = ParseEvent(start, end)
                                if len(data) == 3:
                                    Date, start_time, end_time = data
                                    response += "{0} on {1} in {2}, beginning at {3} and ending at {4}.\n".format(name, Date, location, start_time, end_time)
                                elif len(data) == 4:
                                    start_date, end_date, start_time, end_time = data
                                    response += "{0} in {1}, beginning {2} at {3} and ending {4} at {5}.\n".format(name, location, start_date, start_time, end_date, end_time)
                            elif len(event) == 3:
                                name, start, end = event
                                data = ParseEvent(start, end)
                                if len(data) == 3:
                                    Date, start_time, end_time = data
                                    response += "{0} on {1}, beginning at {2} and ending at {3}.\n".format(name, Date, start_time, end_time)
                                elif len(data) == 4:
                                    start_date, end_date, start_time, end_time = data
                                    response += "{0}, beginning {1} at {2} and ending {3} at {4}.\n".format(name, start_date, start_time, end_date, end_time)
                        response = response[:len(response) - 2]
                        return response
                    else:
                        if 'today' in message:
                            day = 'Today'
                        elif 'tomorrow' in message:
                            day = 'Tomorrow'
                        response = ''
                        if len(package) == 0:
                            return "No events to show!"
                        else:
                            for event in package:
                                if len(event) == 4:
                                    name, start, end, location = event
                                    data = ParseEvent(start, end)
                                    if len(data) == 3:
                                        Date, start_time, end_time = data
                                        response += "{0}, we have {1} in {2}, beginning at {3} and ending at {4}.\n".format(day, name, location, start_time, end_time)
                                    elif len(data) == 4:
                                        start_date, end_date, start_time, end_time = data
                                        response += "{0}, we have {1} in {2}, beginning {3} and ending at {4}.\n".format(day, name, location, start_time, end_time)
                                elif len(event) == 3:
                                    name, start, end = event
                                    data = ParseEvent(start, end)
                                    if len(data) == 3:
                                        Date, start_time, end_time = data
                                        response += "{0}, we have {1}, beginning at {2} and ending at {3}.\n".format(day, name, start_time, end_time)
                                    elif len(data) == 4:
                                        start_date, end_date, start_time, end_time = data
                                        response += "{0}, we have {1}, beginning at {2} and ending at {3}.\n".format(day, name, start_time, end_time)
                            response = response[:len(response) - 1]
                            return response
                else:
                    respose = "We have no events coming up in that time. Enjoy the break!"

                page_token = events.get('nextPageToken')
                if not page_token:
                    break

        except client.AccessTokenRefreshError:
            print('Something went wrong :( Contact drewbaer@vt.edu (Andrew Samuelson) for more help.')
            

# message_where = "Where is the GE Event?"
# message_when = "When in the GE event?"
# message_what = "What events do we have tomorrow?"
# message_what2 = "What events do we have this week?"
# message_next = "What is our next event?"
# message_next2 = "When is our next event?"
            
#tests
# if __name__ == "__main__":
#      print(message_where)
#      first, second = StripEventName(message_where)
#      response = CalendarResponse(first, second)
#      print(response)
#      print(message_when)
#      first, second = StripEventName(message_when)
#      response = CalendarResponse(first, second)
#      print(response)
#     print(message_what)
#     first, second = StripEventName(message_what)
#     response = CalendarResponse(first, second, message_what)
#     print(response)  
#     print(message_what2)
#     first, second = StripEventName(message_what2)
#     response = CalendarResponse(first, second, message_what2)
#     print(response)
#      print(message_next)
#      first, second = StripEventName(message_next)
#      response = CalendarResponse(first, second)
#      print(response)
#      print(message_next2)
#      first, second = StripEventName(message_next2)
#      response = CalendarResponse(first, second)
#      print(response)