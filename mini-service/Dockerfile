# Multi-stage minimal build
FROM golang:1.22-alpine AS build
WORKDIR /src
RUN adduser -D -u 10001 appuser
COPY main.go .
RUN go build -o /out/mini-server main.go

FROM alpine:3.20
WORKDIR /app
# Add non-root user first (always succeeds)
RUN adduser -D -u 10001 appuser
# CA certs (optional for future HTTPS/external APIs)
# Using || true to allow build to succeed even if network/repository issues occur
RUN apk add --no-cache ca-certificates 2>/dev/null || echo "Warning: ca-certificates not installed"
COPY --from=build /out/mini-server /app/mini-server
USER appuser
ENV PORT=8080
EXPOSE 8080
ENTRYPOINT ["/app/mini-server"]
