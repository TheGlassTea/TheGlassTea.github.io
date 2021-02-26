from flask import Flask, render_template, request, jsonify
import time
import random
import requests
import json
import base64

app = Flask(__name__)

input_url = ''
output_msg = ''

def bypass(url):
    
    if '.com' not in url and '.net' not in url:
        return 'Please enter a valid link.'
    elif 'dynamic' in url:
        return 'This is a dynamic link. This program does not work with dynamic Linkvertise links'
    else:
        try:
            f = open('proxies.txt','r')
            proxies = f.read().splitlines()
            f.close()

            proxy_dict = {}
            proxy_removed = False

            while True:
                try:

                    proxy = random.choice(proxies)

                    http_proxy  = "http://" + proxy
                    https_proxy = "https://" + proxy
                    ftp_proxy   = "ftp://" + proxy

                    proxy_dict = { 
                        "http"  : http_proxy, 
                        "https" : https_proxy, 
                        "ftp"   : ftp_proxy
                    }

                    
                    print('Testing proxy: ' + str(proxy))
                    response = requests.get('https://www.google.com/', proxies = proxy_dict,timeout = 3)
                    break
                except requests.exceptions.ProxyError:
                    print('Proxy error, choosing new proxy')
                    try:
                        proxies.remove(proxy)
                        proxy_removed = True
                        print('Proxy removed from proxy list')
                    except:
                        print('Error removing proxy from proxy list')
                except requests.exceptions.ConnectTimeout:
                    print('Connect error, choosing new proxy')
                    try:
                        proxies.remove(proxy)
                        proxy_removed = True
                        print('Proxy removed from proxy list')
                    except:
                        print('Error removing proxy from proxy list')
            
            #updating proxy list
            if proxy_removed==True:
                new_text = ''
                for z in range(len(proxies)-1):
                    new_text = new_text + proxies[z] + '\n'
                new_text = new_text + proxies[len(proxies)-1]

                f = open('proxies.txt','w')
                f.write(new_text)
                f.close()


            proxy = random.choice(proxies)

            first_link = 'https://publisher.linkvertise.com/api/v1/redirect/link/static/'

            second_link = 'https://publisher.linkvertise.com/api/v1/redirect/link/insert/linkvertise/path/here/target?serial=base64encodedjson'
            second_link_front = second_link[0:second_link.find('insert/linkvertise')]
            second_link_back = second_link[second_link.find('/target?serial'):second_link.find('base64encodedjson')]

            

            input_link = url

            if '.com/' in input_link:
                if '?o=' in input_link:
                    link = input_link[input_link.find('.com/')+5:input_link.find('?o=')]
                else:
                    link = input_link[input_link.find('.com/')+5:len(input_link)]
            if '.net/' in input_link:
                if '?o=' in input_link:
                    link = input_link[input_link.find('.net/')+5:input_link.find('?o=')]
                else:
                    link = input_link[input_link.find('.net/')+5:len(input_link)]
            
            r = requests.get(first_link + link,proxies=proxy_dict,timeout=2)
            text = r.text
            link_id = text[text.find('"id":')+5:text.find(',"url":')]

            new_json = {"timestamp":int(time.time()), "random":"6548307", "link_id":int(link_id)}

            s = json.dumps(new_json)
            json_converted = base64.b64encode(s.encode('utf-8'))
            json_converted = str(json_converted)
            json_converted = json_converted[2:len(json_converted)-1]

                #r = proxy.scrape(second_link_front + link + second_link_back + json_converted)
            r = requests.get(second_link_front + link + second_link_back + json_converted,proxies=proxy_dict,timeout=4)
            converted_json = json.loads(r.text)
            new_link = converted_json['data']['target']
        except:
            new_link = 'Error. Your link is either not a linkvertise link or the linkvertise link is dead.\nYou may try again, as Linkvertise is sometimes buggy.'

        return new_link

@app.route("/", methods=['GET', 'POST'])
def home():
    #print(request.environ.get('HTTP_X_REAL_IP', request.remote_addr))

    start_time = time.time()

    input_url = ''
    output_msg = 'Currently No Link'
    if request.method == 'GET':
        print('GET')
    if request.method == 'POST':
        print('POST')
        form_data = request.form
        if request.form['button'] == 'Bypass':
            form_data = request.form
            input_url = form_data['input_link']
            output_msg = bypass(input_url)
        elif request.form['button'] == 'Clear':
            input_url = ''
            output_msg = "Currently No Link"
    is_url = 0
    if 'https' in output_msg or 'http' in output_msg:
        is_url = 1
    
    f = open('static/data.json','r')
    data = json.load(f)
    f.close()

    new_json = {
        "ip":request.environ.get('HTTP_X_REAL_IP', request.remote_addr),
        "time":time.time(),
        "time_elapsed":time.time()-start_time,
        "input_text":input_url,
        "output_text":output_msg
    }

    data['commands'].append(new_json)

    f = open('static/data.json','w')
    json_object = json.dumps(data, indent = 4)
        
    f.write(json_object)
    f.close()

    if is_url == 0:
        return render_template('index.html', input_url = 'Link Inputted: ' + input_url , output_msg = 'Output: ' + output_msg, is_url = is_url)
    if is_url == 1:
        return render_template('index.html', input_url = 'Link Inputted: ' + input_url , output_msg = output_msg, is_url = is_url)




if __name__ == "__main__":
    app.run(debug=False, host = '0.0.0.0')