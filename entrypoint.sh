#!/bin/sh
# entrypoint.sh

set -e

# Check if TS_AUTHKEY is provided (will be substituted by Docker Compose)
if [ -z "${TS_AUTHKEY}" ]; then
  echo "ERROR: TS_AUTHKEY environment variable not set."
  exit 1
fi

# Define arguments for tailscaled
# Using userspace-networking avoids needing NET_ADMIN caps in many cases.
# Added outbound proxy and metrics address.
TAILSCALED_ARGS="--state=/var/lib/tailscale/tailscaled.state --socket=/var/run/tailscale/tailscaled.sock --tun=userspace-networking --outbound-http-proxy-listen=localhost:1055 --metrics-addr=0.0.0.0:9099"

# Define base arguments for tailscale up
# Use TS_HOSTNAME or default to 'tailscale-gw'
# Use TS_EXTRA_ARGS for any additional flags like --advertise-tags, etc.
# Use --accept-routes=false unless specifically needed
TS_UP_ARGS="--hostname=${TS_HOSTNAME:-tailscale-gw} --authkey=${TS_AUTHKEY} --accept-dns=false --accept-routes=false ${TS_EXTRA_ARGS}"

echo "Starting tailscaled..."
/usr/local/bin/tailscaled ${TAILSCALED_ARGS} &
TAILSCALED_PID=$!

# Wait for tailscaled socket to be ready
until /usr/local/bin/tailscale --socket=/var/run/tailscale/tailscaled.sock status > /dev/null 2>&1; do
    echo "Waiting for tailscaled socket..."
    sleep 1
done
echo "Tailscaled socket active."

echo "Running tailscale up..."
/usr/local/bin/tailscale --socket=/var/run/tailscale/tailscaled.sock up ${TS_UP_ARGS}

# Apply Serve configuration if provided via TS_SERVE_CONFIG_JSON
if [ -n "$TS_SERVE_CONFIG_JSON" ]; then
  echo "Applying Tailscale Serve configuration..."
  # Use '-' to read config from stdin
  echo "$TS_SERVE_CONFIG_JSON" | /usr/local/bin/tailscale --socket=/var/run/tailscale/tailscaled.sock serve --set-bg -
  echo "Tailscale Serve configuration applied."
else
  echo "No TS_SERVE_CONFIG_JSON provided, skipping Serve configuration."
fi

# Optional: Enable Funnel on port 443 after 'up' if requested
# Note: Requires appropriate ACL tags (e.g., tag:funnel) advertised via TS_EXTRA_ARGS
if [ "${TS_FUNNEL_ENABLE}" = "true" ]; then
    echo "Enabling Tailscale Funnel on port 443..."
    /usr/local/bin/tailscale --socket=/var/run/tailscale/tailscaled.sock funnel 443 on
    echo "Tailscale Funnel enabled."
fi

echo "Tailscale is up and running. Waiting for tailscaled process to exit..."

# Wait for tailscaled process to exit (it shouldn't unless error)
wait ${TAILSCALED_PID}

echo "Tailscaled exited."
exit $?