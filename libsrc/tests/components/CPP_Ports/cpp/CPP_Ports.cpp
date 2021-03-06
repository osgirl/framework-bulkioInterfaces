
/**************************************************************************

    This is the component code. This file contains the child class where
    custom functionality can be added to the component. Custom
    functionality to the base class can be extended here. Access to
    the ports can also be done from this class

 	Source: CPP_Ports.spd.xml
 	Generated on: Tue Nov 06 14:25:39 EST 2012
 	Redhawk IDE
 	Version:@buildLabel@
 	Build id: @buildId@

**************************************************************************/

#include "CPP_Ports.h"

PREPARE_LOGGING(CPP_Ports_i)

CPP_Ports_i::CPP_Ports_i(const char *uuid, const char *label) : 
CPP_Ports_base(uuid, label)
{
}

CPP_Ports_i::~CPP_Ports_i()
{
}

void CPP_Ports_i::initialize() throw (CF::LifeCycle::InitializeError, CORBA::SystemException)
{
  CPP_Ports_base::initialize();
  dataCharIn->setNewStreamListener(this, &CPP_Ports_i::newStreamCallback);
}


/***********************************************************************************************

    Basic functionality:

        The service function is called by the serviceThread object (of type ProcessThread).
        This call happens immediately after the previous call if the return value for
        the previous call was NORMAL.
        If the return value for the previous call was NOOP, then the serviceThread waits
        an amount of time defined in the serviceThread's constructor.
        
    SRI:
        To create a StreamSRI object, use the following code:
        	stream_id = "";
	    	sri = BULKIO::StreamSRI();
	    	sri.hversion = 1;
	    	sri.xstart = 0.0;
	    	sri.xdelta = 0.0;
	    	sri.xunits = BULKIO::UNITS_TIME;
	    	sri.subsize = 0;
	    	sri.ystart = 0.0;
	    	sri.ydelta = 0.0;
	    	sri.yunits = BULKIO::UNITS_NONE;
	    	sri.mode = 0;
	    	sri.streamID = this->stream_id.c_str();

	Time:
	    To create a PrecisionUTCTime object, use the following code:
	        struct timeval tmp_time;
	        struct timezone tmp_tz;
	        gettimeofday(&tmp_time, &tmp_tz);
	        double wsec = tmp_time.tv_sec;
	        double fsec = tmp_time.tv_usec / 1e6;;
	        BULKIO::PrecisionUTCTime tstamp = BULKIO::PrecisionUTCTime();
	        tstamp.tcmode = BULKIO::TCM_CPU;
	        tstamp.tcstatus = (short)1;
	        tstamp.toff = 0.0;
	        tstamp.twsec = wsec;
	        tstamp.tfsec = fsec;
        
    Ports:

        Data is passed to the serviceFunction through the getPacket call (BULKIO only).
        The dataTransfer class is a port-specific class, so each port implementing the
        BULKIO interface will have its own type-specific dataTransfer.

        The argument to the getPacket function is a floating point number that specifies
        the time to wait in seconds. A zero value is non-blocking. A negative value
        is blocking.

        Each received dataTransfer is owned by serviceFunction and *MUST* be
        explicitly deallocated.

        To send data using a BULKIO interface, a convenience interface has been added 
        that takes a std::vector as the data input

        NOTE: If you have a BULKIO dataSDDS port, you must manually call 
              "port->updateStats()" to update the port statistics when appropriate.

        Example:
            // this example assumes that the component has two ports:
            //  A provides (input) port of type BULKIO::dataShort called short_in
            //  A uses (output) port of type BULKIO::dataFloat called float_out
            // The mapping between the port and the class is found
            // in the component base class header file

            BULKIO_dataShort_In_i::dataTransfer *tmp = short_in->getPacket(-1);
            if (not tmp) { // No data is available
                return NOOP;
            }

            std::vector<float> outputData;
            outputData.resize(tmp->dataBuffer.size());
            for (unsigned int i=0; i<tmp->dataBuffer.size(); i++) {
                outputData[i] = (float)tmp->dataBuffer[i];
            }

            // NOTE: You must make at least one valid pushSRI call
            if (tmp->sriChanged) {
                float_out->pushSRI(tmp->SRI);
            }
            float_out->pushPacket(outputData, tmp->T, tmp->EOS, tmp->streamID);

            delete tmp; // IMPORTANT: MUST RELEASE THE RECEIVED DATA BLOCK
            return NORMAL;

        Interactions with non-BULKIO ports are left up to the component developer's discretion

    Properties:
        
        Properties are accessed directly as member variables. For example, if the
        property name is "baudRate", it may be accessed within member functions as
        "baudRate". Unnamed properties are given a generated name of the form
        "prop_n", where "n" is the ordinal number of the property in the PRF file.
        Property types are mapped to the nearest C++ type, (e.g. "string" becomes
        "std::string"). All generated properties are declared in the base class
        (CPP_Ports_base).
    
        Simple sequence properties are mapped to "std::vector" of the simple type.
        Struct properties, if used, are mapped to C++ structs defined in the
        generated file "struct_props.h". Field names are taken from the name in
        the properties file; if no name is given, a generated name of the form
        "field_n" is used, where "n" is the ordinal number of the field.
        
        Example:
            // This example makes use of the following Properties:
            //  - A float value called scaleValue
            //  - A boolean called scaleInput
              
            if (scaleInput) {
                dataOut[i] = dataIn[i] * scaleValue;
            } else {
                dataOut[i] = dataIn[i];
            }
            
        A callback method can be associated with a property so that the method is
        called each time the property value changes.  This is done by calling 
        setPropertyChangeListener(<property name>, this, &CPP_Ports::<callback method>)
        in the constructor.
            
        Example:
            // This example makes use of the following Properties:
            //  - A float value called scaleValue
            
        //Add to CPP_Ports.cpp
        CPP_Ports_i::CPP_Ports_i(const char *uuid, const char *label) :
            CPP_Ports_base(uuid, label)
        {
            setPropertyChangeListener("scaleValue", this, &CPP_Ports_i::scaleChanged);
        }

        void CPP_Ports_i::scaleChanged(const std::string& id){
            std::cout << "scaleChanged scaleValue " << scaleValue << std::endl;
        }
            
        //Add to CPP_Ports.h
        void scaleChanged(const std::string&);
        
        
************************************************************************************************/
template < typename IPT, typename  OPT > 
void  DoPort( IPT *iport, OPT *oport, const char *tname ) {

    typename IPT::dataTransfer *p1 = iport->getPacket( bulkio::Const::NON_BLOCKING );

    if ( p1 ) {
      std::cout << "CPP_PORTS::SVC_FUN   TYPE:" << tname << " DATALEN:" << p1->dataBuffer.size()  << std::endl;
      
      if ( oport ) {
	//typename OPT::TransportSequence odata;
	//std::copy( p1->dataBuffer.begin(), p1->dataBuffer.end(), std::back_inserter(odata) );
	//oport->pushPacket( odata, p1->T, p1->EOS, p1->streamID );
	oport->pushPacket( p1->dataBuffer, p1->T, p1->EOS, p1->streamID );
	delete p1;
      }
    }
}


