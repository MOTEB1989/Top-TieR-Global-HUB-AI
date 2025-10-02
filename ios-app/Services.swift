import Foundation

final class APIService {
    static let shared = APIService()

    private let baseURL = "http://localhost:5000/api/chat"
    private init() {}

    func sendMessage(_ message: String, provider: String = "openai", completion: @escaping (String) -> Void) {
        guard let url = URL(string: baseURL) else {
            completion("❌ Invalid URL")
            return
        }

        let body: [String: Any] = [
            "message": message,
            "provider": provider
        ]

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")

        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: body, options: [])
        } catch {
            completion("❌ Failed to encode request body")
            return
        }

        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                completion("❌ Network error: \(error.localizedDescription)")
                return
            }

            guard let data = data else {
                completion("❌ Empty response")
                return
            }

            if let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
               let reply = json["reply"] as? String {
                completion(reply)
            } else if let stringResponse = String(data: data, encoding: .utf8) {
                completion(stringResponse)
            } else {
                completion("❌ Failed to parse response")
            }
        }.resume()
    }
}
