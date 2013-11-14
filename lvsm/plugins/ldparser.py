"""
Parse a ldirector configuration file. The config specs are defined in ldirectord.cf(5)
"""
import logging
import parseactions
from pyparsing import *

logging.basicConfig(format='[%(levelname)s]: %(message)s')
logger = logging.getLogger('ldparser')

def tokenize_config(configfile):
    """Tokenize the config file. This method will do the bulk of the 
    parsing. Additional verifications can be made in parse_config"""
    # Needed to parse the tabbed ldirector config
    indentStack = [1]

    # Define statics
    EQUAL = Literal("=").suppress()
    COLON = Literal(":").suppress()
    # INDENT = White("    ").suppress()
    # INDENT = Regex("^ {4,}").suppress()

    # Define parsing rules for single lines
    hostname = Word(alphanums + '._+-')
    ip4_address = Combine(Word(nums) - ('.' + Word(nums)) * 3)
    ip4_address.setParseAction(parseactions.validate_ip4)
    ip6_address = Word(alphanums + ':')
    ip6_address.setParseAction(parseactions.validate_ip6)

    port = Word(alphanums)
    port.setParseAction(parseactions.validate_port)

    lbmethod = Word(alphas)
    lbmethod.setParseAction(parseactions.validate_lbmethod)

    ip4_addrport = (ip4_address | hostname) + COLON + port
    ip6_addrport = (ip6_address | hostname) + COLON + port

    yesno = Word(printables)
    yesno.setParseAction(parseactions.validate_yesno)

    integer = Word(printables)
    integer.setParseAction(parseactions.validate_int)
    # integer.setParseAction(lambda t:int(t[0]))

    send_receive = dblQuotedString + Literal(",") + dblQuotedString

    real4 = Group(Literal("real") + EQUAL + ip4_addrport + lbmethod + Optional(Word(nums)) + Optional(send_receive))
    # real4 = Group(Literal("real") + EQUAL + ip4_addrport + lbmethod + Optional(Word(nums)) + Optional(Word(dblQuotedString) + Word(dblQuotedString)))
    real6 = Group(Literal("real6") + EQUAL + ip6_addrport + lbmethod + Optional(Word(nums)) + Optional(send_receive))

    virtual4 = Group(Literal("virtual") + EQUAL + ip4_addrport)
    virtual6 = Group(Literal("virtual6") + EQUAL + ip6_addrport)
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
    # fallback = Group(Literal("fallback") + EQUAL + ip4_addrport + Optional(lbmethod, default=''))
    fallback = Group(Literal("fallback") + EQUAL + ip4_addrport)
    fallback6 = Group(Literal("fallback6") + EQUAL + ip6_addrport)
    fallbackcommand = Group(Literal("fallbackcommand") + EQUAL + (dblQuotedString | Word(printables)))
    fork = Group(Literal("fork") + EQUAL + yesno)
    httpmethod = Group(Literal("httpmethod") + EQUAL + Word(alphanums))
    load = Group(Literal("load") + EQUAL + dblQuotedString)
    logfile = Group(Literal("logfile") + EQUAL + Word(printables))
    login = Group(Literal("login") + EQUAL + dblQuotedString)
    maintenancedir = Group(Literal("maintenancedir") + EQUAL + Word(printables))
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
    virtualhost = Group(Literal("virtualhost") + EQUAL + '"' + hostname + '"' )

    # Validate all the matched elements
    checkport.setParseAction(parseactions.validate_port)
    checktype.setParseAction(parseactions.validate_checktype)
    httpmethod.setParseAction(parseactions.validate_httpmethod)
    protocol.setParseAction(parseactions.validate_protocol)
    scheduler.setParseAction(parseactions.validate_scheduler)
    service.setParseAction(parseactions.validate_service)

    # TODO: implement fwm parsing
    # TODO: validate protocol with respect to the virtual directive

    optionals << ( checkcommand | checkinterval | checktimeout | checktype | checkport | cleanstop
                | database | emailalert | emailalertfreq | emailalertstatus | failurecount | fallback | fallback6
                | fallbackcommand | httpmethod | load | login | monitorfile | negotiatetimeout | netmask
                | passwd | persistent | protocol | quiescent | receive | request | scheduler | secret
                | service | smtp | virtualhost)
    # optionals = ( checkcommand | checkinterval | checktimeout | checktype | checkport | cleanstop
    #             | database | emailalert | emailalertfreq | emailalertstatus | failurecount | fallback
    #             | fallbackcommand | httpmethod | load | login | monitorfile | negotiatetimeout | netmask
    #             | passwd | persistent | protocol | quiescent | receive | request | scheduler | secret
    #             | service | smtp | virtualhost)

    glb_optionals = ( checktimeout | negotiatetimeout | checkinterval | failurecount | fallback | fallback6
                    | fallbackcommand | autoreload | callback | logfile | execute | fork | supervised
                    | quiescent | readdquiescent | emailalert | emailalertfreq | emailalertstatus
                    | emailalertfrom | cleanstop | smtp | maintenancedir )

    ## Define block of config
    # both of the next two styles works
    # virtual4_keywords = indentedBlock(OneOrMore(real4 & ZeroOrMore(optionals)), indentStack, True)
    # virtual4_block = virtual4 + virtual4_keywords
    virtual4_keywords = OneOrMore(real4) & ZeroOrMore(optionals)
    virtual4_block = Group(virtual4 + indentedBlock(virtual4_keywords, indentStack, True))
    virtual4_block.ignore(comment)

    virtual6_keywords = OneOrMore(real6) & ZeroOrMore(optionals)
    virtual6_block = Group(virtual6 + indentedBlock(virtual6_keywords, indentStack, True))
    virtual6_block.ignore(comment)
    
    allconfig = OneOrMore(virtual4_block | virtual6_block) & ZeroOrMore(glb_optionals)
    allconfig.ignore(comment)

    try:
        tokens = allconfig.parseString(configfile)
    except ParseException as pe:
        logger.error("Exception parsing config file")
        logger.error(pe)
    except ParseFatalException as pe:
        logger.error("While parsing config file")
        logger.error(pe)
    else:
        return tokens
    finally:
        pass
