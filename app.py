import os
import threading

from bottle import route, run, request, response

import google
import wrike

my_env = os.getenv('my_env')


@route('/')
def landing_page():
    if unicode(request.query.get('code', ''), "utf-8") != '':
        import wrike
        if not wrike.creds.new_auth(unicode(request.query.get('code', ''), "utf-8")):
            return 'Fatal Error'
        else:
            response.set_cookie("wrike_refresh_token", wrike.creds.refresh_token, max_age=3600)  # make expire date a dynamic duration TODO

    timelog_page = "/wrike/timelogs/"
    project_status_page = "/wrike/projectstatus/"
    track_assessment_page = "/wrike/assessment_time/"
    return 'What do you want to do? <br> <br> ' \
           '<a href="' + timelog_page + '">Run timelog report.</a> <br>' + \
           '<a href="' + project_status_page + '">Run project status report.</a> <br>' + \
           '<a href="' + track_assessment_page + '">Run track assessment report.</a> <br>' + \
           ''


@route('/wrike/<path>/')
def wrike_page(path=''):
    # try:

    if request.get_cookie("wrike_refresh_token"):
        print 'cookie found'
        my_cookie = request.get_cookie("wrike_refresh_token")
        wrike.creds.refresh_token = my_cookie
    else:
        print 'no cookie found'

    if not wrike.creds.refresh():
        return 'Please click <a href="https://www.wrike.com/oauth2/authorize?client_id=' + wrike.client_id + \
               '&response_type=code' \
               '&scope=wsReadOnly, wsReadWrite, amReadOnlyWorkflow, amReadWriteWorkflow, amReadOnlyInvitation, amReadWriteInvitation,' \
               ' amReadOnlyGroup, amReadWriteGroup, amReadOnlyUser, amReadWriteUser">here to reauth.</a>'
    else:
        response.set_cookie("wrike_refresh_token", wrike.creds.refresh_token, max_age=3600)  # make expire date a dynamic duration TODO

    if path == 'timelogs':
        timelog_list = wrike.get_timelog_table()
        sheets = google.NewSession()
        workbook_url = 'https://docs.google.com/spreadsheets/d/1tkjX3EL8LhftztrM0FR2gRJH6foC6zCFCHY4fdrKjVY/edit#gid=0'
        sheets.open_workbook(workbook_url)
        sheets.open_worksheet('Sheet2')
        sheets.clear_sheet()
        sheets.upload_table(timelog_list, start_row=2)
        return 'Your sheet was updated at <a href="{}">{}</a>'.format(workbook_url, workbook_url)

    if path == 'projectstatus':
        wrike.get_project_details()

    if path == 'assessment_time':
        t = threading.Thread(name='tracker', target=wrike.track_wrike)
        t.start()
        # print t.isAlive()

    # except Exception as e:
    #     exc_type, exc_value, exc_traceback = sys.exc_info()
    #     traceback_template = '''Traceback (most recent call last):
    #       File "%(filename)s", line %(lineno)s, in %(name)s
    #     %(type)s: %(message)s\n'''
    #
    #     traceback_details = {
    #         'filename': exc_traceback.tb_frame.f_code.co_filename,
    #         'lineno': exc_traceback.tb_lineno,
    #         'name': exc_traceback.tb_frame.f_code.co_name,
    #         'type': exc_type.__name__,
    #         'message': exc_value.message,  # or see traceback._some_str()
    #     }
    #
    #     return ('error\n' + traceback_template % traceback_details).replace('\n', '<br />')
    return '<pre>Command ', path, ' unknown</pre>'


# IEAAYQ33KQC4HFGQ



# if __name__ == "__main__":
if my_env == 'local':
    run(host='localhost', port=int(os.environ.get('PORT', 8080)))
else:
    run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
