# -*- coding: utf-8 -*-
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from Latch.latch import Latch
import json
import ast
import os
from coinbase.models import LatchAccess

class LatchInterface(object):

    # ------------------------------ PROPERTIES ------------------------------------------

    @property
    def account_id(self):
        try:
            account = LatchAccess.objects.filter(fixed_id=1)[0].account_id
            return account
        except:
            return None
    
    @account_id.setter
    def account_id(self, account_new):
        self._account_id = account_new

    @property
    def webhookChanges(self):
        return self._webhookChanges
    
    @webhookChanges.setter
    def webhookChanges(self, webhook_new):
        self._webhookChanges = webhook_new

    # ------------------------------ INIT ------------------------------------------
    
    

    def __init__(self, account_id = None):
        self.account_id = account_id
        #self.latch_api = Latch(app_id, app_secret)
        self.latch_app_id = os.environ.get('LATCH_APP', '')
        self.latch_app_secret = os.environ.get('LATCH_SECRET', '')
        self.latch_api = Latch(self.latch_app_id, self.latch_app_secret)
        self.webhookChanges = False

# ------------------------------ LATCH METHODS ------------------------------------------

    def checkAccountId(self):
        return self.account_id
    

    def parse_response(self, response):
        data = response.get_data()
        error = response.get_error()
        return data, error
        
    # Pair methods
    def pairLatch(self, pairing_key):
        response = self.latch_api.pair(pairing_key)
        data, error = self.parse_response(response)
        try:
            self.account_id = data['accountId']
            return True
        except:
            print(error)
            return None
        

    def unPairLatch(self):
        response = self.latch_api.unpair(self.account_id)
        data, error = self.parse_response(response)
        return False if error else True


    # Latch Control
    def checkLatch(self):
        response = self.latch_api.status(self.account_id)
        data, error = self.parse_response(response)
        try:
            operations = data['operations']
            isLocked = operations[operations.keys()[0]]["status"]
            return isLocked == 'off'
        except:
            print(error)
            return False

    def getLatchOperation(self):
        response = self.latch_api.status(self.account_id)
        data, error = self.parse_response(response)
        try:
            operations = data.get('operations', '')
            op_id = next(iter(operations))
            return op_id
        except:
            return None

    def lockLatch(self, operationId=None):
        response = self.latch_api.lock(self.account_id, operationId)
        data, error = self.parse_response(response)
        return False if error else True

    def unlockLatch(self, operationId=None):
        response = self.latch_api.unlock(self.account_id, operationId)
        data, error = self.parse_response(response)
        return False if error else True

    def unlockAll(self, dic_latches):
        for key, value in dic_latches.iteritems():
            self.unlockLatch(value)

    # Instances
    def getInstances(self, operation_id=None):
        response = self.latch_api.getInstances(self.account_id, operation_id)
        data, error = self.parse_response(response)
        return data

    def getInstanceStatus(self, instance_id, operation_id=None, silent=False, nootp=False):
        response = self.latch_api.instanceStatus(instance_id, self.account_id, operation_id)
        error, data = self.parse_response(response)
        if error:
            return False
        else:
            status = data.get('operations', {}).get(instance_id, {}).get('status', '')
            return status == 'off'

    def createInstance(self, name, operation_id=None):
        response = self.latch_api.createInstance(name, self.account_id, operation_id)
        data, error = self.parse_response(response)
        if error:
            return None
        else:
            instanceNew = data.get('instances', None)
            return instanceNew

    def deleteInstance(self, instance_id, operation_id=None):
        response = self.latch_api.deleteInstance(instance_id, self.account_id)
        data, error = self.parse_response(response)
        return error

    # Operations
    def getOperations(self, operation_id=None):
        response = self.latch_api.getOperations()
        data, error = self.parse_response(response)
        return data.get('operations', None)

    def getOperationStatus(self, operation_id, silent=False, nootp=False):
        response = self.latch_api.operationStatus(self.account_id, operation_id)
        data, error = self.parse_response(response)
        if error:
            return False
        else:
            status = data.get('operations', {}).get(operation_id, {}).get('status', '')
            return status == 'off'

    def createOperation(self, name, two_factor='DISABLED', lock_on='DISABLED'):
        op_id = self.getLatchOperation()
        response = self.latch_api.createOperation(op_id, name, two_factor, lock_on)
        data, error = self.parse_response(response)
        if error:
            return None
        else:
            operationNew = data.get('instances', None)
            return operationNew

    def deleteOperation(self, operation_id):
        response = self.latch_api.deleteOperation(operation_id)
        data, error = self.parse_response(response)
        return error

    
    # def update_account_id(self, new_account_id=None):
    #     LatchAccess.objects.filter(fixed_id=1).delete()
    #     self.account_id = new_account_id
    #     if new_account_id:
    #         account_id_model = LatchAccess(account_id=new_account_id, fixed_id=1)
    #         account_id_model.save()