template <> 
void  DoPort< bulkio::InCharPort, bulkio::OutCharPort >( bulkio::InCharPort *iport, bulkio::OutCharPort *oport, const char *tname ) {

    bulkio::InCharPort::dataTransfer *p1 = iport->getPacket( bulkio::Const::NON_BLOCKING );

    if ( p1 ) {
      std::cout << "CPP_PORTS::SVC_FUN   TYPE:" << tname << " DATALEN:" << p1->dataBuffer.size()  << std::endl;
      
      if ( oport ) {
	std::vector< bulkio::OutCharPort::NativeType > d;
	int dlen = p1->dataBuffer.size();
	d.resize( dlen );
	std::copy( &p1->dataBuffer[0], &(p1->dataBuffer[0])+dlen, &(d[0]) );
	oport->pushPacket( d, p1->T, p1->EOS, p1->streamID );
	delete p1;
      }
    }
}


template <> 
void  DoPort< bulkio::InFilePort, bulkio::OutFilePort >( bulkio::InFilePort *iport, bulkio::OutFilePort *oport, const char *tname ) {

    bulkio::InFilePort::dataTransfer *p1 = iport->getPacket( bulkio::Const::NON_BLOCKING );

    if ( p1 ) {
      std::cout << "CPP_PORTS::SVC_FUN   TYPE:" << tname << " DATALEN:" << p1->dataBuffer.size()  << std::endl;
      
      if ( oport ) {
	std::string d;
	int dlen = p1->dataBuffer.size();
	d.resize( dlen );
	std::copy( &p1->dataBuffer[0], &(p1->dataBuffer[0])+dlen, &(d[0]) );
	oport->pushPacket( d.c_str(), p1->T, p1->EOS, p1->streamID );
	delete p1;
      }
    }
}


template <> 
void  DoPort< bulkio::InXMLPort, bulkio::OutXMLPort >( bulkio::InXMLPort *iport, bulkio::OutXMLPort *oport, const char *tname ) {

    bulkio::InXMLPort::dataTransfer *p1 = iport->getPacket( bulkio::Const::NON_BLOCKING );

    if ( p1 ) {
      std::cout << "CPP_PORTS::SVC_FUN   TYPE:" << tname << " DATALEN:" << p1->dataBuffer.size()  << std::endl;
      
      if ( oport ) {
	std::string d;
	int dlen = p1->dataBuffer.size();
	d.resize( dlen );
	std::copy( &p1->dataBuffer[0], &(p1->dataBuffer[0])+dlen, &(d[0]) );
	//oport->pushPacket( d.c_str(), p1->T, p1->EOS, p1->streamID );
	oport->pushPacket( d.c_str(), p1->EOS, p1->streamID );
	delete p1;
      }
    }
}


int CPP_Ports_i::serviceFunction()
{
    LOG_DEBUG(CPP_Ports_i, "serviceFunction() example log message");
    
    DoPort( dataFloatIn, dataFloatOut, "FLOAT");
    DoPort( dataDoubleIn, dataDoubleOut, "DOUBLE");
    DoPort( dataCharIn, dataCharOut, "CHAR");
    DoPort( dataOctetIn, dataOctetOut, "OCTET");
    DoPort( dataShortIn, dataShortOut, "SHORT");
    DoPort( dataUShortIn, dataUShortOut, "USHORT");

    DoPort( dataLongIn, dataLongOut, "LONG");
    DoPort( dataULongIn, dataULongOut, "ULONG");

    DoPort( dataLongLongIn, dataLongLongOut, "LONGLONG");
    DoPort( dataULongLongIn, dataULongLongOut, "ULONGLONG");


    DoPort( dataFileIn, dataFileOut, "URL");
    DoPort( dataXMLIn, dataXMLOut, "XML");

    LOG_DEBUG(CPP_Ports_i, "CPP_Ports:SVC_FUNC END" );
    boost::this_thread::sleep( boost::posix_time::milliseconds(2));

    return NORMAL;

}
