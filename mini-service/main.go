package main

import (
	"encoding/json"
	"log"
	"net/http"
	"os"
	"time"
)

type Health struct {
	Status  string `json:"status"`
	Service string `json:"service"`
	Version string `json:"version"`
	Uptime  string `json:"uptime"`
}

var start = time.Now()

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080" // default local fallback
	}

	mux := http.NewServeMux()
	mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodGet {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}
		resp := Health{
			Status:  "ok",
			Service: "mini-safe",
			Version: "1.0.0",
			Uptime:  time.Since(start).String(),
		}
		data, err := json.Marshal(resp)
		if err != nil {
			http.Error(w, "Internal server error", http.StatusInternalServerError)
			log.Printf("failed to marshal response: %v", err)
			return
		}
		w.Header().Set("Content-Type", "application/json; charset=utf-8")
		w.WriteHeader(http.StatusOK)
		if _, err := w.Write(data); err != nil {
			log.Printf("failed to write response: %v", err)
		}
	})

	log.Printf("[mini-service] listening on :%s (non-root)", port)
	if err := http.ListenAndServe(":"+port, mux); err != nil {
		log.Fatalf("server error: %v", err)
	}
}
