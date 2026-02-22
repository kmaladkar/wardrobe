import SwiftUI

/// Main tab bar: Profile | Closet | Today | Add | Settings.
struct ContentView: View {
    @State private var selectedTab = 0

    var body: some View {
        TabView(selection: $selectedTab) {
            ProfileView()
                .tabItem { Label("Profile", systemImage: "person.circle.fill") }
                .tag(0)
            ClosetView()
                .tabItem { Label("Closet", systemImage: "tshirt.fill") }
                .tag(1)
            TodayView()
                .tabItem { Label("Today", systemImage: "sparkles") }
                .tag(2)
            AddItemView()
                .tabItem { Label("Add", systemImage: "camera.fill") }
                .tag(3)
            SettingsView()
                .tabItem { Label("Settings", systemImage: "gearshape.fill") }
                .tag(4)
        }
    }
}

#Preview {
    ContentView()
}
