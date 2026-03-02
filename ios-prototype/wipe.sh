#!/usr/bin/env bash
# ios-prototype: wipe
cat << 'EOF' > ~/.openclaw/workspace/projects/SwiftDesignPlayground/Sources/ContentView.swift
import SwiftUI

struct ContentView: View {
    var body: some View {
        Text("Wiped. Ready for fresh design.")
    }
}

#Preview {
    ContentView()
}
EOF
echo "Wiped ContentView.swift."