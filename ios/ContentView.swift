import SwiftUI

struct ContentView: View {
    @State private var messages: [ChatMessage] = []
    @State private var userInput: String = ""
    @State private var selectedProvider: String = "openai"

    private let providers: [String] = ["openai", "anthropic", "azure"]

    var body: some View {
        VStack {
            Picker("Provider", selection: $selectedProvider) {
                ForEach(providers, id: \.self) { provider in
                    Text(provider.capitalized)
                        .tag(provider)
                }
            }
            .pickerStyle(SegmentedPickerStyle())
            .padding()

            ScrollView {
                LazyVStack(alignment: .leading, spacing: 8) {
                    ForEach(messages) { message in
                        ChatBubble(message: message)
                    }
                }
                .padding(.horizontal)
            }

            HStack {
                TextField("Type your message", text: $userInput)
                    .textFieldStyle(.roundedBorder)

                Button("Send") {
                    sendMessage()
                }
                .disabled(userInput.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
            }
            .padding()
        }
    }

    private func sendMessage() {
        let trimmed = userInput.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }

        let userMsg = ChatMessage(
            text: trimmed,
            isUser: true,
            timestamp: Date(),
            provider: nil
        )

        messages.append(userMsg)
        userInput = ""

        APIService.shared.sendMessage(trimmed, provider: selectedProvider) { reply in
            DispatchQueue.main.async {
                let botMsg = ChatMessage(
                    text: reply,
                    isUser: false,
                    timestamp: Date(),
                    provider: selectedProvider
                )
                messages.append(botMsg)
            }
        }
    }
}

final class APIService {
    static let shared = APIService()

    func sendMessage(_ message: String, provider: String, completion: @escaping (String) -> Void) {
        // Placeholder implementation.
        let reply = "Response from \(provider.capitalized): \(message)"
        DispatchQueue.global().asyncAfter(deadline: .now() + 0.3) {
            completion(reply)
        }
    }
}

#Preview {
    ContentView()
}
