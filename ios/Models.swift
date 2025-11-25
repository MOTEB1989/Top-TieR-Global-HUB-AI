import Foundation

struct ChatMessage: Identifiable {
    let id = UUID()
    let text: String
    let isUser: Bool
    let timestamp: Date
    let provider: String?
}

struct ChatResponse: Decodable {
    let response: String
}
