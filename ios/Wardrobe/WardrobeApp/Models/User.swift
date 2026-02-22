import Foundation

/// User profile – matches backend users schema (avatar_image_id, etc.).
struct User: Identifiable, Codable {
    let id: String
    let email: String
    var displayName: String?
    var avatarImageId: String?
    var avatarUrl: String?
    let createdAt: String?
    let updatedAt: String?

    enum CodingKeys: String, CodingKey {
        case id
        case email
        case displayName = "display_name"
        case avatarImageId = "avatar_image_id"
        case avatarUrl = "avatar_url"
        case createdAt = "created_at"
        case updatedAt = "updated_at"
    }
}
