# Copyright 2023 Google LLC

# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
# //
#   http://www.apache.org/licenses/LICENSE-2.0
# //
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from flask import Flask
import time
import os
from random import randint
from time import sleep
import socket

from opentelemetry._metrics import get_meter_provider, set_meter_provider
from opentelemetry.exporter.otlp.proto.grpc._metric_exporter import OTLPMetricExporter
from opentelemetry.sdk._metrics import MeterProvider
from opentelemetry.sdk._metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource

meter = get_meter_provider().get_meter("getting-started")
metric_exporter = OTLPMetricExporter(
    endpoint:="10.64.8.250:4317",
    insecure=True,
    # credentials=ChannelCredentials(credentials),
    # headers=(("metadata", "metadata")),
)
reader = PeriodicExportingMetricReader(metric_exporter)
provider = MeterProvider(metric_readers=[reader],
                        resource=Resource.create({
                                "service.name": "otel-metrics-demo",
                                "service.instance.id": socket.gethostname(),
                            }))
set_meter_provider(provider)

requests_counter = meter.create_counter("otel_total_requests_custom")
errors_counter = meter.create_counter("otel_failed_requests_custom")
request_latency = meter.create_histogram("otel_request_latency_custom")

labels = {}
app = Flask(__name__)

@app.route('/')
def index():
    requests_counter.add(1)
    start = time.time()
    sleep(randint(1,1000)/1000)
    latency = time.time() - start
    if randint(1,100) > 95:
        # fail 5 % of the time
        errors_counter.add(1)
        request_latency.record(latency)
        return 'Processing failed!', 500
    request_latency.record(latency)
    return 'returned in ' + str(round(latency, 3) * 1000) + ' ms', 200
    
app.run(host='0.0.0.0', port=8080)