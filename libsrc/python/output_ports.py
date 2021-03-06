
import threading
import copy
import time

from ossie.cf    import ExtendedCF
from ossie.cf.CF    import Port
from ossie.utils import uuid
from bulkio.statistics import OutStats
from bulkio import sri
from bulkio import timestamp
from bulkio.bulkioInterfaces import BULKIO, BULKIO__POA 


class OutPort (BULKIO__POA.UsesPortStatisticsProvider ):
    TRANSFER_TYPE='c'
    def __init__(self, name, PortTypeClass, PortTransferType=TRANSFER_TYPE, logger=None ):
        self.name = name
        self.logger = logger
        self.PortType = PortTypeClass
        self.outConnections = {} # key=connectionId,  value=port
        self.refreshSRI = False
        self.stats = OutStats(self.name, PortTransferType )
        self.port_lock = threading.Lock()
        self.sriDict = {} # key=streamID  value=StreamSRI

        if self.logger:
            self.logger.debug('bulkio::OutPort CTOR port:' + str(self.name))
            

    def connectPort(self, connection, connectionId):

        if self.logger:
            self.logger.trace('bulkio::OutPort  connectPort ENTER ')

        self.port_lock.acquire()
        try:
           try:
              port = connection._narrow(self.PortType)
              self.outConnections[str(connectionId)] = port
              self.refreshSRI = True

              if self.logger:
                  self.logger.debug('bulkio::OutPort  CONNECT PORT:' + str(self.name) + ' CONNECTION:' + str(connectionId) )
              
           except:
              if self.logger:
                  self.logger.error('bulkio::OutPort  CONNECT PORT:' + str(self.name) + ' PORT FAILED NARROW')
              raise Port.InvalidPort(1, "Invalid Port for Connection ID:" + str(connectionId) )
        finally:
            self.port_lock.release()

        if self.logger:
            self.logger.trace('bulkio::OutPort  connectPort EXIT ')
            
    def disconnectPort(self, connectionId):
        if self.logger:
            self.logger.trace('bulkio::OutPort  disconnectPort ENTER ')
        self.port_lock.acquire()
        try:
            self.outConnections.pop(str(connectionId), None)
            if self.logger:
                self.logger.debug( "bulkio::OutPort DISCONNECT PORT:" + str(self.name) + " CONNECTION:" + str(connectionId ) )
        finally:
            self.port_lock.release()

        if self.logger:
            self.logger.trace('bulkio::OutPort  disconnectPort EXIT ')

    def enableStats(self, enabled):
        self.stats.setEnabled(enabled)

    def setBitSize(self, bitSize):
        self.stats.setBitSize(bitSize)
        
    def _get_connections(self):
        currentConnections = []
        self.port_lock.acquire()
        for id_, port in self.outConnections.items():
            currentConnections.append(ExtendedCF.UsesConnection(id_, port))
        self.port_lock.release()
        return currentConnections

    def _get_statistics(self):
        self.port_lock.acquire()
        recStat = self.stats.retrieve()
        self.port_lock.release()
        return recStat

    def _get_state(self):
        self.port_lock.acquire()
        numberOutgoingConnections = len(self.outConnections)
        self.port_lock.release()
        if numberOutgoingConnections == 0:
            return BULKIO.IDLE
        else:
            return BULKIO.ACTIVE
        return BULKIO.BUSY

    def _get_activeSRIs(self):
        self.port_lock.acquire()
        sris = []
        for entry in self.sriDict:
            sris.append(copy.deepcopy(self.sriDict[entry]))
        self.port_lock.release()
        return sris

    def pushSRI(self, H):
        if self.logger:
            self.logger.trace('bulkio::OutPort pushSRI ENTER ')
        self.port_lock.acquire()
        self.sriDict[H.streamID] = copy.deepcopy(H)
        try:
            for connId, port in self.outConnections.items():
                try:
                   if port != None:
                      port.pushSRI(H)
                except Exception:
                    if self.logger:
                       self.logger.error("The call to pushSRI failed on port %s connection %s instance %s", self.name, connId, port)
        finally:
            self.refreshSRI = False
            self.port_lock.release()

        if self.logger:
            self.logger.trace('bulkio::OutPort  pushSRI EXIT ')

    def pushPacket(self, data, T, EOS, streamID):

        if self.logger:
            self.logger.trace('bulkio::OutPort  pushPacket ENTER ')

        if self.refreshSRI:
            if self.sriDict.has_key(streamID): 
                self.pushSRI(self.sriDict[streamID])

        self.port_lock.acquire()

        try:    
            for connId, port in self.outConnections.items():
               try:
                    if port != None:
                        port.pushPacket(data, T, EOS, streamID)
                        self.stats.update(len(data), 0, EOS, streamID, connId)
               except Exception:
                   if self.logger:
                       self.logger.error("The call to pushPacket failed on port %s connection %s instance %s", self.name, connId, port)
            if EOS==True:
                if self.sriDict.has_key(streamID):
                    tmp = self.sriDict.pop(streamID)
        finally:
            self.port_lock.release()
 
        if self.logger:
            self.logger.trace('bulkio::OutPort  pushPacket EXIT ')



