
## Why Containerize?
Containerizing the V2O Navigator ensures it runs the same way on a laptop, a private data center, or the public cloud. It packages the Python version, the `uv` dependencies, and the code into a single immutable "Image."

## Podman vs. Docker
On the MacBook M3, we use **Podman**. It is:
- **Daemonless:** More secure.
- **Rootless:** Runs without admin privileges.
- **Native to Red Hat:** It uses the same underlying technology as OpenShift (CRI-O).

## Deployment Strategies on OpenShift
1. **Source-to-Image (S2I):** What we used with `oc new-app .`. OpenShift detects the code and builds the container for us.
2. **Binary Build:** Building the image locally with Podman and pushing the "Binary" to OpenShift.

## Key Deployment Commands
- `podman build -t [name] .` : Creates the local image.
- `oc new-app .` : Tells OpenShift to build and run the code.
- `oc expose svc/[name]` : Creates the public URL.