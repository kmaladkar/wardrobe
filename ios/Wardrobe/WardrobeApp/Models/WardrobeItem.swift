import Foundation

/// Wardrobe collection item – top, bottom, jacket, footwear.
struct WardrobeItem: Identifiable, Codable {
    let id: String
    let userId: String
    let imageId: String
    let imageUrl: String
    let category: String
    let createdAt: String?

    enum CodingKeys: String, CodingKey {
        case id
        case userId = "user_id"
        case imageId = "image_id"
        case imageUrl = "image_url"
        case category
        case createdAt = "created_at"
    }

    static let categories = ["top", "bottom", "jacket", "footwear"]
}
