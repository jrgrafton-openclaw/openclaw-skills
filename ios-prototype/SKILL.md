# ios-prototype

A zero-friction SwiftUI design playground and prototyping skill.

Before prototyping, **always read and apply the `apple-hig` skill** to ensure the design follows Apple Human Interface Guidelines and best practices.

### Commands

* **`prototype new`**: Wipes `ContentView.swift` and regenerates a fresh structure.
* **`prototype snap`**: Builds the app, boots the simulator, takes a screenshot, and posts it to the chat.
* **`prototype ship`**: Uses Fastlane to push the UI build straight to TestFlight to distribute it.
* **`prototype merge`**: Extracts `ContentView.swift` and applies it to the active app project (e.g. SingCoach).

### Rationale
Use this skill instead of trying to generate HTML/CSS to rapidly iterate natively. Always reference `apple-hig` for native UI/UX patterns.
