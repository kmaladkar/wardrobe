import SwiftUI

/// Main tab bar: Closet | Today | Add | Settings (per IDEAS.md).
struct ContentView: View {
    @State private var selectedTab = 0

    var body: some View {
        TabView(selection: $selectedTab) {
            ClosetView()
                .tabItem { Label("Closet", systemImage: "tshirt.fill") }
                .tag(0)
            TodayView()
                .tabItem { Label("Today", systemImage: "sparkles") }
                .tag(1)
            AddItemView()
                .tabItem { Label("Add", systemImage: "camera.fill") }
                .tag(2)
            SettingsView()
                .tabItem { Label("Settings", systemImage: "gearshape.fill") }
                .tag(3)
        }
    }
}

#Preview {
    ContentView()
}
