import SwiftUI

/// Virtual closet – browse by collection: Top, Bottom, Jacket, Footwear.
struct ClosetView: View {
    @AppStorage("userId") private var userId: String = ""
    @State private var items: [WardrobeItem] = []
    @State private var selectedCategory: String? = nil
    @State private var loading = false
    @State private var errorMessage: String?

    private var categoryTitle: String {
        selectedCategory?.capitalized ?? "All"
    }

    var body: some View {
        NavigationStack {
            Group {
                if !userId.isEmpty {
                    VStack(spacing: 0) {
                        Picker("Collection", selection: $selectedCategory) {
                            Text("All").tag(nil as String?)
                            ForEach(WardrobeItem.categories, id: \.self) { c in
                                Text(c.capitalized).tag(c as String?)
                            }
                        }
                        .pickerStyle(.segmented)
                        .padding()
                        if loading {
                            Spacer()
                            ProgressView("Loading…")
                        } else if let msg = errorMessage {
                            Spacer()
                            Text(msg).foregroundStyle(.secondary).padding()
                        } else if items.isEmpty {
                            Spacer()
                            ContentUnavailableView(
                                "No items yet",
                                systemImage: "tshirt",
                                description: Text("Add clothes with the Add tab.")
                            )
                        } else {
                            ScrollView {
                                LazyVStack(spacing: 0) {
                                    ForEach(items) { item in
                                        HStack(spacing: 12) {
                                            ItemThumbnail(imageUrl: item.imageUrl)
                                            VStack(alignment: .leading) {
                                                Text(item.category.capitalized).font(.headline)
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
                } else {
                    ContentUnavailableView(
                        "Sign in to view closet",
                        systemImage: "person.crop.circle.badge.plus",
                        description: Text("Create a profile in the Profile tab.")
                    )
                }
            }
            .navigationTitle("Closet")
            .task { await loadItems() }
            .onChange(of: selectedCategory) { _, _ in Task { await loadItems() } }
        }
    }

    private func loadItems() async {
        guard !userId.isEmpty else { items = []; return }
        loading = true
        errorMessage = nil
        defer { loading = false }
        do {
            items = try await APIClient.shared.fetchWardrobeItems(category: selectedCategory)
        } catch {
            errorMessage = "Could not load wardrobe."
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
