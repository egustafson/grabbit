#!/usr/bin/env python

import argparse
import pika


def pika_callback(ch, method, properties, body):
    print body


#
# Main Program
#
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("hosturl", help="URL / hostname of the RabbitMQ server", default='localhost')
    parser.add_argument("-u", "--username", help="username")
    parser.add_argument("-p", "--password", help="password")
    parser.add_argument("--port", type=int, default=5672)
    parser.add_argument("-v", "--vhost", help="vhost")
    parser.add_argument("-e", "--exchange", help="exchange")
    parser.add_argument("-r", "--routekey", help="routing key")

    args = parser.parse_args()

    creds = None
    if args.username:
        creds = pika.PlainCredentials(args.username, args.password)

    parameters = pika.ConnectionParameters( host         = args.hosturl, 
                                            port         = args.port, 
                                            virtual_host = args.vhost, 
                                            credentials  = creds )

    connection = pika.BlockingConnection( parameters )
    channel = connection.channel()

    channel.queue_declare(queue='grabbit')
    channel.basic_consume( pika_callback, queue='grabbit', no_ack=True)
    channel.start_consuming()

    print "done."
