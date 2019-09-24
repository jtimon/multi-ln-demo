
import requests
import json
import time

class RpcCaller(object):

    def __init__(self, address, user, password,
                 **kwargs):

        if not address:
            raise Exception('RpcCaller.__init__: No address provided')
        self.address = address
        if not user:
            raise Exception('RpcCaller.__init__: No user provided')
        self.user = user
        if not password:
            raise Exception('RpcCaller.__init__: No password provided')
        self.password = password
        self.tries = 5

        super(RpcCaller, self).__init__(**kwargs)

    def call(self, method, params):

        requestData = {
            'method': method,
            'params': params,
            'jsonrpc': '2.0',
            'id': self.address + '_' + method,
        }
        rpcAuth = (self.user, self.password)
        rpcHeaders = {'content-type': 'application/json'}
        response = None
        counter = 0
        while response == None:
            json_result = False
            try:
                response = requests.request('post', 'http://' + self.address,
                                            data=json.dumps(requestData), auth=rpcAuth, headers=rpcHeaders)
                # response.raise_for_status()
                json_result = response.json()
            except Exception as e:
                print("Error in RpcCaller.RpcCall:", type(e), e)
                if counter == self.tries:
                    return {'error': {'message': 'Rpc connection error for method %s' % method}}
                time.sleep(2)
                counter = counter + 1
                continue

        if not json_result:
            return {'error': {'message': 'No rpc result for method %s' % method}}

        if not isinstance(json_result, dict):
            return {'error': {'message': 'Result for method %s is not a dict: %s' % (method, json_result)}}

        # If there's errors, only return the errors
        if 'error' in json_result and json_result['error']:
            return {'error': json_result['error']}

        if ('result' in json_result):
            json_result = json_result['result']

        return json_result
