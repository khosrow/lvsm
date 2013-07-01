import logging
from pyparsing import *


# Helper function to validate IPv4 addresses
def validate_ip4(s, loc, tokens):
    octets = tokens[0].split(".")

    logger = logging.getLogger('ldparser')
    logger.debug('IP4 octets: %s', octets)

    for octet in octets:
        if int(octet) <= 255 and int(octet) >= 0:
            pass
        else:
            errmsg = "invalid IPv4 address"
            raise ParseFatalException(s, loc, errmsg)
    return tokens

# Helper function that verifies we have a valid port number
def validate_port(s, loc, tokens):
    # port = tokens[1]
    port = tokens[0]
    if int(port) < 65535 and int(port) > 0:
        return tokens
    else:
        errmsg = "Invalid port number!"
        raise ParseFatalException(s, loc, errmsg)
        
def validate_scheduler(s, loc, tokens):
    schedulers = ['rr', 'wrr', 'lc', 'wlc', 'lblc', 'lblcr', 'dh', 'sh', 'sed', 'nq']

    logger = logging.getLogger('ldparser')
    logger.debug('Tokens: %s', tokens)

    if tokens[0][1] in schedulers:
        return tokens
    else:
        errmsg = "Invalid scheduler type!"
        raise ParseFatalException(s, loc, errmsg)

def validate_checktype(s, loc, tokens):
    checktypes = ["connect", "negotiate", "ping", "off", "on", "external", "external-perl"]
    if ((tokens[0][1] in checktypes) or (tokens[0][1].isdigit() and int(tokens[0][1]) > 0)):
        return tokens
    else:
        errmsg = "Invalid checktype!"
        raise ParseFatalException(s, loc, errmsg)

def validate_int(s, loc, tokens):
    # if tokens[0][1].isdigit() and int(tokens[0][1]) > 0:
    if tokens[0].isdigit() and int(tokens[0]) > 0:
        return tokens
    else:
        errmsg = "Value must be an integer!"
        raise ParseFatalException(s, loc, errmsg)

def validate_protocol(s, loc, tokens):
    protocols = ['fwm', 'udp', 'tcp']
    if tokens[0][1] in protocols:
        return tokens
    else:
        errmsg = "Invalid protocol!"
        raise ParseFatalException(s, loc, errmsg)

def validate_service(s, loc, tokens):
    services = ["dns", "ftp", "http", "https", "http_proxy", "imap", "imaps"
                ,"ldap", "nntp", "mysql", "none", "oracle", "pop" , "pops"
                , "radius", "pgsql" , "sip" , "smtp", "submission", "simpletcp"]
    if tokens[0][1] in services:
        return tokens
    else:
        errmsg = "Invalid service type!"
        raise ParseFatalException(s, loc, errmsg)

def validate_yesno(s, loc, tokens):
    if tokens[0] == "yes" or tokens[0] == "no":
        return tokens
    else:
        errmsg = "Value must be 'yes' or 'no'"
        raise ParseFatalException(s, loc, errmsg)

def validate_httpmethod(s, loc, tokens):
    if tokens[0] in ['GET', 'HEAD']:
        return tokens
    else:
        errmsg = "Value must be 'GET' or 'HEAD'"
        raise ParseFatalException(s, loc, errmsg)

