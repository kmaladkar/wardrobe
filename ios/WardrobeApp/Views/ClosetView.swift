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
                    List(items) { item in
                        HStack {
                            placeholderImage
                            VStack(alignment: .leading) {
                                Text(item.category).font(.headline)
                                if let sub = item.subcategory, !sub.isEmpty { Text(sub).font(.caption) }
                            }
                        }
                    }
                }
            }
            .navigationTitle("Closet")
            .refreshable { await loadItems() }
            .task { await loadItems() }
        }
    }

    private var placeholderImage: some View {
        RoundedRectangle(cornerRadius: 8)
            .fill(.gray.opacity(0.2))
            .frame(width: 56, height: 56)
            .overlay(Image(systemName: "tshirt").foregroundStyle(.gray))
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

#Preview {
    ClosetView()
}
