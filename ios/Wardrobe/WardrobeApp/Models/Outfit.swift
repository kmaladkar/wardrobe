import Foundation

/// Suggested outfit – matches backend (item_ids, occasion, etc.).
struct Outfit: Identifiable, Codable {
    let id: String
    var itemIds: [String]
    var occasion: String?
    var rating: Int?
    var weather: String?

    enum CodingKeys: String, CodingKey {
        case id
        case itemIds = "item_ids"
        case occasion
        case rating
        case weather
    }
}
