# Dockerfile

# Use a specific Alpine version for stability
FROM alpine:3.19

# TARGETARCH is automatically provided by Docker buildx
ARG TARGETARCH

# Install dependencies
# Added grep and sed for version detection.
RUN apk add --no-cache ca-certificates curl iptables ip6tables grep sed

# Download and install LATEST STABLE Tailscale static binaries
RUN echo "Arch: ${TARGETARCH}" && \
    # Map Docker arch to Tailscale arch
    case "${TARGETARCH}" in \
        "amd64") TS_ARCH="amd64" ;; \
        "arm64") TS_ARCH="arm64" ;; \
        "arm/v7") TS_ARCH="arm" ;; \
        *) echo >&2 "error: unsupported architecture: ${TARGETARCH}"; exit 1 ;; \
    esac && \
    # --- Fetch latest stable version ---
    # NOTE: This method relies on parsing the pkgs.tailscale.com HTML/JSON structure.
    # It might break if Tailscale changes their site significantly.
    LATEST_TS_VERSION=$(curl -fsSL "https://pkgs.tailscale.com/stable/?mode=json" | grep -o '"name":"tailscale_[^"]*"' | grep -o '[0-9]*\.[0-9]*\.[0-9]*' | sort -V | tail -n 1) && \
    if [ -z "$LATEST_TS_VERSION" ]; then echo >&2 "error: could not determine latest Tailscale version"; exit 1; fi && \
    echo "Determined Latest Stable Tailscale version: ${LATEST_TS_VERSION}" && \
    TS_VERSION=${LATEST_TS_VERSION} && \
    # --- End fetch latest ---
    echo "Downloading Tailscale version ${TS_VERSION} for arch ${TS_ARCH}" && \
    curl -fsSL "https://pkgs.tailscale.com/stable/tailscale_${TS_VERSION}_${TS_ARCH}.tgz" -o /tmp/tailscale.tgz && \
    tar xzf /tmp/tailscale.tgz -C /tmp --strip-components=1 && \
    mkdir -p /usr/local/bin && \
    mv /tmp/tailscale /usr/local/bin/tailscale && \
    mv /tmp/tailscaled /usr/local/bin/tailscaled && \
    rm -rf /tmp/tailscale.tgz /tmp/tailscale*

# Create necessary directories and files
RUN mkdir -p /var/run/tailscale /var/lib/tailscale /dev/net && \
    touch /dev/net/tun

# Copy the entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Define the volume for state persistence
VOLUME /var/lib/tailscale

# Expose Tailscale's default metrics port (optional)
EXPOSE 9099

# Set the entrypoint
ENTRYPOINT ["/entrypoint.sh"]