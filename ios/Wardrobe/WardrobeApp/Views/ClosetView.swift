import SwiftUI

/// Virtual closet – browse and filter wardrobe items (IDEAS: "all blue tops", "formal shoes").
struct ClosetView: View {
    @State private var items: [Item] = []
    @State private var loading = false
    @State private var errorMessage: String?

    var body: some View {
        NavigationStack {
            Group {
                if loading {
                    ProgressView("Loading closet…")
                } else if let msg = errorMessage {
                    Text(msg)
                        .foregroundStyle(.secondary)
                        .padding()
                } else if items.isEmpty {
                    ContentUnavailableView(
                        "No items yet",
                        systemImage: "tshirt",
                        description: Text("Add clothes with the Add tab to build your closet.")
                    )
                } else {
                    ScrollView {
                        LazyVStack(spacing: 0) {
                            ForEach(items) { item in
                                HStack(spacing: 12) {
                                    ItemThumbnail(imageUrl: item.imageUrl)
                                    VStack(alignment: .leading) {
                                        Text(item.category).font(.headline)
                                        if let sub = item.subcategory, !sub.isEmpty { Text(sub).font(.caption) }
                                    }
                                    Spacer(minLength: 0)
                                }
                                .padding(.horizontal)
                                .padding(.vertical, 10)
                                .background(Color(.secondarySystemGroupedBackground))
                                .padding(.horizontal)
                                .padding(.vertical, 4)
                            }
                        }
                        .padding(.vertical, 8)
                    }
                    .scrollIndicators(.visible)
                    .refreshable { await loadItems() }
                }
            }
            .navigationTitle("Closet")
            .task { await loadItems() }
        }
    }

    private func loadItems() async {
        loading = true
        errorMessage = nil
        defer { loading = false }
        do {
            items = try await APIClient.shared.fetchItems()
        } catch {
            errorMessage = "Could not load items. Is the backend running?"
        }
    }
}

// MARK: - Thumbnail

private struct ItemThumbnail: View {
    let imageUrl: String
    private let size: CGFloat = 56

    var body: some View {
        AsyncImage(url: URL(string: imageUrl)) { phase in
            switch phase {
            case .empty:
                placeholder
            case .success(let image):
                image
                    .resizable()
                    .aspectRatio(contentMode: .fill)
            case .failure:
                placeholder
            @unknown default:
                placeholder
            }
        }
        .frame(width: size, height: size)
        .clipShape(RoundedRectangle(cornerRadius: 8))
    }

    private var placeholder: some View {
        RoundedRectangle(cornerRadius: 8)
            .fill(.gray.opacity(0.2))
            .overlay(Image(systemName: "tshirt").foregroundStyle(.gray))
    }
}

#Preview {
    ClosetView()
}
