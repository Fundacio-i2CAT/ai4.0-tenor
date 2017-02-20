from models.instance_configuration import InstanceConfiguration
from models.tenor_messages import MonitoringMessage
from models.tenor_messages import CriticalError
from mongoengine import connect
import json
import datetime
from time import mktime, strptime

def get_siids(idate=None, fdate=None):
    today = datetime.datetime.now()
    if not idate:
        idate = '{0}-{1}-{2}'.format(today.year, today.month, today.day)
    if not fdate:
        fdate = '{0}-{1}-{2} 23:59:59'.format(today.year, today.month, today.day)
    initial_date = datetime.datetime.fromtimestamp(mktime(strptime(idate, '%Y-%m-%d')))
    final_date = datetime.datetime.fromtimestamp(mktime(strptime(fdate, '%Y-%m-%d %H:%M:%S')))
    confs = InstanceConfiguration.objects(timestamp__gte=initial_date,
                                          timestamp__lt=final_date).order_by('timestamp')
    return {'date': initial_date, 'confs': confs}

if __name__ == "__main__":
    connect('pi40orch')
    failed = { 'i2cat': [], 'adam': []}
    hanged = { 'i2cat': [], 'adam': []}
    ok = { 'i2cat': [], 'adam': []}
    confs_data = get_siids()
    confs = confs_data['confs']
    for conf in confs:
        dc = 'i2cat'
        siid = conf['service_instance_id']
        if 'content' in conf['consumer_params'][0]:
            dc = 'i2cat'
        if 'fields' in conf['consumer_params'][0]:
            for field in conf['consumer_params'][0]['fields']:
                if field['name'] == 'picture':
                    if field['value'] == 'https://dimoniko.files.wordpress.com/2011/01/hora-de-aventura.jpg':
                        dc = 'adam'

        mss = MonitoringMessage.objects(service_instance_id=siid, message='ACTIVE')
        if len(mss) > 0:
            crite = CriticalError.objects(service_instance_id=siid)
            if len(crite) > 0:
                failed[dc].append({'id': siid, 'message': crite[0]['message']})
                print " ", dc, "\t", conf['timestamp'], 'FAILED'
            else:
                ok[dc].append({'id': siid, 'message': 'ok'})
                print " ", dc, "\t", conf['timestamp'], 'OK'
        else:
            hanged[dc].append({'id': siid, 'message': 'no response'})
            print " ", dc, "\t", conf['timestamp'], 'HANGED'

    totals = {}
    totals['adam'] = len(ok['adam'])+len(failed['adam'])+len(hanged['adam'])
    totals['i2cat'] = len(ok['i2cat'])+len(failed['i2cat'])+len(hanged['i2cat'])
    total = totals['adam']+totals['i2cat']

    print
    print

    print " TOTAL INSTANCES LAUNCHED: {0}".format(total)
    print " -------------------------------"
    print " DATE: {0}".format(confs_data['date'].strftime('%d-%m-%Y'))
    print " -------------------------------"
    print " AT ADAM: {0}/{1}".format(str(totals['adam']),str(total))
    print " \tOK:\t{0}/{1}\t({2}%)".format(len(ok['adam']), totals['adam'], round(100.0*float(len(ok['adam']))/totals['adam']),2)
    print " \tHANGED:\t{0}/{1}\t({2}%)".format(len(hanged['adam']),totals['adam'], round(100.0*float(len(hanged['adam']))/totals['adam']),2)
    print " \tFAILED:\t{0}/{1}\t({2}%)".format(len(failed['adam']),totals['adam'], round(100.0*float(len(failed['adam']))/totals['adam']),2)
    print
    print " AT I2CAT: {0}/{1}".format(str(totals['i2cat']),str(total))
    print " \tOK:\t{0}/{1}\t({2}%)".format(len(ok['i2cat']), totals['i2cat'], round(100.0*float(len(ok['i2cat']))/totals['i2cat']),2)
    print " \tHANGED:\t{0}/{1}\t({2}%)".format(len(hanged['i2cat']),totals['i2cat'], round(100.0*float(len(hanged['i2cat']))/totals['i2cat']),2)
    print " \tFAILED:\t{0}/{1}\t({2}%)".format(len(failed['i2cat']),totals['i2cat'], round(100.0*float(len(failed['i2cat']))/totals['i2cat']),2)

    print
    print

    print " ERRORS"
    print " -------------------------------"
    for conf in confs:
        siid = conf['service_instance_id']
        crite = CriticalError.objects(service_instance_id=siid)
        if len(crite) > 0:
            print " ", crite[0]['message'], crite[0]['code']
