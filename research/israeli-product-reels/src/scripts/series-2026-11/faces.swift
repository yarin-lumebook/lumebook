// Face boxes in still frames, with macOS Vision (no download, no cost).
// Yarin, 20 Nov 2026: "never hide the kids faces in the b rolls". reel_make.py uses this to keep pictures and text off faces.
//
//   swift faces.swift frame1.png frame2.png ...
//
// Prints one JSON line per frame: {"file": ..., "faces": [[x0, y0, x1, y1], ...]}, as shares of the width and height with
// the origin at the top left (Vision's own origin is the bottom left).
import Foundation
import Vision
import AppKit

for path in CommandLine.arguments.dropFirst() {
    var boxes: [[Double]] = []
    if let img = NSImage(contentsOfFile: path),
       let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) {
        let req = VNDetectFaceRectanglesRequest()
        let handler = VNImageRequestHandler(cgImage: cg, options: [:])
        try? handler.perform([req])
        for f in req.results ?? [] {
            let b = f.boundingBox
            boxes.append([b.minX, 1 - b.maxY, b.maxX, 1 - b.minY].map { (Double($0) * 1000).rounded() / 1000 })
        }
    }
    let line: [String: Any] = ["file": path, "faces": boxes]
    if let d = try? JSONSerialization.data(withJSONObject: line), let s = String(data: d, encoding: .utf8) {
        print(s)
    }
}
