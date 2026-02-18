import SwiftUI
import PhotosUI

/// Camera-first add item (IDEAS: quick photo capture and crop for adding items).
struct AddItemView: View {
    @State private var selectedItem: PhotosPickerItem?
    @State private var category = "top"
    @State private var uploading = false
    @State private var message: String?

    var body: some View {
        NavigationStack {
            Form {
                Section("Photo") {
                    PhotosPicker(selection: $selectedItem, matching: .images) {
                        if selectedItem != nil {
                            Label("Photo selected", systemImage: "checkmark.circle.fill")
                        } else {
                            Label("Choose from library", systemImage: "photo.on.rectangle.angled")
                        }
                    }
                    Text("Or use the camera in a full implementation.")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
                Section("Category") {
                    Picker("Category", selection: $category) {
                        Text("Top").tag("top")
                        Text("Bottom").tag("bottom")
                        Text("Shoes").tag("shoes")
                        Text("Accessory").tag("accessory")
                    }
                }
                if let msg = message {
                    Section { Text(msg).foregroundStyle(.secondary) }
                }
                Section {
                    Button("Upload") {
                        Task { await upload() }
                    }
                    .disabled(selectedItem == nil || uploading)
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
            _ = try await APIClient.shared.uploadItem(
                imageData: imageData,
                filename: "photo.jpg",
                category: category
            )
            message = "Uploaded."
            selectedItem = nil
        } catch {
            message = "Upload failed. Is the backend running?"
        }
    }
}

#Preview {
    AddItemView()
}
