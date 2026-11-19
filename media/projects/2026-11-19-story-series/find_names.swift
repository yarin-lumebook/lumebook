import Foundation
import Vision
import AppKit
// find_names.swift (19 Nov 2026): text lines of review screenshots with their boxes (image pixels, origin top left), as JSON.
// macOS Vision; reads Latin usernames well, Hebrew not at all, so make_sets.py uses it only to find Instagram usernames.
var out: [[String: Any]] = []
for path in CommandLine.arguments.dropFirst() {
    guard let img = NSImage(contentsOfFile: path), let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { continue }
    let W = Double(cg.width), H = Double(cg.height)
    let req = VNRecognizeTextRequest()
    req.recognitionLevel = .accurate
    req.recognitionLanguages = ["he-IL", "en-US"]
    req.usesLanguageCorrection = false
    try? VNImageRequestHandler(cgImage: cg, options: [:]).perform([req])
    var lines: [[String: Any]] = []
    for o in (req.results ?? []) {
        guard let t = o.topCandidates(1).first else { continue }
        let b = o.boundingBox
        lines.append(["t": t.string, "x": b.minX * W, "y": (1 - b.maxY) * H, "w": b.width * W, "h": b.height * H])
    }
    out.append(["file": path, "w": W, "h": H, "lines": lines])
}
let d = try! JSONSerialization.data(withJSONObject: out, options: [])
print(String(data: d, encoding: .utf8)!)
