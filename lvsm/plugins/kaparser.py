"""
Parse a keepalived configuration file. The config specs are defined in keepalived.conf(5)
"""
from pyparsing import *
import logging
import parseactions

logging.basicConfig(format='[%(levelname)s]: %(message)s')
logger = logging.getLogger('keepalived')

def tokenize_config(configfile):

	LBRACE, RBRACE = map(Suppress, "{}")

	# generic value types
	email_addr = Regex(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}")
	integer = Word(nums)
	string = Word(printables)

	ip4_address = Regex(r"\d{1,3}(\.\d{1,3}){3}")
	ip6_address = Regex(r"[0-9a-fA-F:]+")
	ip_address = ip4_address | ip6_address

	ip4_class = Regex(r"\d{1,3}(\.\d{1,3}){3}\/\d{1,3}")
	ip6_class = Regex(r"[0-9a-fA-F:]+\/\d{1,3}")
	ip_class = ip4_class | ip6_class

	ip_classaddr = ip_address | ip_class

	# global params
	notification_emails = ( "notification_email" + LBRACE + OneOrMore(email_addr) + RBRACE)
	notification_email_from = ( "notification_email_from" + email_addr)
	smtp_server =  ( "smtp_server" + ip_address)
	smtp_connection_timeout = ("smtp_connection_timeout" + integer)
	router_id = ("router_id" + string)

	# static commands. This is the parameters to "ip addr add" command
	ipaddr_cmd = (ip_classaddr + Optional( "dev" + Word(alphanums) + "scope" + oneOf("global site link host"))) 

	global_params = (notification_emails | notification_email_from | 
					smtp_server | smtp_connection_timeout | router_id)

	global_defs = Group( "global_defs" + LBRACE + OneOrMore(global_params) + RBRACE)
	static_ipaddress = Group("static_ipaddress" + LBRACE + OneOrMore(ipaddr_cmd) + RBRACE)

	comment = "#" + restOfLine

	allconfig = global_defs + Optional(static_ipaddress)
	allconfig.ignore(comment)

	try: 
		tokens = allconfig.parseString(configfile)
	except ParseException as e:
		logger.error("Exception")
		logger.error(e)
	except ParseFatalException as e:
		logger.error("FatalException")
		logger.error(e)
	else:
		return tokens