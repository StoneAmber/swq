## -*- coding:utf-8 -*-

import requests
from flask import Flask, render_template, request, flash
from flask_bootstrap import Bootstrap

def get_weather_data(location0, API_URL):
    ''' Get latest weather data from Thinkpage web API
    and handle timeout error.'''
    try:
        API_out0 = requests.get(API_URL, params={
                'key': 'si8wuvsixvksn9dv',
                'location': location0}, timeout=(1, 2))
        return API_out0.json()
        '''
        if API_out0.raise_for_status() is None:  # Raise http error but *not*
            return API_out0.json()               # present error message to user.
        '''
    except requests.exceptions.Timeout:
        return 9

def record_history(query_log1, weather_data1):
    ''' Record query history in a query_log list.'''
    query_log1.append(weather_data1['location'])
    query_log1.append(weather_data1['condition'])
    query_log1.append(weather_data1['temperature'])

app = Flask(__name__)  # Use instance of Flask to build web app.
app.config['SECRET_KEY'] = 'a738868da9dd25d3728c445231f00ab3325a8add18e60d90'
# To handle error in which user's input string is empty or whitespace.
bootstrap = Bootstrap(app)  # Use Bootstrap frame to make a beautiful
weather_data = {}           # and mobile first html.
query_log = []

@app.route('/', methods=['GET', 'POST'])
def homepage():
    '''Mainbody of this web app.Deal with user's input and
       return latest weather condition.'''
    #print(request.form)
    if request.method == 'GET':
        return render_template('homepage.html', welcome=1,  error=0)
    elif request.method == 'POST':
        input_str = request.form['entry']
        if (not input_str) or input_str.isspace():  # Handle the bug when user input nonsense string
            flash('地点名为空 请重新输入！')
            return render_template('homepage.html', welcome=0,  error=0)
        else:
            API_out = get_weather_data(input_str,
                             'https://api.thinkpage.cn/v3/weather/now.json')
            #print(API_out)
            if isinstance(API_out, int) and API_out == 9: # Give error message to user.
                return render_template('homepage.html', welcome=0, error=9,
                                         input_str=input_str)
            else:
                if 'status' not in API_out:
                    up_d_t = API_out['results'][0]['last_update'].replace(
                                          'T',' ')  # Make updata time readable to user.
                    weather_data['updata_time'] = up_d_t.replace('+',
                                                                     ' UTC+')
                    weather_data['location'] = API_out['results'][0]['location']['name']
                    weather_data['condition'] = API_out['results'][0]['now']['text']
                    weather_data['temperature'] = API_out['results'][0]['now']['temperature']
                    #print(weather_data)
                    record_history(query_log, weather_data)
                    return render_template('homepage.html', welcome=0,
                                              error=0,weather_data=weather_data)
                else:
                    if API_out['status_code'] == 'AP010010':
                        return render_template('homepage.html', welcome=0,
                                                   error=3, input_str=input_str,
                                                   error_message=API_out)
                    else:
                        return render_template('homepage.html', welcome=0,
                                                   error=4, input_str=input_str,
                                                   error_message=API_out)
@app.route('/help')
def get_helpdoc():
    ''' Render help doc html page.'''
    return render_template('help.html')

@app.route('/history')
def get_history():
    ''' Render query history html page.'''
    return render_template('history.html', query_log=query_log)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
