import SwiftUI
import PhotosUI

/// User profile: avatar, display name, login/register. Upload avatar to backend.
struct ProfileView: View {
    @AppStorage("userId") private var userId: String = ""
    @State private var user: User?
    @State private var loading = false
    @State private var errorMessage: String?
    @State private var displayName: String = ""
    @State private var selectedPhoto: PhotosPickerItem?
    @State private var showLogin = false
    @State private var loginEmail = ""

    var body: some View {
        NavigationStack {
            Group {
                if loading {
                    ProgressView()
                } else if let u = user {
                    Form {
                        Section("Profile") {
                            HStack {
                                avatarView(u)
                                VStack(alignment: .leading) {
                                    TextField("Display name", text: $displayName)
                                        .textContentType(.name)
                                    Text(u.email).font(.caption).foregroundStyle(.secondary)
                                }
                            }
                            Button("Save name") {
                                Task { await saveName() }
                            }
                        }
                        Section("Avatar") {
                            PhotosPicker(selection: $selectedPhoto, matching: .images) {
                                Label("Change avatar", systemImage: "person.crop.circle.badge.plus")
                            }
                            .onChange(of: selectedPhoto) { _, new in
                                guard let new else { return }
                                Task { await uploadAvatar(from: new) }
                            }
                        }
                        if let msg = errorMessage {
                            Section { Text(msg).foregroundStyle(.red) }
                        }
                    }
                } else {
                    VStack(spacing: 16) {
                        Text("Create a profile to use your wardrobe and try-on.")
                            .foregroundStyle(.secondary)
                            .multilineTextAlignment(.center)
                            .padding()
                        TextField("Email", text: $loginEmail)
                            .textContentType(.emailAddress)
                            .textInputAutocapitalization(.never)
                            .autocorrectionDisabled()
                            .padding(.horizontal, 32)
                        HStack {
                            Button("Register") { Task { await register() } }
                            Button("Login") { Task { await login() } }
                        }
                        .disabled(loginEmail.isEmpty)
                        if let msg = errorMessage {
                            Text(msg).foregroundStyle(.red).font(.caption)
                        }
                    }
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                }
            }
            .navigationTitle("Profile")
            .task {
                if !userId.isEmpty {
                    APIClient.shared.currentUserId = userId
                    await loadUser()
                }
            }
            .onChange(of: userId) { _, new in
                if !new.isEmpty { APIClient.shared.currentUserId = new }
            }
        }
    }

    @ViewBuilder
    private func avatarView(_ u: User) -> some View {
        if let urlString = u.avatarUrl, let url = URL(string: urlString) {
            AsyncImage(url: url) { phase in
                switch phase {
                case .success(let img): img.resizable().scaledToFill()
                default: placeholderAvatar
                }
            }
            .frame(width: 72, height: 72)
            .clipShape(Circle())
        } else {
            placeholderAvatar
        }
    }

    private var placeholderAvatar: some View {
        Circle()
            .fill(.gray.opacity(0.2))
            .frame(width: 72, height: 72)
            .overlay(Image(systemName: "person.fill").foregroundStyle(.gray))
    }

    private func loadUser() async {
        loading = true
        errorMessage = nil
        defer { loading = false }
        do {
            user = try await APIClient.shared.getMe()
            displayName = user?.displayName ?? ""
        } catch {
            errorMessage = "Could not load profile."
            user = nil
        }
    }

    private func register() async {
        guard !loginEmail.isEmpty else { return }
        loading = true
        errorMessage = nil
        defer { loading = false }
        do {
            let u = try await APIClient.shared.register(email: loginEmail, displayName: nil)
            APIClient.shared.currentUserId = u.id
            userId = u.id
            user = u
        } catch {
            errorMessage = "Register failed."
        }
    }

    private func login() async {
        guard !loginEmail.isEmpty else { return }
        loading = true
        errorMessage = nil
        defer { loading = false }
        do {
            let u = try await APIClient.shared.login(email: loginEmail)
            APIClient.shared.currentUserId = u.id
            userId = u.id
            user = u
        } catch {
            errorMessage = "Login failed."
        }
    }

    private func saveName() async {
        loading = true
        errorMessage = nil
        defer { loading = false }
        do {
            user = try await APIClient.shared.updateProfile(displayName: displayName.isEmpty ? nil : displayName)
        } catch {
            errorMessage = "Save failed."
        }
    }

    private func uploadAvatar(from item: PhotosPickerItem) async {
        guard let data = try? await item.loadTransferable(type: Data.self) else { return }
        loading = true
        errorMessage = nil
        defer { loading = false }
        do {
            user = try await APIClient.shared.uploadAvatar(imageData: data)
            selectedPhoto = nil
        } catch {
            errorMessage = "Avatar upload failed."
        }
    }
}

#Preview {
    ProfileView()
}