def parse_config(configfile):
    indentStack = [1]

    # Define statics
    EQUAL = Literal("=").suppress()
    COLON = Literal(":").suppress()
    # INDENT = White("    ").suppress()
    INDENT = Regex("^ {4,}").suppress()

    ## Define parsing rules for single lines
    hostname = Word(alphanums + '._+-')
    ip4_address = Combine(Word(nums) - ('.' + Word(nums)) * 3)
    ip4_address.setParseAction(validate_ip4)

    port = Word(alphanums)
    port.setParseAction(validate_port)

    ip4_addrport = (ip4_address | hostname) + COLON + port
    # Validate port numbers
    # ip4_addrport.setParseAction(validate_port)

    yesno = Literal("yes") | Literal("no")
    yesno.setParseAction(validate_yesno)

    integer = Word(printables)
    integer.setParseAction(validate_int)

    real4 = Group(Literal("real") + EQUAL + ip4_addrport + Optional(Word(nums)))
    virtual4 = Group(Literal("virtual") + EQUAL + ip4_addrport)
    comment = Literal("#") + Optional(restOfLine)

    # Optional keywords
    optionals = Forward()
    autoreload = Group(Literal("autoreload") + EQUAL + yesno)
    callback = Group(Literal("callback") + EQUAL + dblQuotedString)
    checkcommand = Group(Literal("checkcommand") + EQUAL + (dblQuotedString | Word(printables)))
    # checkinterval = Group(Literal("checkinterval") + EQUAL + Word(alphanums))
    checkinterval = Group(Literal("checkinterval") + EQUAL + integer)
    checktimeout = Group(Literal("checktimeout") + EQUAL + integer)
    checktype = Group(Literal("checktype") + EQUAL + Word(alphanums))
    checkport = Group(Literal("checkport") + EQUAL + Word(alphanums))
    cleanstop = Group(Literal("cleanstop") + EQUAL + yesno)
    database = Group(Literal("database") + EQUAL + dblQuotedString)
    emailalert = Group(Literal("emailalert") + EQUAL + Word(printables))
    emailalertfreq = Group(Literal("emailalertfreq") + EQUAL + integer)
    emailalertfrom = Group(Literal("emailalertfrom") + EQUAL + Word(printables))
    emailalertstatus = Group(Literal("emailalertstatus") + EQUAL + Word(printables))
    execute = Group(Literal("execute") + EQUAL + Word(printables))
    failurecount = Group(Literal("failurecount") + EQUAL + integer)
    fallback = Group(Literal("fallback") + EQUAL + ip4_addrport)
    fallbackcommand = Group(Literal("fallbackcommand") + EQUAL + (dblQuotedString | Word(printables)))
    fork = Group(Literal("fork") + EQUAL + yesno)
    httpmethod = Group(Literal("httpmethod") + EQUAL + Word(alphanums))
    load = Group(Literal("load") + EQUAL + dblQuotedString)
    logfile = Group(Literal("logfile") + EQUAL + dblQuotedString)
    login = Group(Literal("login") + EQUAL + dblQuotedString)
    maintenance_dir = Group(Literal("maintenance_dir") + EQUAL + Word(printables))
    monitorfile = Group(Literal("monitorfile") + EQUAL + (dblQuotedString | Word(printables)))
    negotiatetimeout = Group(Literal("negotiatetimeout") + EQUAL + integer)
    netmask = Group(Literal("netmask") + EQUAL + ip4_address)
    passwd = Group(Literal("passwd") + EQUAL + dblQuotedString)
    persistent = Group(Literal("persistent") + EQUAL + integer)
    protocol = Group(Literal("protocol") + EQUAL + Word(alphas))
    quiescent = Group(Literal("quiescent") + EQUAL + yesno)
    readdquiescent = Group(Literal("readdquiescent") + EQUAL + yesno)
    receive = Group(Literal("receive") + EQUAL + dblQuotedString)
    request = Group(Literal("request") + EQUAL + dblQuotedString)
    scheduler = Group(Literal("scheduler") + EQUAL + Word(alphas))
    secret = Group(Literal("secret") + EQUAL + dblQuotedString)
    service = Group(Literal("service") + EQUAL + Word(alphas))
    supervised = Group(Literal("supervised") + EQUAL + yesno)
    smtp = Group(Literal("smtp") + EQUAL + (ip4_address | hostname))
    virtualhost = Group(Literal("virtualhost") + EQUAL + hostname )

    # Validate all the matched elements
    checkport.setParseAction(validate_port)
    checktype.setParseAction(validate_checktype)
    httpmethod.setParseAction(validate_httpmethod)
    protocol.setParseAction(validate_protocol)
    scheduler.setParseAction(validate_scheduler)
    service.setParseAction(validate_service)

    # TODO: validate protocol with respect to the virtual directive
    # TODO: implement virtual6, real6, fallback6

    optionals << ( checkcommand | checkinterval | checktimeout | checktype | checkport | cleanstop
                | database | emailalert | emailalertfreq | emailalertstatus | failurecount | fallback
                | fallbackcommand | httpmethod | load | login | monitorfile | negotiatetimeout | netmask
                | passwd | persistent | protocol | quiescent | receive | request | scheduler | secret
                | service | smtp | virtualhost)
    # optionals = ( checkcommand | checkinterval | checktimeout | checktype | checkport | cleanstop
    #             | database | emailalert | emailalertfreq | emailalertstatus | failurecount | fallback
    #             | fallbackcommand | httpmethod | load | login | monitorfile | negotiatetimeout | netmask
    #             | passwd | persistent | protocol | quiescent | receive | request | scheduler | secret
    #             | service | smtp | virtualhost)

    glb_optionals = ( checktimeout | negotiatetimeout | checkinterval | failurecount | fallback
                    | fallbackcommand | autoreload | callback | logfile | execute | fork | supervised
                    | quiescent | readdquiescent | emailalert | emailalertfreq | emailalertstatus
                    | emailalertfrom | cleanstop | smtp | maintenance_dir )

    ## Define block of config
    # both of the next two styles works
    # virtual4_keywords = indentedBlock(OneOrMore(real4 & ZeroOrMore(optionals)), indentStack, True)
    # virtual4_block = virtual4 + virtual4_keywords
    virtual4_keywords = OneOrMore(real4) & ZeroOrMore(optionals)
    virtual4_block = virtual4 + indentedBlock(virtual4_keywords, indentStack, True)

    virtual4_block.ignore(comment)

    allconfig = OneOrMore(virtual4_block) & ZeroOrMore(glb_optionals)
    allconfig.ignore(comment)

    try:
        tokens = allconfig.parseString(configfile)
    except ParseException as pe:
        print "[ERROR] While parsing config file"
        print pe
    except ParseFatalException as pe:
        print "[ERROR] While parsing config file"
        print pe
    else:
        return tokens
    finally:
        pass

FORMAT = "%(asctime)s %(name)s[%(levelname)s][%(funcName)s]: %(message)s"
logging.basicConfig(format=FORMAT, level=logging.DEBUG, datefmt='%b %d %H:%m:%S')
logger = logging.getLogger('ldparser')
conf = "".join(open("./test.cfg").readlines())
config = parse_config(conf)

if config:
    for item in config.asList():
        logger.debug('Token: %s' ,item)