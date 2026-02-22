import SwiftUI
import PhotosUI

/// Add item to wardrobe collection: Top, Bottom, Jacket, Footwear.
struct AddItemView: View {
    @AppStorage("userId") private var userId: String = ""
    @State private var selectedItem: PhotosPickerItem?
    @State private var category = "top"
    @State private var uploading = false
    @State private var message: String?

    private let categories = WardrobeItem.categories

    var body: some View {
        NavigationStack {
            Group {
                if !userId.isEmpty {
                    Form {
                        Section("Photo") {
                            PhotosPicker(selection: $selectedItem, matching: .images) {
                                if selectedItem != nil {
                                    Label("Photo selected", systemImage: "checkmark.circle.fill")
                                } else {
                                    Label("Choose from library", systemImage: "photo.on.rectangle.angled")
                                }
                            }
                        }
                        Section("Collection") {
                            Picker("Category", selection: $category) {
                                ForEach(categories, id: \.self) { c in
                                    Text(c.capitalized).tag(c)
                                }
                            }
                            .pickerStyle(.menu)
                        }
                        if let msg = message {
                            Section { Text(msg).foregroundStyle(.secondary) }
                        }
                        Section {
                            Button("Upload to wardrobe") {
                                Task { await upload() }
                            }
                            .disabled(selectedItem == nil || uploading)
                        }
                    }
                } else {
                    ContentUnavailableView(
                        "Sign in to add items",
                        systemImage: "person.crop.circle.badge.plus",
                        description: Text("Create a profile in the Profile tab.")
                    )
                }
            }
            .navigationTitle("Add item")
            .onChange(of: selectedItem) { _, _ in message = nil }
        }
    }

    private func upload() async {
        guard let picker = selectedItem else { return }
        uploading = true
        message = nil
        defer { uploading = false }
        do {
            let data = try await picker.loadTransferable(type: Data.self)
            guard let imageData = data else {
                message = "Could not load image."
                return
            }
            _ = try await APIClient.shared.uploadWardrobeItem(imageData: imageData, category: category)
            message = "Added to \(category)."
            selectedItem = nil
        } catch {
            message = "Upload failed."
        }
    }
}

#Preview {
    AddItemView()
}
