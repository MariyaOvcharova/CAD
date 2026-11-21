import json, os, signal, sys
import boto3
from http.server import BaseHTTPRequestHandler, HTTPServer

signal.signal(signal.SIGTERM, lambda s, f: sys.exit(0))
TOPIC_ARN = os.environ["TOPIC_ARN"]
sns = boto3.client("sns", region_name=os.environ["REGION"])


class Handler(BaseHTTPRequestHandler):
    def reply(self, code, body):
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/health":
            self.reply(200, {"status": "ok"})
        else:
            self.reply(200, {"service": "orders-api", "usage": "POST /orders {orderId, ...}"})

    def do_POST(self):
        if self.path != "/orders":
            return self.reply(404, {"error": "not found"})
        try:
            length = int(self.headers.get("Content-Length", 0))
            order = json.loads(self.rfile.read(length))
            order_id = order["orderId"]
        except Exception:
            return self.reply(400, {"error": "send JSON with an orderId"})
        sns.publish(
            TopicArn=TOPIC_ARN,
            Message=json.dumps(order),
            MessageAttributes={"eventType": {"DataType": "String", "StringValue": "OrderCreated"}},
        )
        print("published OrderCreated", order_id, flush=True)
        self.reply(202, {"published": order_id})


HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
