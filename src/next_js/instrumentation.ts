export async function register() {
  // Only run in Node.js runtime — this file also executes in the Edge runtime
  // where Node.js packages are unavailable.
  if (process.env.NEXT_RUNTIME !== "nodejs") return;

  const { NodeSDK } = await import("@opentelemetry/sdk-node");
  const { OTLPTraceExporter } = await import(
    "@opentelemetry/exporter-trace-otlp-http"
  );
  const { resourceFromAttributes } = await import("@opentelemetry/resources");
  const { ATTR_SERVICE_NAME } = await import(
    "@opentelemetry/semantic-conventions"
  );
  const { SimpleSpanProcessor } = await import(
    "@opentelemetry/sdk-trace-node"
  );
  const { getNodeAutoInstrumentations } = await import(
    "@opentelemetry/auto-instrumentations-node"
  );

  const endpoint =
    process.env.OTEL_EXPORTER_OTLP_ENDPOINT ??
    "http://otel-collector.observability.svc.cluster.local:4318";

  const exporter = new OTLPTraceExporter({ url: `${endpoint}/v1/traces` });

  const sdk = new NodeSDK({
    resource: resourceFromAttributes({ [ATTR_SERVICE_NAME]: "nextjs.frontend" }),
    spanProcessors: [new SimpleSpanProcessor(exporter)],
    instrumentations: [
      getNodeAutoInstrumentations({
        // Disable noisy instrumentations that add no value locally
        "@opentelemetry/instrumentation-fs": { enabled: false },
        "@opentelemetry/instrumentation-dns": { enabled: false },
      }),
    ],
  });

  sdk.start();
}
