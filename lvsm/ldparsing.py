from pyparsing import *

# Helper function to validate IPv4 addresses
def validate_ip4(s, loc, tokens):
    octets = tokens[0].split(".")
    print octets
    for octet in octets:
        if int(octet) <= 255 and int(octet) >= 0:
            pass
        else:
            errmsg = "invalid IPv4 address"
            raise ParseFatalException(s, loc, errmsg)
    return tokens

# Helper function that verifies we have a valid port number
def validate_port(s, loc, tokens):
    port = tokens[1]
    if int(port) < 65535 and int(port) > 0:
        return tokens
    else:
        errmsg = "Invalid port number!"
        raise ParseFatalException(s, loc, errmsg)
        
def validate_scheduler(s, loc, tokens):
    schedulers = ['rr', 'wrr', 'lc', 'wlc', 'lblc', 'lblcr', 'dh', 'sh', 'sed', 'nq']
    print tokens
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
    if tokens[0][1].isdigit() and int(tokens[0][1]) > 0:
        return tokens
    else:
        errmsg = "Invalid value for " + tokens[0][0] + "!"
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

def validate_yesno(s, loc, errmsg):
    if tokens[0][1] == "yes" or tokens[0][1] == "no":
        return tokens
    else:
        errmsg = "Value must be 'yes' or 'no'"
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
    # Validate ip4 addresses
    ip4_address.setParseAction(validate_ip4)
    ip4_addrport = (ip4_address | hostname) + COLON + (Word(nums) | Word(alphas))
    # Validate port numbers
    ip4_addrport.setParseAction(validate_port)

    yesno = Literal("yes") | Literal("no")

    real4 = Group(Literal("real") + EQUAL + ip4_addrport + Optional(Word(nums)))
    virtual4 = Group(Literal("virtual") + EQUAL + ip4_addrport)
    comment = Literal("#") + Optional(restOfLine)

    # Optional keywords
    optionals = Forward()
    autoreload = Group(Literal("autoreload") + EQUAL + yesno)
    callback = Group(Literal("callback") + EQUAL + dblQuotedString)
    checkcommand = Group(Literal("checkcommand") + EQUAL + (dblQuotedString | Word(printables)))
    checkinterval = Group(Literal("checkinterval") + EQUAL + Word(alphanums))
    checktimeout = Group(Literal("checktimeout") + EQUAL + Word(alphanums))
    checktype = Group(Literal("checktype") + EQUAL + Word(alphanums))
    checkport = Group(Literal("checkport") + EQUAL + Word(alphanums))
    cleanstop = Group(Literal("cleanstop") + EQUAL + Word(alphas))
    database = Group(Literal("database") + EQUAL + dblQuotedString)
    emailalert = Group(Literal("emailalert") + EQUAL + Word(printables))
    emailalertfreq = Group(Literal("emailalertfreq") + EQUAL + Word(nums))
    emailalertstatus = Group(Literal("emailalertstatus") + EQUAL + Word(printables))
    execute = Group(Literal("execute") + EQUAL + Word(printables))
    failurecount = Group(Literal("failurecount") + EQUAL + Word(alphanums))
    fallback = Group(Literal("fallback") + EQUAL + ip4_addrport)
    fallbackcommand = Group(Literal("fallbackcommand") + EQUAL + (dblQuotedString | Word(printables)))
    fork = Group(Literal("fork") + EQUAL + Word(alphas))
    httpmethod = Group(Literal("httpmethod") + EQUAL + Word(alphanums))
    load = Group(Literal("load") + EQUAL + dblQuotedString)
    logfile = Group(Literal("logfile") + EQUAL + dblQuotedString)
    login = Group(Literal("login") + EQUAL + dblQuotedString)
    monitorfile = Group(Literal("monitorfile") + EQUAL + (dblQuotedString | Word(printables)))
    negotiatetimeout = Group(Literal("negotiatetimeout") + EQUAL + Word(alphanums))
    netmask = Group(Literal("netmask") + EQUAL + ip4_address)
    passwd = Group(Literal("passwd") + EQUAL + dblQuotedString)
    persistent = Group(Literal("persistent") + EQUAL + Word(alphanums))
    protocol = Group(Literal("protocol") + EQUAL + Word(alphas))
    quiescent = Group(Literal("quiescent") + EQUAL + Word(alphas))
    receive = Group(Literal("receive") + EQUAL + dblQuotedString)
    request = Group(Literal("request") + EQUAL + dblQuotedString)
    scheduler = Group(Literal("scheduler") + EQUAL + Word(alphas))
    secret = Group(Literal("secret") + EQUAL + dblQuotedString)
    service = Group(Literal("service") + EQUAL + Word(alphas))
    smtp = Group(Literal("smtp") + EQUAL + (ip4_address | hostname))
    virtualhost = Group(Literal("virtualhost") + EQUAL + hostname )

    # TODO: fork was the last one I did

    # Validate all the matched elements
    # autoreload.setParseAction()
    checkinterval.setParseAction(validate_int)
    checkport.setParseAction(validate_port)
    checktype.setParseAction(validate_checktype)
    checktimeout.setParseAction(validate_int)
    # cleanstop.setParseAction()
    # emailalert.setParseAction()
    # emailalertfreq.setParseAction()
    # emailalertstatus.setParseAction()
    failurecount.setParseAction(validate_int)
    # fork.setParseAction()
    # httpmethod.setParseAction()
    # monitorfile.setParseAction()
    negotiatetimeout.setParseAction(validate_int)
    persistent.setParseAction(validate_int)
    protocol.setParseAction(validate_protocol)
    # quiescent.setParseAction()
    scheduler.setParseAction(validate_scheduler)
    service.setParseAction(validate_service)
    # smtp.setParseAction()

    # TODO: validate protocol=

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

    glb_optionals = ( checktimeout | negotiatetimeout | checkinterval | failurecount | autoreload)

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
        # tokens = virtual4_block.parseString(configfile)
        tokens = allconfig.parseString(configfile)
    except ParseException as pe:
        print pe
    except ParseFatalException as pe:
        print pe
    else:
        return tokens
    finally:
        # print "contents"
        import pprint
        # pprint.pprint(tokens.asList())

conf = "".join(open("./test.cfg").readlines())
config = parse_config(conf)

if config:
    print "== Dict == "
    for item in config.asDict():
        print item
    print "== List =="
    for item in config.asList():
        print item

