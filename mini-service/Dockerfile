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
# CA certs (optional future HTTPS) - best effort
RUN apk add --no-cache ca-certificates || true
COPY --from=build /out/mini-server /app/mini-server
USER appuser
ENV PORT=8080
EXPOSE 8080
ENTRYPOINT ["/app/mini-server"]
