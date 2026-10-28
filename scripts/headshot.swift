// Crops a portrait to a uniform 240x300 headshot centered on the largest detected face.
import Foundation
import Vision
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

let args = CommandLine.arguments
let outW = 240, outH = 300
let faceShare: CGFloat = Double(args.count > 3 ? args[3] : "0.36").map { CGFloat($0) } ?? 0.36
guard let src = CGImageSourceCreateWithURL(URL(fileURLWithPath: args[1]) as CFURL, nil),
      let props = CGImageSourceCopyPropertiesAtIndex(src, 0, nil) as? [CFString: Any] else { exit(1) }
let maxDim = max(props[kCGImagePropertyPixelWidth] as? Int ?? 4000, props[kCGImagePropertyPixelHeight] as? Int ?? 4000)
let topts: [CFString: Any] = [kCGImageSourceCreateThumbnailFromImageAlways: true, kCGImageSourceCreateThumbnailWithTransform: true,
                              kCGImageSourceThumbnailMaxPixelSize: maxDim]
guard let img = CGImageSourceCreateThumbnailAtIndex(src, 0, topts as CFDictionary) else { exit(1) }
let W = CGFloat(img.width), H = CGFloat(img.height), aspect = CGFloat(outW) / CGFloat(outH)
let req = VNDetectFaceRectanglesRequest()
try? VNImageRequestHandler(cgImage: img, options: [:]).perform([req])
let face = (req.results ?? []).max { $0.boundingBox.width * $0.boundingBox.height < $1.boundingBox.width * $1.boundingBox.height }?.boundingBox
var ch: CGFloat, cw: CGFloat, x: CGFloat, y: CGFloat
if let f = face {
    ch = f.height * H / faceShare; cw = ch * aspect
    if cw > W { cw = W; ch = cw / aspect }
    if ch > H { ch = H; cw = ch * aspect }
    x = f.midX * W - cw / 2; y = (1 - f.midY) * H - ch * 0.40
} else {
    cw = W; ch = cw / aspect
    if ch > H { ch = H; cw = ch * aspect }
    x = (W - cw) / 2; y = 0
}
x = min(max(0, x), W - cw); y = min(max(0, y), H - ch)
guard let cut = img.cropping(to: CGRect(x: x, y: y, width: cw, height: ch).integral),
      let ctx = CGContext(data: nil, width: outW, height: outH, bitsPerComponent: 8, bytesPerRow: 0,
                          space: CGColorSpace(name: CGColorSpace.sRGB)!, bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue) else { exit(2) }
ctx.interpolationQuality = .high
ctx.setFillColor(CGColor(red: 1, green: 1, blue: 1, alpha: 1))
ctx.fill(CGRect(x: 0, y: 0, width: outW, height: outH))
ctx.draw(cut, in: CGRect(x: 0, y: 0, width: outW, height: outH))
guard let out = ctx.makeImage(),
      let dest = CGImageDestinationCreateWithURL(URL(fileURLWithPath: args[2]) as CFURL, UTType.jpeg.identifier as CFString, 1, nil) else { exit(3) }
CGImageDestinationAddImage(dest, out, [kCGImageDestinationLossyCompressionQuality: 0.82] as CFDictionary)
CGImageDestinationFinalize(dest)
print(face == nil ? "NO FACE" : "face", "crop \(Int(cw))x\(Int(ch)) of \(Int(W))x\(Int(H))")
