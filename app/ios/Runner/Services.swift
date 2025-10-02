import Foundation

class APIService {
    static let shared = APIService()
    private init() {}

    // عدّل العنوان حسب مكان تشغيل FastAPI
    let runnerURL = "http://localhost:8000/runner/run"

    func runRecipe(completion: @escaping (String) -> Void) {
        guard let url = URL(string: runnerURL) else {
            completion("❌ Invalid URL")
            return
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"

        URLSession.shared.dataTask(with: request) { data, _, error in
            if let error = error {
                completion("⚠️ Error: \(error.localizedDescription)")
                return
            }

            guard let data = data else {
                completion("⚠️ No data returned")
                return
            }

            if let decoded = try? JSONDecoder().decode(RunnerResponse.self, from: data) {
                let logs = """
                ✅ Status: \(decoded.status)
                📄 Output:
                \(decoded.stdout ?? "")
                ⚠️ Errors:
                \(decoded.stderr ?? "")
                """
                completion(logs)
            } else {
                completion("⚠️ Failed to decode response")
            }
        }.resume()
    }
}
