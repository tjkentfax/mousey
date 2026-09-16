import CoreMotion
import Foundation

final class MotionManager: ObservableObject {
    private let manager = CMMotionManager()
    private let queue = OperationQueue()
    var onDelta: ((Double, Double) -> Void)?

    func start() {
        guard manager.isDeviceMotionAvailable else { return }
        manager.deviceMotionUpdateInterval = 1.0 / 60.0
        manager.startDeviceMotionUpdates(to: queue) { [weak self] motion, _ in
            guard let motion else { return }
            // Rotation around the phone's axes becomes cursor movement. Inverting Y
            // makes the motion feel natural when holding the phone flat.
            let sensitivity = 28.0
            let dx = motion.rotationRate.z * sensitivity
            let dy = -motion.rotationRate.x * sensitivity
            if abs(dx) > 0.01 || abs(dy) > 0.01 {
                DispatchQueue.main.async {
                    self?.onDelta?(dx, dy)
                }
            }
        }
    }

    func stop() {
        manager.stopDeviceMotionUpdates()
    }
}
