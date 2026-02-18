import Foundation

/// Wardrobe item – matches backend items schema (image_url, category, etc.).
struct Item: Identifiable, Codable {
    let id: String
    var imageUrl: String
    var category: String
    var subcategory: String?
    var colors: String?
    var formality: String?
    var season: String?
    var createdAt: String?
    var updatedAt: String?

    enum CodingKeys: String, CodingKey {
        case id
        case imageUrl = "image_url"
        case category
        case subcategory
        case colors
        case formality
        case season
        case createdAt = "created_at"
        case updatedAt = "updated_at"
    }
}
