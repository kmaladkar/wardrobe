import SwiftUI

/// "What to wear today" – one-tap daily suggestion (IDEAS: weather, occasion, calendar).
struct TodayView: View {
    @State private var outfit: Outfit?
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
                } else if let o = outfit {
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Suggested outfit")
                            .font(.headline)
                        Text("Items: \(o.itemIds.joined(separator: ", "))")
                            .font(.subheadline)
                        if let occ = o.occasion { Text("Occasion: \(occ)").font(.caption) }
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding()
                } else {
                    ContentUnavailableView(
                        "No suggestion yet",
                        systemImage: "sparkles",
                        description: Text("Add items to your closet and we’ll suggest what to wear today.")
                    )
                }
            }
            .navigationTitle("Today")
            .refreshable { await loadToday() }
            .task { await loadToday() }
        }
    }

    private func loadToday() async {
        loading = true
        errorMessage = nil
        defer { loading = false }
        do {
            outfit = try await APIClient.shared.fetchTodayRecommendation()
        } catch {
            errorMessage = "Could not load recommendation. Is the backend running?"
        }
    }
}

#Preview {
    TodayView()
}
