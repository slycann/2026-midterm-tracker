import Foundation
import ImageIO
import UniformTypeIdentifiers
// crop <in> <out> <height>: keep the top <height> pixel rows
let a = CommandLine.arguments
let src = CGImageSourceCreateWithURL(URL(fileURLWithPath: a[1]) as CFURL, nil)!
let img = CGImageSourceCreateImageAtIndex(src, 0, nil)!
let out = img.cropping(to: CGRect(x: 0, y: 0, width: img.width, height: Int(a[3])!))!
let dst = CGImageDestinationCreateWithURL(URL(fileURLWithPath: a[2]) as CFURL, UTType.png.identifier as CFString, 1, nil)!
CGImageDestinationAddImage(dst, out, nil); CGImageDestinationFinalize(dst)
