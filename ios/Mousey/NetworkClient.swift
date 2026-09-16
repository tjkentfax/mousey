import Foundation

final class NetworkClient {
    var baseURL = ""
    var pin = ""

    private let session: URLSession = .shared

    func send(action: String, button: String? = nil, dx: Double = 0, dy: Double = 0) {
        guard let url = URL(string: baseURL.trimmingCharacters(in: CharacterSet(charactersIn: "/")) + "/mouse") else { return }
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.timeoutInterval = 0.5
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        var payload: [String: Any] = ["pin": pin, "action": action, "dx": dx, "dy": dy]
        if let button { payload["button"] = button }
        request.httpBody = try? JSONSerialization.data(withJSONObject: payload)
        session.dataTask(with: request).resume()
    }
}
