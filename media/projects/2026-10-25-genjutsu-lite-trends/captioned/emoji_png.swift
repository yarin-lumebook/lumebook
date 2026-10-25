// Renders one emoji sequence (skin tones included) with macOS Apple Color Emoji to a transparent PNG.
// Usage: swift emoji_png.swift "👇🏻" out.png [pointSize]
import AppKit
let args = CommandLine.arguments
let text = args[1], out = args[2]
let size = CGFloat(Double(args.count > 3 ? args[3] : "160") ?? 160)
let font = NSFont(name: "AppleColorEmoji", size: size)!
let s = NSAttributedString(string: text, attributes: [.font: font])
let b = s.boundingRect(with: NSSize(width: 4000, height: 4000), options: [.usesLineFragmentOrigin])
let w = Int(ceil(b.width)) + 20, h = Int(ceil(b.height)) + 20
let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: w, pixelsHigh: h, bitsPerSample: 8, samplesPerPixel: 4,
                           hasAlpha: true, isPlanar: false, colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
NSGraphicsContext.saveGraphicsState()
NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: rep)
s.draw(at: NSPoint(x: 10, y: 10))
NSGraphicsContext.restoreGraphicsState()
try! rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: out))
