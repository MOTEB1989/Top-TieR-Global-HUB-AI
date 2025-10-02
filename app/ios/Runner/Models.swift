import Foundation

struct ChatMessage: Identifiable, Codable {
    let id: UUID
    let text: String
    let isUser: Bool
    let timestamp: Date
    let provider: String?
    
    init(id: UUID = UUID(), text: String, isUser: Bool, timestamp: Date, provider: String? = nil) {
        self.id = id
        self.text = text
        self.isUser = isUser
        self.timestamp = timestamp
        self.provider = provider
    }
}

struct RunnerResponse: Decodable {
    let status: String
    let stdout: String?
    let stderr: String?
}
