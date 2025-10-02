import Foundation

class APIService {
    static let shared = APIService()
    private init() {}

    let baseURL = "http://localhost:5000/chat"

    func sendMessage(_ message: String, provider: String = "openai", completion: @escaping (String) -> Void) {
        guard let url = URL(string: baseURL) else {
            completion("❌ Invalid URL")
            return
        }

        let body: [String: Any] = [
            "message": message,
            "provider": provider
        ]

        guard let jsonData = try? JSONSerialization.data(withJSONObject: body) else {
            completion("❌ Error encoding JSON")
            return
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = jsonData

        URLSession.shared.dataTask(with: request) { data, _, error in
            if let error = error {
                completion("⚠️ Error: \(error.localizedDescription)")
                return
            }

            guard let data = data else {
                completion("⚠️ No data returned")
                return
            }

            if let decoded = try? JSONDecoder().decode(ChatResponse.self, from: data) {
                completion(decoded.response)
            } else {
                completion("⚠️ Failed to decode response")
            }
        }.resume()
    }
}
