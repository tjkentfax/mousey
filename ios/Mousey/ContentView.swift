import SwiftUI

struct ContentView: View {
    @StateObject private var motion = MotionManager()
    @State private var server = "http://192.168.1.100:8765"
    @State private var pin = ""
    @State private var connected = false
    @State private var draggingButton: String?
    private let client = NetworkClient()

    var body: some View {
        GeometryReader { geo in
            ZStack {
                Color.black.ignoresSafeArea()

                VStack(spacing: 0) {
                    HStack {
                        Image(systemName: connected ? "wifi" : "wifi.slash")
                        Text(connected ? "Connected" : "Mousey")
                            .font(.headline)
                        Spacer()
                        Button("Settings") { connected = false }
                            .font(.subheadline)
                    }
                    .foregroundStyle(.white)
                    .padding()

                    if !connected {
                        setup
                    } else {
                        mouseSurface(size: geo.size)
                    }
                }
            }
        }
        .preferredColorScheme(.dark)
    }

    private var setup: some View {
        VStack(spacing: 18) {
            Spacer()
            Image(systemName: "computermouse.fill")
                .font(.system(size: 64))
            Text("Connect to your PC")
                .font(.title2.bold())
            Text("Run the Mousey receiver on Linux or Windows. Enter the address and 6-digit PIN it displays.")
                .multilineTextAlignment(.center)
                .foregroundStyle(.secondary)
                .padding(.horizontal)
            TextField("PC address, e.g. 192.168.1.20:8765", text: $server)
                .textInputAutocapitalization(.never)
                .autocorrectionDisabled()
                .textFieldStyle(.roundedBorder)
                .keyboardType(.URL)
            TextField("6-digit PIN", text: $pin)
                .textFieldStyle(.roundedBorder)
                .keyboardType(.numberPad)
            Button {
                client.baseURL = server.hasPrefix("http") ? server : "http://" + server
                client.pin = pin
                connected = true
                motion.onDelta = { dx, dy in client.send(action: "move", dx: dx, dy: dy) }
                motion.start()
                client.send(action: "ping")
            } label: {
                Text("Connect")
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(.white)
                    .foregroundStyle(.black)
                    .clipShape(RoundedRectangle(cornerRadius: 14))
            }
            Spacer()
        }
        .padding(24)
    }

    private func mouseSurface(size: CGSize) -> some View {
        VStack(spacing: 0) {
            HStack(spacing: 1) {
                clickZone(title: "LEFT", button: "left")
                clickZone(title: "RIGHT", button: "right")
            }
            .frame(height: max(160, size.height * 0.48))

            Text("Move phone to move pointer • Swipe with two fingers to scroll")
                .font(.footnote)
                .foregroundStyle(.secondary)
                .frame(maxWidth: .infinity)
                .frame(maxHeight: .infinity)
        }
        .contentShape(Rectangle())
        .simultaneousGesture(
            DragGesture(minimumDistance: 10)
                .onChanged { value in
                    if abs(value.translation.height) > abs(value.translation.width) {
                        client.send(action: "scroll", dy: -value.translation.height / 80)
                    }
                }
        )
    }

    private func clickZone(title: String, button: String) -> some View {
        RoundedRectangle(cornerRadius: 18)
            .fill(Color.white.opacity(0.08))
            .overlay(Text(title).font(.caption.bold()).foregroundStyle(.secondary))
            .padding(4)
            .contentShape(Rectangle())
            .onLongPressGesture(minimumDuration: 0.25, maximumDistance: 30, pressing: { pressing in
                if pressing {
                    draggingButton = button
                    client.send(action: "down", button: button)
                } else if draggingButton == button {
                    draggingButton = nil
                    client.send(action: "up", button: button)
                }
            }, perform: {})
            .simultaneousGesture(
                TapGesture().onEnded {
                    guard draggingButton == nil else { return }
                    client.send(action: "click", button: button)
                }
            )
    }
}
