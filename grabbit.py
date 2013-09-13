#!/usr/bin/env python

import argparse
import sys
import pika


def pika_callback(ch, method, properties, body):
    print "%r" % (body,)


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
    parser.add_argument("-r", "--routekey", help="routing key")
    parser.add_argument("-q", "--queue", help="queue name")

    args = parser.parse_args()

    creds = None
    if args.username:
        creds = pika.PlainCredentials(args.username, args.password)

    parameters = pika.ConnectionParameters( host         = args.hostname, 
#                                            port         = args.port, 
                                            virtual_host = args.vhost, 
                                            credentials  = creds )

    try:
        connection = pika.BlockingConnection( parameters )
    except pika.exceptions.AMQPError as err:
        sys.stderr.write("Connection Error: %s:%s\n" % (err.__class__, err))
        sys.exit(1)


    sys.stderr.write("connected...\n")
    channel = connection.channel()

    qname = args.queue
    rtkey = "#"
    
    if args.routekey:
        rtkey = args.routekey
    
    if not args.queue:
        qname = '' # Server generated queue name
        channel.queue_declare(queue=qname, auto_delete=True, exclusive=True)

        if args.exchange:
            channel.queue_bind(exchange=args.exchange, queue=qname, 
                               routing_key=rtkey)

    try:
        channel.basic_consume( pika_callback, queue=qname, no_ack=True)
        channel.start_consuming()
    except pika.exceptions.AMQPError as err:
        sys.stderr.write("AMQP Error: %s:%s\n" % (err.__class__, err))

    print "done."
