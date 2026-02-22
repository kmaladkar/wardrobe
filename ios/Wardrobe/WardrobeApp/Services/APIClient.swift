import Foundation

/// REST client for the Wardrobe Python backend.
/// Set baseURL and currentUserId (after login) for profile/wardrobe/try-on.
final class APIClient {
    static let shared = APIClient()

    var baseURL: String = "http://localhost:8000"
    /// Set after login/register; used as X-User-Id for users/wardrobe/recommendations.
    var currentUserId: String?

    private init() {}

    private func url(_ path: String) -> URL { URL(string: "\(baseURL)\(path)")! }

    private func request(_ path: String, method: String = "GET", body: Data? = nil, contentType: String? = "application/json") -> URLRequest {
        var req = URLRequest(url: url(path))
        req.httpMethod = method
        if let ct = contentType { req.setValue(ct, forHTTPHeaderField: "Content-Type") }
        if let uid = currentUserId { req.setValue(uid, forHTTPHeaderField: "X-User-Id") }
        req.httpBody = body
        return req
    }

    // MARK: - Auth

    func register(email: String, displayName: String?) async throws -> User {
        let body = ["email": email, "display_name": displayName as Any]
        let data = try JSONEncoder().encode(body as [String: Any?])
        var req = request("/auth/register", method: "POST", body: data)
        req.httpBody = try JSONSerialization.data(withJSONObject: ["email": email, "display_name": displayName ?? NSNull()])
        let (respData, response) = try await URLSession.shared.data(for: req)
        guard (response as? HTTPURLResponse)?.statusCode == 200 else { throw APIError.serverError }
        return try JSONDecoder().decode(User.self, from: respData)
    }

    func login(email: String) async throws -> User {
        let body = ["email": email]
        let data = try JSONSerialization.data(withJSONObject: body)
        var req = request("/auth/login", method: "POST", body: data)
        let (respData, response) = try await URLSession.shared.data(for: req)
        guard (response as? HTTPURLResponse)?.statusCode == 200 else { throw APIError.serverError }
        return try JSONDecoder().decode(User.self, from: respData)
    }

    // MARK: - User profile & avatar

    func getMe() async throws -> User {
        let (data, response) = try await URLSession.shared.data(for: request("/users/me"))
        guard (response as? HTTPURLResponse)?.statusCode == 200 else { throw APIError.serverError }
        return try JSONDecoder().decode(User.self, from: data)
    }

    func updateProfile(displayName: String?) async throws -> User {
        let body = try JSONEncoder().encode(UpdateProfileRequest(display_name: displayName))
        var req = request("/users/me", method: "PATCH", body: body)
        let (data, response) = try await URLSession.shared.data(for: req)
        guard (response as? HTTPURLResponse)?.statusCode == 200 else { throw APIError.serverError }
        return try JSONDecoder().decode(User.self, from: data)
    }

    func uploadAvatar(imageData: Data) async throws -> User {
        let url = url("/users/me/avatar")
        var req = URLRequest(url: url)
        req.httpMethod = "POST"
        if let uid = currentUserId { req.setValue(uid, forHTTPHeaderField: "X-User-Id") }
        let boundary = UUID().uuidString
        req.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        req.httpBody = multipartBody(boundary: boundary, imageData: imageData, fieldName: "file", filename: "avatar.jpg")
        let (data, response) = try await URLSession.shared.data(for: req)
        guard (response as? HTTPURLResponse)?.statusCode == 200 else { throw APIError.serverError }
        return try JSONDecoder().decode(User.self, from: data)
    }

    // MARK: - Wardrobe (collections: top, bottom, jacket, footwear)

    func fetchWardrobeItems(category: String? = nil) async throws -> [WardrobeItem] {
        var path = "/wardrobe"
        if let c = category, !c.isEmpty { path += "?category=\(c)" }
        let (data, response) = try await URLSession.shared.data(for: request(path))
        guard (response as? HTTPURLResponse)?.statusCode == 200 else { throw APIError.serverError }
        return try JSONDecoder().decode([WardrobeItem].self, from: data)
    }

    func uploadWardrobeItem(imageData: Data, category: String) async throws -> WardrobeItem {
        let url = url("/wardrobe")
        var req = URLRequest(url: url)
        req.httpMethod = "POST"
        if let uid = currentUserId { req.setValue(uid, forHTTPHeaderField: "X-User-Id") }
        let boundary = UUID().uuidString
        req.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        req.httpBody = multipartBody(boundary: boundary, imageData: imageData, fieldName: "file", filename: "item.jpg", extraFields: ["category": category])
        let (data, response) = try await URLSession.shared.data(for: req)
        guard (response as? HTTPURLResponse)?.statusCode == 201 else { throw APIError.serverError }
        return try JSONDecoder().decode(WardrobeItem.self, from: data)
    }

    // MARK: - Legacy items (flat list, no user)

    func fetchItems() async throws -> [Item] {
        let (data, response) = try await URLSession.shared.data(from: url("/items"))
        guard (response as? HTTPURLResponse)?.statusCode == 200 else { throw APIError.serverError }
        return try JSONDecoder().decode([Item].self, from: data)
    }

    func uploadItem(imageData: Data, filename: String, category: String) async throws -> Item {
        var req = URLRequest(url: url("/items"))
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

    private func multipartBody(boundary: String, imageData: Data, fieldName: String, filename: String, extraFields: [String: String] = [:]) -> Data {
        var body = Data()
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"\(fieldName)\"; filename=\"\(filename)\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: image/jpeg\r\n\r\n".data(using: .utf8)!)
        body.append(imageData)
        for (k, v) in extraFields {
            body.append("\r\n--\(boundary)\r\n".data(using: .utf8)!)
            body.append("Content-Disposition: form-data; name=\"\(k)\"\r\n\r\n\(v)\r\n".data(using: .utf8)!)
        }
        body.append("--\(boundary)--\r\n".data(using: .utf8)!)
        return body
    }

    // MARK: - Recommendations & try-on

    func fetchTodayRecommendation() async throws -> Outfit? {
        let (_, response) = try await URLSession.shared.data(for: request("/recommendations/today"))
        guard let http = response as? HTTPURLResponse else { throw APIError.serverError }
        if http.statusCode == 204 { return nil }
        guard http.statusCode == 200 else { throw APIError.serverError }
        return nil
    }

    func tryOn(avatarImageId: String, itemIds: [String]) async throws -> TryOnResult {
        var req = request("/recommendations/try-on", method: "POST", body: try JSONEncoder().encode(TryOnRequest(avatar_image_id: avatarImageId, item_ids: itemIds)))
        let (data, response) = try await URLSession.shared.data(for: req)
        guard (response as? HTTPURLResponse)?.statusCode == 200 else { throw APIError.serverError }
        return try JSONDecoder().decode(TryOnResult.self, from: data)
    }
}

struct UpdateProfileRequest: Encodable {
    let display_name: String?
}

struct TryOnRequest: Encodable {
    let avatar_image_id: String
    let item_ids: [String]
}

struct TryOnResult: Codable {
    let try_on_id: String
    let status: String
    let result_image_id: String?
    let message: String

    enum CodingKeys: String, CodingKey {
        case try_on_id
        case status
        case result_image_id
        case message
    }
}

enum APIError: Error {
    case serverError
}
