import Foundation

/// REST client for the Wardrobe Python backend.
/// Set baseURL to your server (e.g. http://localhost:8000 for simulator).
final class APIClient {
    static let shared = APIClient()

    /// Change this to your backend URL (use your Mac’s IP for a real device).
    var baseURL: String = "http://localhost:8000"

    private init() {}

    // MARK: - Auth (placeholder until backend has auth)

    func login(email: String, password: String) async throws {
        let url = URL(string: "\(baseURL)/auth/login")!
        var req = URLRequest(url: url)
        req.httpMethod = "POST"
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        req.httpBody = try JSONEncoder().encode(["email": email, "password": password])
        let (_, response) = try await URLSession.shared.data(for: req)
        guard (response as? HTTPURLResponse)?.statusCode == 200 else {
            throw APIError.serverError
        }
    }

    // MARK: - Items (wardrobe CRUD)

    func fetchItems() async throws -> [Item] {
        let url = URL(string: "\(baseURL)/items")!
        let (data, response) = try await URLSession.shared.data(from: url)
        guard (response as? HTTPURLResponse)?.statusCode == 200 else {
            throw APIError.serverError
        }
        return try JSONDecoder().decode([Item].self, from: data)
    }

    func uploadItem(imageData: Data, filename: String, category: String) async throws -> Item {
        let url = URL(string: "\(baseURL)/items")!
        var req = URLRequest(url: url)
        req.httpMethod = "POST"
        let boundary = UUID().uuidString
        req.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        req.httpBody = multipartBody(boundary: boundary, imageData: imageData, filename: filename, category: category)
        let (data, resp) = try await URLSession.shared.data(for: req)
        guard (resp as? HTTPURLResponse)?.statusCode == 201 else { throw APIError.serverError }
        return try JSONDecoder().decode(Item.self, from: data)
    }

    private func multipartBody(boundary: String, imageData: Data, filename: String, category: String) -> Data {
        var body = Data()
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"file\"; filename=\"\(filename)\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: image/jpeg\r\n\r\n".data(using: .utf8)!)
        body.append(imageData)
        body.append("\r\n--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"category\"\r\n\r\n\(category)\r\n".data(using: .utf8)!)
        body.append("--\(boundary)--\r\n".data(using: .utf8)!)
        return body
    }

    // MARK: - Recommendations

    func fetchTodayRecommendation() async throws -> Outfit? {
        let url = URL(string: "\(baseURL)/recommendations/today")!
        let (data, response) = try await URLSession.shared.data(from: url)
        guard let http = response as? HTTPURLResponse else { throw APIError.serverError }
        if http.statusCode == 204 { return nil }
        guard http.statusCode == 200 else { throw APIError.serverError }
        return try JSONDecoder().decode(Outfit.self, from: data)
    }

    func completeOutfit(itemId: String) async throws -> Outfit? {
        var comp = URLComponents(string: "\(baseURL)/recommendations/complete")!
        comp.queryItems = [URLQueryItem(name: "item_id", value: itemId)]
        let (data, response) = try await URLSession.shared.data(from: comp.url!)
        guard let http = response as? HTTPURLResponse else { throw APIError.serverError }
        if http.statusCode == 204 { return nil }
        guard http.statusCode == 200 else { throw APIError.serverError }
        return try JSONDecoder().decode(Outfit.self, from: data)
    }
}

enum APIError: Error {
    case serverError
}
