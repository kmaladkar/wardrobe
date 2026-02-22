import SwiftUI

/// "What to wear today" – suggested outfit (top, bottom, footwear) + virtual try-on result on avatar.
struct TodayView: View {
    @State private var recommendation: TodayRecommendation?
    @State private var tryOnStatus: TryOnResult?
    @State private var loading = false
    @State private var errorMessage: String?

    var body: some View {
        NavigationStack {
            Group {
                if loading {
                    ProgressView("Finding an outfit…")
                } else if let msg = errorMessage {
                    Text(msg)
                        .foregroundStyle(.secondary)
                        .multilineTextAlignment(.center)
                        .padding()
                } else if let rec = recommendation {
                    ScrollView {
                        VStack(alignment: .leading, spacing: 16) {
                            // Try-on result (avatar + garments)
                            if let status = tryOnStatus, status.status == "completed", let imageId = status.result_image_id {
                                VStack(alignment: .leading, spacing: 8) {
                                    Text("Try-on")
                                        .font(.headline)
                                    tryOnImageURL(imageId: imageId)
                                        .frame(height: 320)
                                        .frame(maxWidth: .infinity)
                                        .clipShape(RoundedRectangle(cornerRadius: 12))
                                }
                            } else if let status = tryOnStatus, status.status == "processing" || status.status == "pending" {
                                HStack(spacing: 8) {
                                    ProgressView()
                                    Text("Placing outfit on avatar…")
                                        .font(.subheadline)
                                        .foregroundStyle(.secondary)
                                }
                                .frame(maxWidth: .infinity)
                                .padding()
                            } else if let status = tryOnStatus, status.status == "failed" {
                                Text(status.message)
                                    .font(.subheadline)
                                    .foregroundStyle(.secondary)
                            }

                            // Suggested items
                            Text("Suggested outfit")
                                .font(.headline)
                            LazyVStack(alignment: .leading, spacing: 8) {
                                ForEach(rec.outfit.items) { item in
                                    HStack(spacing: 12) {
                                        itemThumbnail(urlString: item.imageUrl)
                                        Text(item.category.capitalized)
                                            .font(.subheadline)
                                    }
                                }
                            }
                        }
                        .padding()
                    }
                } else {
                    ContentUnavailableView(
                        "No suggestion yet",
                        systemImage: "sparkles",
                        description: Text("Add items (top, bottom, footwear) and set an avatar in Profile. We'll suggest an outfit and show try-on.")
                    )
                }
            }
            .navigationTitle("Today")
            .refreshable { await loadToday() }
            .task { await loadToday() }
        }
    }

    @ViewBuilder
    private func tryOnImageURL(imageId: String) -> some View {
        let urlString = "\(APIClient.shared.baseURL)/images/\(imageId)"
        if let url = URL(string: urlString) {
            AsyncImage(url: url) { phase in
                switch phase {
                case .empty:
                    ProgressView()
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                case .success(let image):
                    image
                        .resizable()
                        .aspectRatio(contentMode: .fit)
                case .failure:
                    Image(systemName: "photo")
                        .font(.largeTitle)
                        .foregroundStyle(.secondary)
                @unknown default:
                    EmptyView()
                }
            }
        } else {
            Image(systemName: "photo")
                .font(.largeTitle)
                .foregroundStyle(.secondary)
        }
    }

    @ViewBuilder
    private func itemThumbnail(urlString: String) -> some View {
        if let url = URL(string: urlString) {
            AsyncImage(url: url) { phase in
                if let image = phase.image {
                    image
                        .resizable()
                        .aspectRatio(contentMode: .fill)
                } else {
                    Rectangle()
                        .fill(Color.gray.opacity(0.2))
                }
            }
            .frame(width: 56, height: 56)
            .clipShape(RoundedRectangle(cornerRadius: 8))
        }
    }

    private func loadToday() async {
        loading = true
        errorMessage = nil
        recommendation = nil
        tryOnStatus = nil
        defer { loading = false }
        do {
            recommendation = try await APIClient.shared.fetchTodayRecommendation()
            if let rec = recommendation {
                await pollTryOn(tryOnId: rec.tryOnId)
            }
        } catch {
            errorMessage = "Could not load recommendation. Is the backend running?"
        }
    }

    private func pollTryOn(tryOnId: String) async {
        for _ in 0 ..< 60 {
            do {
                let result = try await APIClient.shared.getTryOn(tryOnId: tryOnId)
                tryOnStatus = result
                if result.status == "completed" || result.status == "failed" {
                    return
                }
            } catch {
                return
            }
            try? await Task.sleep(nanoseconds: 1_500_000_000)
        }
    }
}

#Preview {
    TodayView()
}
