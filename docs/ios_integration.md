# iOS Client Integration Guide

This guide summarizes how the SwiftUI client interacts with the existing backend stack and how to validate the integration locally.

## Backend Services

The deployment provides three services that are reachable from clients:

- **Gateway API** – exposed on port `3000` and handles core REST endpoints.
- **LLM API** – exposed on port `5000` and accessed via `llm_client.py` as an aggregation layer for multiple model providers.
- **Dashboard** – a Next.js web application exposed on port `3001` that serves the administrative user interface.

All services are available through Docker images published to Docker Hub or GHCR.

## iOS Application Flow

A SwiftUI application communicates with the backend over HTTP using the same REST endpoints that other clients consume. Two common interactions are:

1. **Conversational LLM requests**

   ```http
   POST http://<server-host>:5000/chat
   {
     "message": "مرحبا",
     "provider": "openai"
   }
   ```

2. **Knowledge base (RAG) queries**

   ```http
   POST http://<server-host>:3000/v1/kb/ask_llm
   {
     "query": "اشرح لي الكود"
   }
   ```

Replace `<server-host>` with the hostname or IP address where the backend stack is reachable.

## Sample SwiftUI Client

The following minimal SwiftUI view demonstrates how to send a chat message to the LLM API using `URLSession`:

```swift
import SwiftUI

struct ChatResponse: Decodable {
    let response: String
}

struct ContentView: View {
    @State private var userMessage = ""
    @State private var botReply = ""

    var body: some View {
        VStack {
            Text("🚀 LexCode Chat")
                .font(.title)

            TextEditor(text: $userMessage)
                .frame(height: 100)
                .border(Color.gray)

            Button("Send") {
                sendMessage()
            }
            .padding()

            Text("Bot Reply:")
                .font(.headline)
            Text(botReply)
                .padding()
        }
        .padding()
    }

    func sendMessage() {
        guard let url = URL(string: "http://localhost:5000/chat") else { return }

        let body: [String: Any] = [
            "message": userMessage,
            "provider": "openai"
        ]

        let jsonData = try! JSONSerialization.data(withJSONObject: body)

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = jsonData

        URLSession.shared.dataTask(with: request) { data, _, _ in
            if let data = data,
               let decoded = try? JSONDecoder().decode(ChatResponse.self, from: data) {
                DispatchQueue.main.async {
                    self.botReply = decoded.response
                }
            }
        }.resume()
    }
}
```

Update the URL to point to your deployed server when testing outside the local Docker environment.

## Local Testing

1. Start the backend services via Docker Compose.
2. Update the SwiftUI client URLs to reference the correct host (for example, `http://localhost` on the simulator or the machine IP on physical devices).
3. Run the SwiftUI app in the iOS simulator or on a device.
4. Send a chat message and verify that the LLM responds through the backend APIs.

