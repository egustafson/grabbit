#!/usr/bin/env python

import argparse
import pika
import sys

#
# Main Program
#
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("hostname",
                        help="Hostname of the RabbitMQ server",
                        default='localhost')
    parser.add_argument("-u", "--username", help="username")
    parser.add_argument("-p", "--password", help="password")
    parser.add_argument("--port", type=int, default=5672)
    parser.add_argument("-v", "--vhost", default="/", help="vhost")
    parser.add_argument("-e", "--exchange", help="exchange")
    parser.add_argument("-r", "--routekey", type=str, default='', help="routing key")
    parser.add_argument("-D", "--debug", help="debug output", action='store_true')

    args = parser.parse_args()


    creds = None
    if args.username:
        creds = pika.PlainCredentials(args.username, args.password)

    parameters = pika.ConnectionParameters( host         = args.hostname,
#                                            port         = args.port,
                                            virtual_host = args.vhost,
                                            credentials  = creds )

    if args.debug:
        print("Using pika.__version__ {0}".format(pika.__version__))

    try:
        connection = pika.BlockingConnection( parameters )
    except pika.exceptions.AMQPError as err:
        sys.stderr.write("Connection Error: %s:%s\n" % (err.__class__, err))
        sys.exit(1)

    if args.debug:
        sys.stderr.write("connected...\n")

    channel = connection.channel()

    ex = args.exchange
    rt = args.routekey
    prop = pika.BasicProperties(content_type='text/plain', delivery_mode=1)

    #
    # Consume stdin, sending each line as a message
    #
    for line in sys.stdin:
        channel.basic_publish(ex, rt, line, prop)

    connection.close()

    print "done."
