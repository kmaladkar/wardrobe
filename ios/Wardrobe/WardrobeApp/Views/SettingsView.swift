import SwiftUI

/// Profile, API URL, logout (IDEAS: style profile, preferences).
struct SettingsView: View {
    @AppStorage("apiBaseURL") private var baseURL = "http://localhost:8000"

    var body: some View {
        NavigationStack {
            Form {
                Section("Backend") {
                    TextField("API base URL", text: $baseURL)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                    Text("Use your Mac’s IP (e.g. http://192.168.1.5:8000) when running on a real device.")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
                Section {
                    Button("Save URL") {
                        APIClient.shared.baseURL = baseURL
                    }
                }
                Section("Account") {
                    Text("Login / profile will go here once auth is implemented.")
                        .foregroundStyle(.secondary)
                }
            }
            .navigationTitle("Settings")
        }
        .onAppear { baseURL = APIClient.shared.baseURL }
    }
}

#Preview {
    SettingsView()
}