class OutCharPort(OutPort):
    TRANSFER_TYPE = 'c'
    def __init__(self, name, logger=None ):
        OutPort.__init__(self, name, BULKIO.dataChar, OutCharPort.TRANSFER_TYPE , logger )

class OutOctetPort(OutPort):
    TRANSFER_TYPE = 'B'
    def __init__(self, name, logger=None ):
        OutPort.__init__(self, name, BULKIO.dataOctet, OutOctetPort.TRANSFER_TYPE , logger )

class OutShortPort(OutPort):
    TRANSFER_TYPE = 'h'
    def __init__(self, name, logger=None ):
        OutPort.__init__(self, name, BULKIO.dataShort, OutShortPort.TRANSFER_TYPE , logger )

class OutUShortPort(OutPort):
    TRANSFER_TYPE = 'H'
    def __init__(self, name, logger=None ):
        OutPort.__init__(self, name, BULKIO.dataUshort, OutUShortPort.TRANSFER_TYPE , logger )

class OutLongPort(OutPort):
    TRANSFER_TYPE = 'i'
    def __init__(self, name, logger=None ):
        OutPort.__init__(self, name, BULKIO.dataLong, OutLongPort.TRANSFER_TYPE , logger )

class OutULongPort(OutPort):
    TRANSFER_TYPE = 'I'
    def __init__(self, name, logger=None ):
        OutPort.__init__(self, name, BULKIO.dataUlong, OutULongPort.TRANSFER_TYPE , logger )

class OutLongLongPort(OutPort):
    TRANSFER_TYPE = 'q'
    def __init__(self, name, logger=None ):
        OutPort.__init__(self, name, BULKIO.dataLongLong, OutLongLongPort.TRANSFER_TYPE , logger )

class OutULongLongPort(OutPort):
    TRANSFER_TYPE = 'Q'
    def __init__(self, name, logger=None ):
        OutPort.__init__(self, name, BULKIO.dataUlongLong, OutULongLongPort.TRANSFER_TYPE , logger )

class OutFloatPort(OutPort):
    TRANSFER_TYPE = 'f'
    def __init__(self, name, logger=None ):
        OutPort.__init__(self, name, BULKIO.dataFloat, OutFloatPort.TRANSFER_TYPE , logger )

class OutDoublePort(OutPort):
    TRANSFER_TYPE = 'd'
    def __init__(self, name, logger=None ):
        OutPort.__init__(self, name, BULKIO.dataDouble, OutDoublePort.TRANSFER_TYPE , logger )

class OutFilePort(OutPort):
    TRANSFER_TYPE = 'c'
    def __init__(self, name, logger=None ):
        OutPort.__init__(self, name, BULKIO.dataFile, OutFilePort.TRANSFER_TYPE , logger )

    def pushPacket(self, URL, EOS, streamID):
        self.pushPacket( URL, timestamp.now(), EOS, streamID )

    def pushPacket(self, URL, T, EOS, streamID):

        if self.logger:
            self.logger.trace('bulkio::OutFilePort  pushPacket ENTER ')

        if self.refreshSRI:
            if self.sriDict.has_key(streamID): 
                self.pushSRI(self.sriDict[streamID])

        self.port_lock.acquire()

        try:    
            for connId, port in self.outConnections.items():
               try:
                    if port != None:
                        port.pushPacket(URL, T, EOS, streamID)
                        self.stats.update(1, 0, EOS, streamID, connId)
               except Exception:
                   if self.logger:
                        self.logger.error("The call to OutFilePort::pushPacket failed on port %s connection %s instance %s", self.name, connId, port)
            if EOS==True:
                if self.sriDict.has_key(streamID):
                    tmp = self.sriDict.pop(streamID)
        finally:
            self.port_lock.release()

        if self.logger:
            self.logger.trace('bulkio::OutFilePort  pushPacket EXIT ')
 
class OutXMLPort(OutPort):
    TRANSFER_TYPE = 'c'
    def __init__(self, name, logger=None ):
        OutPort.__init__(self, name, BULKIO.dataXML, OutXMLPort.TRANSFER_TYPE , logger )

    def pushPacket(self, xml_string, T, EOS, streamID):
        self.pushPacket( xml_string, EOS, streamID );

    def pushPacket(self, xml_string, EOS, streamID):

        if self.logger:
            self.logger.trace('bulkio::OutXMLPort  pushPacket ENTER ')

        if self.refreshSRI:
            if self.sriDict.has_key(streamID): 
                self.pushSRI(self.sriDict[streamID])

        self.port_lock.acquire()

        try:    
            for connId, port in self.outConnections.items():
               try:
                    if port != None:
                        port.pushPacket(xml_string, EOS, streamID)
                        self.stats.update(len(xml_string), 0, EOS, streamID, connId)
               except Exception:
                   if self.logger:
                       self.logger.error("The call to OutXMLPort::pushPacket failed on port %s connection %s instance %s", self.name, connId, port)
            if EOS==True:
                if self.sriDict.has_key(streamID):
                    tmp = self.sriDict.pop(streamID)
        finally:
            self.port_lock.release()

        if self.logger:
            self.logger.trace('bulkio::OutXMLPort  pushPacket EXIT ')
 


