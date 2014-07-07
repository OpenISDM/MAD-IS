'''
    Copyright (c) 2014  OpenISDM

    Project Name:

        OpenISDM MAD-IS

    Version:

        1.0

    File Name:

        communicate.py

    Abstract:

        communicate.py is a module of Interface Server (IS) of
        Mobile Assistance for Disasters (MAD) in the OpenISDM
        Virtual Repository project.

        Establish communication with client side, and server will do some actions
        according different request.

    Authors:

        Bai Shan-Wei, k0969032@gmail.com

    License:

        GPL 3.0 This file is subject to the terms and conditions defined
        in file 'COPYING.txt', which is part of this source code package.

    Major Revision History:

        2014/6/5: complete version 1.0
'''

from flask import Flask,request,jsonify,render_template,after_this_request,make_response
from flask import Blueprint

demand = Blueprint('demand', __name__)
import json
import uuid
import requests
import IS
import time
postInfo = "Null"
need_validate = False

@demand.teardown_request
def teardown_request(exception):
    global postInfo
    postData = postInfo
    if postData !="Null":
        time.sleep(2)
        validate_topic_url(postData)
        postInfo = 'Null'
        pass
    else:
        return 'thx'

@demand.route('/fetch/', methods=['POST', 'GET'])
def receive_req():
    '''
        Receive a request from client side and response according different demands
    '''
    response = IS.answer(request.data)
    return jsonify(response)

@demand.route('/send/', methods=['GET', 'POST'])
def create_info():
    '''
        Receive the information from client side and store it.
    '''
    if request.method == 'POST':
        string = (request.data).split('$')
        IS.bulid_info(string)
        return 'ok'
        #return redirect(url_for('.setup_view',step=request.args.get('request')))

@demand.route('/hub/', methods=['GET', 'HEAD'])
def discovery():
    '''
    If subscribers access '/hub' path by using HTTP GET or HEAD method,
    IS will response HTTP Link Header and response body to subscribers.

    This route can make a Link Header of response to subscribers
    Default Link Header can be "Null"

    '''

    pos_id = request.args.get('posId')
    pos_type = request.args.get('posType')
    dt = IS.determine_topic_and_hub(pos_id, pos_type)
    print 'return response'
    print dt

    #print >> sys.stderr, "/hub GET HEAD..."
    resp = make_response(render_template('ok.html'), 200)
    resp.headers['link'] = '<' + dt['hub_url'] + '>; rel="hub", <' \
        + dt['topic_url'] + '>; rel="self"'
    print resp
    return resp
    #
    # To Do judgement function for response
    #
    # result = determineTopic(request.query_string)
    #

@demand.route('/subscribe/', methods=['POST'])
def hub():
    print 'hello'
    #
    # If subscribers access '/hub' path using HTTP POST method,
    # IS will be a Hub to deal with subscribe/unsubcribe action.
    #
    # This request has a Content-Type of application/x-www-form-urlencoded and
    # the following parameters in its body:
    #
    # hub.callback
    #
    # hub.mode
    #
    # hub.topic
    #
    # hub.lease_seconds(Optional) -
    #     The hub-determined number of seconds that the subscription will stay active before expiring,
    #     measured from the time the verification request was made from the hub to the subscriber.
    #
    # hub.secret(Optional) -
    #     A subscriber-provided secret string that will be used to compute an HMAC digest
    #     for authorized content distribution.
    #

    global postInfo

    #postData = json.loads(request.data)
    postData = request.form
    print postData
    if postData['hub.mode'] and postData['hub.topic'] \
            and postData['hub.callback']:
        if postData['hub.mode'] == 'subscribe':
            #
            # solve postData to Global context
            #
            #g.postData = postData
            #is_find_url = info.match_url(postInfo['hub.topic'])
            postInfo = postData

            resp = make_response(render_template('Accepted.html'), 202)
            return resp
        elif postData['hub.mode'] == 'unsubscribe':
            #
            # To Do a function to clear record in list of subscribers
            #
            resp = make_response(render_template('Accepted.html'), 202)
            return resp
        else:
            resp = make_response(render_template('Unknown.html'), 406)
            return resp
    else:
        resp = make_response(render_template('Unknown.html'), 406)
        return resp

    #
    # To Do publish for other publisher if we need to be a public hub
    #
    # elif postData['hub.mode'] == 'publish':
    #     return 'publish'
    #

def validate_topic_url(postData):

    #
    # Subscriptions MAY be validated by the Hubs who may require more details to accept or refuse a subscription.
    # The Hub MAY also check with the publisher whether the subscription should be accepted.
    # Hubs MUST preserve the query string during subscription verification
    # by appending new parameters to the end of the list using the & (ampersand) character to join.
    #
    # If topic URL is correct from publisher, the hub MUST perform verification of intent of the subscirber
    # if denied, hub must infrom GET request to subscriber's callback URL []
    #

    #print >> sys.stderr, 'validate_topic_url'
    #answer = fromDb(postData['hub.topic'])


    answer_reason = 'No this topic'
    print postInfo['hub.topic']
    is_find_url = IS.match_url(postInfo['hub.topic'])
    # if answer.judge:
    if is_find_url == True:

        #
        # Verifie Intent of the Subscribers
        # This request has the following query string arguments appended:
        #
        # hub.mode
        # hub.topic
        # hub.challage - A hub-generated, random string that MUST be echoed by the subscriber to verify the subscription.
        # hub.lease_seconds(Optional)
        #

        randomKey = uuid.uuid4()

        payload = {'hub.mode': postInfo['hub.mode'],
                   'hub.topic': postInfo['hub.topic'],
                   'hub.challenge': randomKey}

        req = requests.get(postInfo['hub.callback'], params=payload)
        print payload
        print postInfo['hub.callback']
        print str(req.status_code)
        if str(req.status_code)[:1] == '2' and str(req.content) == str(randomKey):
            IS.store_subscriber(postInfo['hub.topic'],postInfo['hub.callback'])
            IS.content_distribution(postInfo['hub.callback'])
            #postInfo = 'null'

            #print >> sys.stderr, 'storeTheSubscribers: %s' % g.postData[
                #'hub.callback']
            print 'success'
        else:
            print 'fail'
            # 'verification to have failed.'
            # storefailedSubscritions(g.postData['hub.callback'])
            #print >> sys.stderr, 'storefailedSlubscritions: %s' % g.postData[
                #'hub.callback']
    else:

        #
        # return 'send reason to subscribers'
        # This request has the following query string arguments appended:
        #
        # hub.mode
        # hub.topic
        # hub.reason(Optional) -The hub may include a reason for which the
        # subscription has been denied.
        #

        payload = {'hub.mode': postInfo['hub.mode'],
                   'hub.topic': postInfo['hub.topic'],
                   'hub.reason': answer_reason}
        req = requests.get(postInfo['hub.callback'], params=payload)

@demand.route('/textView/')
def show_text():
    '''
        Display the topic content with text.
    '''
    return render_template('textview.html')

@demand.route('/imgView/')
def show_img():
    '''
        Display the topic content with image.
    '''
    return render_template('imageView.html')


