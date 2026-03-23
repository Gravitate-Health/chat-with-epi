# chat-with-epi

## Deployment

### Deploy via Helm (OCI)

```bash
# Login to registry (if private)
helm registry login ghcr.io

# Deploy directly from the registry
helm install my-release oci://ghcr.io/<your-org>/charts/<chart-name> --version <version>
```

Example for this chart:

```bash
helm install my-release oci://ghcr.io/gravitate-health/charts/chat-with-epi --version 0.1.0
```

### Local Development

```bash
helm lint charts/chat-with-epi
helm template my-release charts/chat-with-epi
```