class OutSDDSPort(OutPort):
    TRANSFER_TYPE = 'c'
    def __init__(self, name, max_attachments=1, logger=None ):
        OutPort.__init__(self, name, BULKIO.dataSDDS, OutSDDSPort.TRANSFER_TYPE , logger )
        self.max_attachments = max_attachments
        self.attachedGroup = {} # key=connection_id,  value=attach_id
        self.lastStreamData = None
        self.lastName = None
        self.defaultStreamSRI = sri.create()
        self.defaultTime = timestamp.now()
        
    def _get_state(self):
        self.port_lock.acquire()
        if len(self._attachedStreams.values()) == 0:
            return BULKIO.IDLE
        # default behavior is to limit to one connection
        elif len(self._attachedStreams.values()) == 1:
            return BULKIO.BUSY
        else:
            return BULKIO.ACTIVE

    def _get_attachedSRIs(self):
        return self._get_activeSRIs()

    def connectPort(self, connection, connectionId):
        OutPort.connectPort( self, connection, connectionId )
        self.port_lock.acquire()
        try:
	   try:
               port = self.outConnections[str(connectionId)]
               if self.lastStreamData:
                   self.attachedGroup[str(connectionId)] = port.attach(self.lastStreamData, self.lastName)
           except:
               raise Port.InvalidPort(1, "Invalid Port for Connection ID:" + str(connectionId) )
        finally:
            self.port_lock.release()
    
    def disconnectPort(self, connectionId):
        try:
            self.port_lock.acquire()
            entry = self.outConnections[str(connectionId)]
            if connectionId in self.attachedGroup:
                try:
                    entry.detach(self.attachedGroup.pop(connectionId))
                except:
                    if self.logger:
                        self.logger.error("Unable to detach %s, should not have happened", str(connectionId))
        finally:
            self.port_lock.release()
        OutPort.disconnectPort( self, connectionId )

    def detach(self, attachId=None, connectionId=None):
        if self.logger:
            self.logger.trace("bulkio::OutSDDSPort, DETACH ENTER ")

        self.port_lock.acquire()
        if attachId == None:
            for entry in self.outConnections:
                try:
                    if entry in self.attachedGroup:
                        if connectionId == None or entry == connectionId:
                            self.outConnections[entry].detach(self.attachedGroup[entry])
                            self.attachedGroup.pop(entry)
                except:
                    if self.logger:
                        self.logger.error("Unable to detach %s", str(entry))
            self.lastStreamData = None
            self.lastName = None
        else:
            for entry in self.attachedGroup:
                try:
                    if self.attachedGroup[entry] == attachId:
                        if entry in self.outConnections:
                            if connectionId == None or entry == connectionId:
                                self.outConnections[entry].detach(self.attachedGroup[entry])
                        self.attachedGroup.pop(entry)
                        if len(self.attachedGroup) == 0:
                            self.lastStreamData = None
                            self.lastName = None
                        break
                except:
                    if self.logger:
                        self.logger.error("Unable to detach %s", str(entry))

        self.port_lock.release()
        if self.logger:
            self.logger.trace("bulkio::OutSDDSPort, DETACH EXIT ")
    
    def attach(self, streamData, name):

        if self.logger:
            self.logger.trace("bulkio::OutSDDSPort, ATTACH ENTER ")

        ids = []
        self.port_lock.acquire()
        for entry in self.outConnections:
            try:
                if entry in self.attachedGroup:
                    self.outConnections[entry].detach(self.attachedGroup[entry])
                self.attachedGroup[entry] = self.outConnections[entry].attach(streamData, name)
                ids.append(self.attachedGroup[entry])
            except:
                if self.logger:
                    self.logger.error("Unable to deliver update to %s", str(entry))
        self.lastStreamData = streamData
        self.lastName = name
        self.port_lock.release()

        if self.logger:
            if len(ids) > 0 :
                self.logger.debug("SDDS PORT, ATTACH COMPLETED ID " + str(ids[0]) + " NAME(user-id):" + str(name))
            self.logger.trace("bulkio::OutSDDSPort, ATTACH EXIT ")

        return ids

    def getStreamDefinition(self, attachId):
        return self.lastStreamData

    def getUser(self, attachId):
        return self.lastName
    
    def pushSRI(self, H, T):
        if self.logger:
            self.logger.trace("bulkio::OutSDDSPort, PUSH-SRI ENTER ")

        self.port_lock.acquire()
        self.sriDict[H.streamID] = (copy.deepcopy(H), copy.deepcopy(T))
        self.defaultStreamSRI = H
        self.defaultTime = T
        try:
            for connId, port in self.outConnections.items():
               try:
                    if port != None:
                        port.pushSRI(H, T)
               except Exception:
                   if self.logger:
                       self.logger.error("The call to pushSRI failed on port %s connection %s instance %s", self.name, connId, port)
        finally:
            self.refreshSRI = False
            self.port_lock.release() 

        if self.logger:
            self.logger.trace("bulkio::OutSDDSPort, PUSH-SRI EXIT ")
